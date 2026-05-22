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
        raw_input = raw.get("raw_input", "")
        if not isinstance(raw_input, str) or not raw_input.strip():
            raise ValueError("raw_input must be a non-empty string")
        raw["raw_input"] = cls.sanitize(raw_input)
        return raw
