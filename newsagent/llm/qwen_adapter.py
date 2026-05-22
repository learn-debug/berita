import logging
from typing import Any

from openai import AsyncOpenAI

from newsagent.core.config import settings
from newsagent.llm.base_adapter import BaseLLMAdapter

logger = logging.getLogger(__name__)


class QwenAdapter(BaseLLMAdapter):
    _model = "qwen-plus"

    def _get_client(self) -> AsyncOpenAI:
        if not hasattr(self, "_client"):
            self._client = AsyncOpenAI(
                api_key=settings.qwen_api_key,
                base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
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
            logger.error("[QwenAdapter] API error: %s", e)
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
                response_format={"type": "json_object"},
            )
            return {"raw": response.choices[0].message.content or ""}
        except Exception as e:
            logger.error("[QwenAdapter] structured API error: %s", e)
            raise

    def model_name(self) -> str:
        return self._model
