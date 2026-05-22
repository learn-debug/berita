import re
from typing import Any


class InputSanitizer:
    BLOCKED_PATTERNS: list[re.Pattern[str]] = [
        re.compile(r"<script[^>]*>.*?</script>", re.IGNORECASE | re.DOTALL),
        re.compile(r"javascript:", re.IGNORECASE),
        re.compile(r"on\w+\s*=", re.IGNORECASE),
    ]

    @classmethod
    def sanitize(cls, text: str) -> str:
        for pattern in cls.BLOCKED_PATTERNS:
            text = pattern.sub("", text)
        return text.strip()

    @classmethod
    def validate_input_type(cls, raw: dict[str, Any]) -> dict[str, Any]:
        allowed = {"topic", "draft", "url"}
        if raw.get("input_type") not in allowed:
            raw["input_type"] = "topic"
        if not isinstance(raw.get("raw_input", ""), str) or len(raw["raw_input"]) == 0:
            raise ValueError("raw_input must be a non-empty string")
        raw["raw_input"] = cls.sanitize(raw["raw_input"])
        return raw
