"""Inactive user triggers: not_logged_in_1_day / not_logged_in_1_week."""
import logging
from datetime import timedelta

from django.contrib.auth.models import User
from django.utils import timezone

from .dispatcher import fire_trigger

logger = logging.getLogger(__name__)

RULES = [
    # (trigger_code, days of inactivity, profile field that marks it as sent)
    ("not_logged_in_1_day", 1, "inactive_1_day_sent_at"),
    ("not_logged_in_1_week", 7, "inactive_1_week_sent_at"),
]


def run_inactivity_check():
    """Checks every user's last_seen_at and sends the notification when due.
    The sent_at field prevents the same user being notified repeatedly."""
    now = timezone.now()
    summary = {"checked": 0, "sent": []}

    for user in User.objects.select_related("profile").filter(is_active=True):
        profile = getattr(user, "profile", None)
        if profile is None or profile.last_seen_at is None:
            continue
        summary["checked"] += 1
        idle = now - profile.last_seen_at

        for code, days, field in RULES:
            already = getattr(profile, field)
            if idle >= timedelta(days=days) and (already is None or already < profile.last_seen_at):
                results = fire_trigger(code, user=user)
                setattr(profile, field, now)
                profile.save(update_fields=[field])
                summary["sent"].append(
                    {"user": user.username, "trigger": code, "results": results}
                )

    return summary
