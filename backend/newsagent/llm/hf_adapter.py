import logging
from typing import Any

from huggingface_hub import AsyncInferenceClient

from newsagent.core.config import settings
from newsagent.llm.base_adapter import BaseLLMAdapter, parse_json_response
from newsagent.resilience.retry_policy import RateLimiter, with_rate_limit_retry

logger = logging.getLogger(__name__)


class HuggingFaceAdapter(BaseLLMAdapter):
    def __init__(self, model: str = "Qwen/Qwen2.5-7B-Instruct") -> None:
        self._model = model
        token = settings.hf_api_key
        self._client = AsyncInferenceClient(api_key=token)
        self._rate_limiter = RateLimiter(provider="huggingface", max_concurrent=1, min_interval=2.0)

    @with_rate_limit_retry()
    async def complete(self, prompt: str, system: str | None = None, max_tokens: int = 2048) -> str:
        await self._rate_limiter.acquire()
        try:
            messages: list[dict[str, str]] = []
            if system:
                messages.append({"role": "system", "content": system})
            messages.append({"role": "user", "content": prompt})

            response = await self._client.chat_completion(
                model=self._model,
                messages=messages,
                max_tokens=max_tokens,
            )
            return response.choices[0].message.content or ""
        except Exception as e:
            logger.error("[HuggingFaceAdapter] API error: %s", e)
            raise
        finally:
            self._rate_limiter.release()

    @with_rate_limit_retry()
    async def complete_structured(
        self, prompt: str, schema: dict[str, Any], system: str | None = None, max_tokens: int = 2048
    ) -> dict[str, Any]:
        await self._rate_limiter.acquire()
        try:
            messages: list[dict[str, str]] = []
            if system:
                messages.append({"role": "system", "content": system})
            json_instruction = "\n\nRespond only with valid JSON matching this schema:\n" + str(schema)
            messages.append({"role": "user", "content": prompt + json_instruction})

            response = await self._client.chat_completion(
                model=self._model,
                messages=messages,
                max_tokens=max_tokens,
                response_format={"type": "json_object"},
            )
            return parse_json_response(response.choices[0].message.content or "", "HuggingFaceAdapter")
        except Exception as e:
            logger.error("[HuggingFaceAdapter] structured API error: %s", e)
            raise
        finally:
            self._rate_limiter.release()

    def model_name(self) -> str:
        return self._model
