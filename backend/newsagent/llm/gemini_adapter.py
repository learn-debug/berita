import logging
from typing import Any

from google import genai

from newsagent.core.config import settings
from newsagent.llm.base_adapter import BaseLLMAdapter, parse_json_response
from newsagent.resilience.retry_policy import RateLimiter, with_rate_limit_retry

logger = logging.getLogger(__name__)


class GeminiAdapter(BaseLLMAdapter):
    _model = "gemini-2.5-flash-lite"

    def __init__(self) -> None:
        self._rate_limiter = RateLimiter(provider="gemini", max_concurrent=1, min_interval=1.0)

    def _get_client(self) -> genai.Client:
        if not hasattr(self, "_client"):
            self._client = genai.Client(api_key=settings.gemini_api_key)
        return self._client

    @with_rate_limit_retry()
    async def complete(self, prompt: str, system: str | None = None, max_tokens: int = 2048) -> str:
        await self._rate_limiter.acquire()
        client = self._get_client()
        try:
            response = await client.aio.models.generate_content(
                model=self._model,
                contents=prompt,
                config=genai.types.GenerateContentConfig(system_instruction=system or ""),
            )
            return response.text or ""
        except Exception as e:
            logger.error("[GeminiAdapter] API error: %s", e)
            raise
        finally:
            self._rate_limiter.release()

    @with_rate_limit_retry()
    async def complete_structured(
        self, prompt: str, schema: dict[str, Any], system: str | None = None, max_tokens: int = 2048
    ) -> dict[str, Any]:
        await self._rate_limiter.acquire()
        client = self._get_client()
        try:
            response = await client.aio.models.generate_content(
                model=self._model,
                contents=prompt,
                config=genai.types.GenerateContentConfig(
                    system_instruction=system or "",
                    response_mime_type="application/json",
                    response_schema=schema,
                ),
            )
            return parse_json_response(response.text or "", "GeminiAdapter")
        except Exception as e:
            logger.error("[GeminiAdapter] structured API error: %s", e)
            raise
        finally:
            self._rate_limiter.release()

    def model_name(self) -> str:
        return self._model
