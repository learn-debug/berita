from typing import Any

from openai import AsyncOpenAI

from newsagent.core.config import settings
from newsagent.llm.base_adapter import BaseLLMAdapter


class QwenAdapter(BaseLLMAdapter):
    _model = "qwen-plus"

    def __init__(self) -> None:
        self._client = AsyncOpenAI(
            api_key=settings.qwen_api_key,
            base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
        )

    async def complete(self, prompt: str, system: str | None = None) -> str:
        response = await self._client.chat.completions.create(
            model=self._model,
            max_tokens=4096,
            messages=[
                {"role": "system", "content": system or ""},
                {"role": "user", "content": prompt},
            ],
        )
        return response.choices[0].message.content or ""

    async def complete_structured(
        self, prompt: str, schema: dict[str, Any], system: str | None = None
    ) -> dict[str, Any]:
        response = await self._client.chat.completions.create(
            model=self._model,
            max_tokens=4096,
            messages=[
                {"role": "system", "content": system or ""},
                {"role": "user", "content": prompt},
            ],
            response_format={"type": "json_object"},
        )
        return {"raw": response.choices[0].message.content or ""}

    def model_name(self) -> str:
        return self._model
