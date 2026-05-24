from datetime import datetime, timezone
from typing import Any, TypedDict

from typing_extensions import NotRequired


class EventDict(TypedDict):
    agent: str
    action: str
    detail: str | None
    timestamp: str
    metadata: dict[str, Any]


def make_event(
    agent: str, action: str, detail: str | None = None, metadata: dict[str, Any] | None = None
) -> EventDict:
    return EventDict(
        agent=agent,
        action=action,
        detail=detail,
        timestamp=datetime.now(timezone.utc).isoformat(),
        metadata=metadata or {},
    )
