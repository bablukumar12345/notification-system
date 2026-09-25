"""Send messages through the WhatsApp Cloud API (Meta sandbox)."""
import logging

import requests
from django.conf import settings

from .base import SendResult

logger = logging.getLogger(__name__)
TIMEOUT = 20


def send_whatsapp(to_phone: str, body: str, template_name: str = "", language: str = "en_US"):
    """to_phone must include the country code without a plus, e.g. 919876543210."""
    to_phone = (to_phone or "").strip().replace("+", "").replace(" ", "")
    if not to_phone:
        return SendResult(False, detail="No phone number saved for this user.")

    token = settings.WHATSAPP_ACCESS_TOKEN
    phone_id = settings.PHONE_NUMBER_ID
    if not token or not phone_id:
        return SendResult(
            False,
            recipient=to_phone,
            detail="WHATSAPP_ACCESS_TOKEN or PHONE_NUMBER_ID is missing from .env.",
        )

    url = f"https://graph.facebook.com/{settings.WHATSAPP_API_VERSION}/{phone_id}/messages"

    if template_name:
        payload = {
            "messaging_product": "whatsapp",
            "to": to_phone,
            "type": "template",
            "template": {
                "name": template_name,
                "language": {"code": language or "en_US"},
            },
        }
    else:
        payload = {
            "messaging_product": "whatsapp",
            "to": to_phone,
            "type": "text",
            "text": {"preview_url": False, "body": body},
        }

    try:
        resp = requests.post(
            url,
            json=payload,
            headers={"Authorization": f"Bearer {token}"},
            timeout=TIMEOUT,
        )
        data = resp.json() if resp.content else {}
        if resp.status_code < 300:
            return SendResult(True, to_phone, "WhatsApp message sent.", data)
        detail = data.get("error", {}).get("message", resp.text[:300])
        return SendResult(False, to_phone, f"WhatsApp error: {detail}", data)
    except requests.RequestException as exc:
        logger.exception("WhatsApp send failed")
        return SendResult(False, to_phone, f"Network error: {exc}")
