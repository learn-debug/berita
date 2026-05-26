import logging
import re
from typing import Any

import bleach

logger = logging.getLogger(__name__)


class InputSanitizer:
    @classmethod
    def sanitize(cls, text: str) -> str:
        if not text:
            return ""
        try:
            # 1. Remove <script>...</script> completely (tags and contents)
            text = re.sub(r"<script\b[^>]*>([\s\S]*?)<\/script>", "", text, flags=re.IGNORECASE)

            # 2. Remove javascript: protocol (case-insensitive)
            text = re.sub(r"javascript:", "", text, flags=re.IGNORECASE)

            # 3. Clean remaining HTML tags and attributes
            cleaned = bleach.clean(text, tags=[], strip=True)
            return cleaned.strip()
        except Exception as e:
            logger.warning("[InputSanitizer] bleach error: %s", e)
            return ""

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
