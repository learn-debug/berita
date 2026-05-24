import json
import logging
from abc import ABC, abstractmethod
from typing import Any

logger = logging.getLogger(__name__)


def parse_json_response(text: str, source: str = "unknown") -> dict[str, Any]:
    try:
        return dict(json.loads(text))
    except (json.JSONDecodeError, TypeError, ValueError) as e:
        logger.error("[%s] JSON parse gagal: %s | text=%.200s", source, e, text)
        return {}


class BaseLLMAdapter(ABC):
    @abstractmethod
    async def complete(
        self, prompt: str, system: str | None = None, max_tokens: int = 2048
    ) -> str: ...

    @abstractmethod
    async def complete_structured(
        self, prompt: str, schema: dict[str, Any], system: str | None = None, max_tokens: int = 2048
    ) -> dict[str, Any]: ...

    @abstractmethod
    def model_name(self) -> str: ...
