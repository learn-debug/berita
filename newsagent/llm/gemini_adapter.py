from typing import Any

from google import genai

from newsagent.core.config import settings
from newsagent.llm.base_adapter import BaseLLMAdapter


class GeminiAdapter(BaseLLMAdapter):
    _model = "gemini-2.0-flash"

    def __init__(self) -> None:
        self._client = genai.Client(api_key=settings.gemini_api_key)

    async def complete(self, prompt: str, system: str | None = None) -> str:
        response = await self._client.aio.models.generate_content(
            model=self._model,
            contents=prompt,
            config=genai.types.GenerateContentConfig(system_instruction=system or ""),
        )
        return response.text or ""

    async def complete_structured(
        self, prompt: str, schema: dict[str, Any], system: str | None = None
    ) -> dict[str, Any]:
        response = await self._client.aio.models.generate_content(
            model=self._model,
            contents=prompt,
            config=genai.types.GenerateContentConfig(
                system_instruction=system or "",
                response_mime_type="application/json",
                response_schema=schema,
            ),
        )
        return {"raw": response.text or ""}

    def model_name(self) -> str:
        return self._model
