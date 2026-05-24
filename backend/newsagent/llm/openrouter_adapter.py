import logging
from typing import Any

from openai import AsyncOpenAI

from newsagent.core.config import settings
from newsagent.llm.base_adapter import BaseLLMAdapter, parse_json_response

logger = logging.getLogger(__name__)

_MODEL_MAP: dict[str, str] = {
    "orchestrator": settings.orchestrator_openrouter_model,
    "draft_agent": settings.draft_agent_openrouter_model,
    "editor_agent": settings.editor_agent_openrouter_model,
    "fact_check": settings.fact_check_openrouter_model,
    "publisher_agent": settings.publisher_agent_openrouter_model,
    "rag": settings.rag_openrouter_model,
}


class OpenRouterAdapter(BaseLLMAdapter):
    def __init__(self, agent_key: str) -> None:
        self._client = AsyncOpenAI(
            api_key=settings.openrouter_api_key,
            base_url="https://openrouter.ai/api/v1",
        )
        self._model = _MODEL_MAP.get(agent_key, "openai/gpt-4o")
        self._agent_key = agent_key

    async def complete(self, prompt: str, system: str | None = None, max_tokens: int = 2048) -> str:
        try:
            response = await self._client.chat.completions.create(
                model=self._model,
                max_tokens=4096,
                messages=[
                    {"role": "system", "content": system or ""},
                    {"role": "user", "content": prompt},
                ],
            )
            return response.choices[0].message.content or ""
        except Exception as e:
            logger.error("[OpenRouterAdapter] %s API error: %s", self._model, e)
            raise

    async def complete_structured(
        self, prompt: str, schema: dict[str, Any], system: str | None = None, max_tokens: int = 2048
    ) -> dict[str, Any]:
        try:
            response = await self._client.chat.completions.create(
                model=self._model,
                max_tokens=4096,
                messages=[
                    {"role": "system", "content": system or ""},
                    {"role": "user", "content": prompt},
                ],
                response_format={"type": "json_object"},
            )
            return parse_json_response(response.choices[0].message.content or "", "OpenRouterAdapter")
        except Exception as e:
            logger.error("[OpenRouterAdapter] %s structured error: %s", self._model, e)
            raise

    def model_name(self) -> str:
        return self._model
