from newsagent.core.events import make_event


def test_make_event_required_fields() -> None:
    event = make_event("TestAgent", "test_action")
    assert event["agent"] == "TestAgent"
    assert event["action"] == "test_action"
    assert event["detail"] is None
    assert "timestamp" in event
    assert event["metadata"] == {}


def test_make_event_all_fields() -> None:
    event = make_event("TestAgent", "test_action", detail="something happened", metadata={"key": "value"})
    assert event["agent"] == "TestAgent"
    assert event["action"] == "test_action"
    assert event["detail"] == "something happened"
    assert event["metadata"] == {"key": "value"}


def test_make_event_timestamp_format() -> None:
    event = make_event("Agent", "action")
    assert "T" in event["timestamp"]
    assert event["timestamp"].endswith("+00:00") or event["timestamp"].endswith("Z")
