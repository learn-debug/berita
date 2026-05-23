import logging
import re
from typing import Any

from lxml.html import fromstring

logger = logging.getLogger(__name__)


class InputSanitizer:
    BLOCKED_TAGS: set[str] = {"script", "style", "iframe", "object", "embed", "svg", "noscript"}
    BLOCKED_ATTR_PATTERNS: list[re.Pattern[str]] = [
        re.compile(r"^\s*javascript:", re.IGNORECASE),
        re.compile(r"^\s*data:", re.IGNORECASE),
        re.compile(r"^\s*vbscript:", re.IGNORECASE),
    ]

    @classmethod
    def sanitize(cls, text: str) -> str:
        try:
            root = fromstring(f"<div>{text}</div>")
            for tag in cls.BLOCKED_TAGS:
                for elem in root.iter(tag):
                    elem.drop_tree()
            for elem in root.iter():
                for attr in list(elem.attrib):
                    val = elem.attrib[attr]
                    for pattern in cls.BLOCKED_ATTR_PATTERNS:
                        if pattern.search(val):
                            del elem.attrib[attr]
                            break
            result = root.text_content()
        except Exception as e:
            logger.warning("[InputSanitizer] HTML parse gagal, fallback regex: %s", e)
            result = ""
        result = re.sub(r"javascript\s*:", " ", result, flags=re.IGNORECASE)
        result = re.sub(r"on\w+\s*=", " ", result, flags=re.IGNORECASE)
        return result.strip()

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
