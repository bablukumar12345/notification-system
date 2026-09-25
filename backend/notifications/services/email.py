"""Sends email. The provider is chosen with EMAIL_PROVIDER in .env.

Supported: postmark | brevo | resend | console
All of them follow the same pattern: a verified sender plus an API token in .env.
"""
import logging

import requests
from django.conf import settings

from .base import SendResult

logger = logging.getLogger(__name__)
TIMEOUT = 20


def _html(body: str) -> str:
    safe = (body or "").replace("\n", "<br>")
    return (
        '<div style="font-family:Inter,Segoe UI,Arial,sans-serif;font-size:15px;'
        f'line-height:1.6;color:#16212B">{safe}</div>'
    )


def send_email(to_email: str, subject: str, body: str) -> SendResult:
    to_email = (to_email or "").strip()
    if not to_email:
        return SendResult(False, detail="No email address saved for this user.")

    provider = (settings.EMAIL_PROVIDER or "console").lower()
    sender = settings.POSTMARK_FROM_EMAIL

    try:
        if provider == "postmark":
            if not settings.POSTMARKAPP_TOKEN or not sender:
                return SendResult(False, to_email, "POSTMARKAPP_TOKEN or the sender email is missing.")
            resp = requests.post(
                "https://api.postmarkapp.com/email",
                json={
                    "From": sender,
                    "To": to_email,
                    "Subject": subject or "(no subject)",
                    "TextBody": body,
                    "HtmlBody": _html(body),
                    "MessageStream": "outbound",
                },
                headers={
                    "Accept": "application/json",
                    "Content-Type": "application/json",
                    "X-Postmark-Server-Token": settings.POSTMARKAPP_TOKEN,
                },
                timeout=TIMEOUT,
            )

        elif provider == "brevo":
            if not settings.BREVO_API_KEY or not sender:
                return SendResult(False, to_email, "BREVO_API_KEY or the sender email is missing.")
            resp = requests.post(
                "https://api.brevo.com/v3/smtp/email",
                json={
                    "sender": {"email": sender, "name": settings.EMAIL_FROM_NAME},
                    "to": [{"email": to_email}],
                    "subject": subject or "(no subject)",
                    "textContent": body,
                    "htmlContent": _html(body),
                },
                headers={"api-key": settings.BREVO_API_KEY, "Content-Type": "application/json"},
                timeout=TIMEOUT,
            )

        elif provider == "resend":
            if not settings.RESEND_API_KEY or not sender:
                return SendResult(False, to_email, "RESEND_API_KEY or the sender email is missing.")
            resp = requests.post(
                "https://api.resend.com/emails",
                json={
                    "from": f"{settings.EMAIL_FROM_NAME} <{sender}>",
                    "to": [to_email],
                    "subject": subject or "(no subject)",
                    "text": body,
                    "html": _html(body),
                },
                headers={"Authorization": f"Bearer {settings.RESEND_API_KEY}"},
                timeout=TIMEOUT,
            )

        else:  # console - local testing, printed in the terminal
            logger.info("[CONSOLE EMAIL] to=%s subject=%s body=%s", to_email, subject, body)
            return SendResult(True, to_email, "Console provider: email printed in the server terminal.")

    except requests.RequestException as exc:
        logger.exception("Email send failed")
        return SendResult(False, to_email, f"Network error: {exc}")

    data = {}
    try:
        data = resp.json()
    except ValueError:
        pass

    if resp.status_code < 300:
        return SendResult(True, to_email, f"Email sent via {provider}.", data)
    detail = data.get("Message") or data.get("message") or resp.text[:300]
    return SendResult(False, to_email, f"{provider} error: {detail}", data)
