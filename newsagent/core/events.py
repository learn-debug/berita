from datetime import datetime, timezone
from typing import Any


def make_event(
    agent: str, action: str, detail: str | None = None, metadata: dict[str, Any] | None = None
) -> dict:
    return {
        "agent": agent,
        "action": action,
        "detail": detail,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "metadata": metadata or {},
    }
