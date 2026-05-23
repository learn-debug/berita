import logging
from typing import Any

from anthropic import AsyncAnthropic
from anthropic.types import TextBlock

from newsagent.core.config import settings
from newsagent.llm.base_adapter import BaseLLMAdapter

logger = logging.getLogger(__name__)


class ClaudeAdapter(BaseLLMAdapter):
    _model = "claude-sonnet-4-20250514"

    def __init__(self) -> None:
        self._client = AsyncAnthropic(api_key=settings.anthropic_api_key)

    def _extract_text(self, content: list[Any]) -> str:
        for block in content:
            if isinstance(block, TextBlock):
                return block.text
        return ""

    async def complete(self, prompt: str, system: str | None = None) -> str:
        try:
            response = await self._client.messages.create(
                model=self._model,
                max_tokens=4096,
                system=system or "",
                messages=[{"role": "user", "content": prompt}],
            )
            return self._extract_text(response.content)
        except Exception as e:
            logger.error("[ClaudeAdapter] API error: %s", e)
            raise

    async def complete_structured(
        self, prompt: str, schema: dict[str, Any], system: str | None = None
    ) -> dict[str, Any]:
        try:
            response = await self._client.messages.create(
                model=self._model,
                max_tokens=4096,
                system=system or "",
                messages=[{"role": "user", "content": prompt}],
            )
            return {"raw": self._extract_text(response.content)}
        except Exception as e:
            logger.error("[ClaudeAdapter] structured API error: %s", e)
            raise

    def model_name(self) -> str:
        return self._model
