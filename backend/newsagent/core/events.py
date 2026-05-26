from datetime import UTC, datetime
from typing import Any, TypedDict


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
        timestamp=datetime.now(UTC).isoformat(),
        metadata=metadata or {},
    )
