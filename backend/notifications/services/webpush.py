"""OneSignal Web Push (browser only)."""
import logging

import requests
from django.conf import settings

from .base import SendResult

logger = logging.getLogger(__name__)
ONESIGNAL_URL = "https://onesignal.com/api/v1/notifications"
TIMEOUT = 20


def send_webpush(player_ids, title: str, body: str, url: str = ""):
    player_ids = [p for p in (player_ids or []) if p]
    if not player_ids:
        return SendResult(False, detail="This user has not subscribed in a browser yet.")

    app_id = settings.ONESIGNAL_APP_ID
    api_key = settings.ONESIGNAL_REST_API_KEY
    if not app_id or not api_key:
        return SendResult(
            False, detail="ONESIGNAL_APP_ID or ONESIGNAL_REST_API_KEY is missing from .env."
        )

    payload = {
        "app_id": app_id,
        "include_player_ids": player_ids,
        "headings": {"en": title or "Notification"},
        "contents": {"en": body or ""},
        "isAnyWeb": True,
    }
    if url:
        payload["url"] = url

    try:
        resp = requests.post(
            ONESIGNAL_URL,
            json=payload,
            headers={
                "Authorization": f"Basic {api_key}",
                "Content-Type": "application/json",
            },
            timeout=TIMEOUT,
        )
        data = resp.json() if resp.content else {}
        recipient = ", ".join(p[:8] for p in player_ids)
        if resp.status_code < 300 and not data.get("errors"):
            return SendResult(True, recipient, "Web push sent.", data)
        return SendResult(False, recipient, f"OneSignal error: {data.get('errors', resp.text[:200])}", data)
    except requests.RequestException as exc:
        logger.exception("Web push failed")
        return SendResult(False, detail=f"Network error: {exc}")
