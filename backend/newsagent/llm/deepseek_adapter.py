import logging
from typing import Any

from openai import AsyncOpenAI

from newsagent.core.config import settings
from newsagent.llm.base_adapter import BaseLLMAdapter

logger = logging.getLogger(__name__)


class DeepSeekAdapter(BaseLLMAdapter):
    _model = "deepseek-chat"

    def _get_client(self) -> AsyncOpenAI:
        if not hasattr(self, "_client"):
            self._client = AsyncOpenAI(
                api_key=settings.deepseek_api_key,
                base_url="https://api.deepseek.com",
            )
        return self._client

    async def complete(self, prompt: str, system: str | None = None) -> str:
        client = self._get_client()
        try:
            response = await client.chat.completions.create(
                model=self._model,
                max_tokens=4096,
                messages=[
                    {"role": "system", "content": system or ""},
                    {"role": "user", "content": prompt},
                ],
            )
            return response.choices[0].message.content or ""
        except Exception as e:
            logger.error("[DeepSeekAdapter] API error: %s", e)
            raise

    async def complete_structured(
        self, prompt: str, schema: dict[str, Any], system: str | None = None
    ) -> dict[str, Any]:
        client = self._get_client()
        try:
            response = await client.chat.completions.create(
                model=self._model,
                max_tokens=4096,
                messages=[
                    {"role": "system", "content": system or ""},
                    {"role": "user", "content": prompt},
                ],
            )
            return {"raw": response.choices[0].message.content or ""}
        except Exception as e:
            logger.error("[DeepSeekAdapter] structured API error: %s", e)
            raise

    def model_name(self) -> str:
        return self._model
