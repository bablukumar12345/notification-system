"""Every channel service returns a SendResult."""
from dataclasses import dataclass, field
from typing import Any, Dict


@dataclass
class SendResult:
    ok: bool
    recipient: str = ""
    detail: str = ""
    raw: Dict[str, Any] = field(default_factory=dict)

    def as_dict(self):
        return {"ok": self.ok, "recipient": self.recipient, "detail": self.detail}
