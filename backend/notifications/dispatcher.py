"""The core of the notification system.

Calling fire_trigger("login", user) will:
 1. load every template that belongs to that trigger
 2. render the ones whose toggle is on (filling placeholders like {{name}})
 3. send them on WhatsApp / Email / Web Push
 4. write a NotificationLog row for every attempt
"""
import logging
import re

from .models import Channel, NotificationLog, PushSubscription, Template, Trigger
from .services.email import send_email
from .services.webpush import send_webpush
from .services.whatsapp import send_whatsapp

logger = logging.getLogger(__name__)

PLACEHOLDER = re.compile(r"{{\s*([\w.]+)\s*}}")


def build_context(user=None, extra=None):
    """The {{variables}} that can be used inside a template."""
    context = {
        "name": "there",
        "username": "",
        "email": "",
        "phone": "",
        "site": "Notification System",
    }
    if user is not None:
        context.update(
            {
                "name": user.first_name or user.username,
                "username": user.username,
                "email": user.email or "",
                "phone": getattr(getattr(user, "profile", None), "phone", "") or "",
            }
        )
    if extra:
        context.update({k: str(v) for k, v in extra.items()})
    return context


def render_text(text: str, context: dict) -> str:
    """Replaces {{name}} with its context value. Unknown keys become empty text."""
    if not text:
        return ""

    def repl(match):
        key = match.group(1)
        return str(context.get(key, ""))

    return PLACEHOLDER.sub(repl, text)


def _log(trigger_code, channel, user, result, subject, body, is_test=False, status=None):
    NotificationLog.objects.create(
        trigger_code=trigger_code,
        channel=channel,
        user=user if getattr(user, "pk", None) else None,
        recipient=result.recipient if result else "",
        rendered_subject=subject[:250],
        rendered_body=body,
        status=status or (NotificationLog.Status.SENT if result and result.ok else NotificationLog.Status.FAILED),
        is_test=is_test,
        provider_response=(result.detail if result else "")[:1000],
    )


def send_on_channel(template: Template, user=None, context=None, is_test=False, overrides=None):
    """Sends one template to one user. `overrides` lets a test send target a
    specific phone, email or subscription id."""
    context = context or build_context(user)
    overrides = overrides or {}

    subject = render_text(template.subject, context)
    title = render_text(template.title, context)
    body = render_text(template.body, context)

    if template.channel == Channel.WHATSAPP:
        phone = overrides.get("phone") or context.get("phone")
        result = send_whatsapp(
            phone,
            body,
            template_name=template.whatsapp_template_name,
            language=template.whatsapp_language,
        )
        _log(template.trigger.code, template.channel, user, result, "", body, is_test)

    elif template.channel == Channel.EMAIL:
        to_email = overrides.get("email") or context.get("email")
        result = send_email(to_email, subject, body)
        _log(template.trigger.code, template.channel, user, result, subject, body, is_test)

    elif template.channel == Channel.WEBPUSH:
        player_ids = overrides.get("player_ids")
        if player_ids is None:
            qs = PushSubscription.objects.all()
            if user is not None and getattr(user, "pk", None):
                qs = qs.filter(user=user)
            player_ids = list(qs.values_list("player_id", flat=True))
        result = send_webpush(player_ids, title or subject or "Notification", body)
        _log(template.trigger.code, template.channel, user, result, title, body, is_test)

    else:
        from .services.base import SendResult

        result = SendResult(False, detail=f"Unknown channel: {template.channel}")

    return result


def fire_trigger(trigger_code: str, user=None, extra=None):
    """Called when an event happens on the site. Returns a list of results."""
    results = []
    try:
        trigger = Trigger.objects.get(code=trigger_code)
    except Trigger.DoesNotExist:
        logger.warning("Trigger '%s' does not exist, skipping.", trigger_code)
        return results

    if not trigger.is_active:
        return [{"channel": "-", "ok": False, "detail": "This trigger is turned off."}]

    context = build_context(user, extra)

    for template in trigger.templates.select_related("trigger").all():
        if not template.is_enabled:
            results.append(
                {"channel": template.channel, "ok": False, "detail": "Channel toggle is off."}
            )
            continue
        result = send_on_channel(template, user=user, context=context)
        results.append({"channel": template.channel, **result.as_dict()})

    if not results:
        results.append(
            {"channel": "-", "ok": False, "detail": "No template has been created for this trigger."}
        )
    return results
