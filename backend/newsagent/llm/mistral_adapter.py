import logging
from typing import Any

from mistralai.client import Mistral
from mistralai.client.models import ChatCompletionChoice, SystemMessage, UserMessage

from newsagent.core.config import settings
from newsagent.llm.base_adapter import BaseLLMAdapter, parse_json_response
from newsagent.resilience.retry_policy import RateLimiter, with_rate_limit_retry

logger = logging.getLogger(__name__)


class MistralAdapter(BaseLLMAdapter):
    _model = "mistral-small-latest"

    def __init__(self) -> None:
        self._client = Mistral(api_key=settings.mistral_api_key)
        self._rate_limiter = RateLimiter(provider="mistral", max_concurrent=1, min_interval=62.0)

    @with_rate_limit_retry()
    async def complete(self, prompt: str, system: str | None = None, max_tokens: int = 2048) -> str:
        await self._rate_limiter.acquire()
        try:
            messages: list[SystemMessage | UserMessage] = []
            if system:
                messages = [SystemMessage(content=system)]
            messages = messages + [UserMessage(content=prompt)]

            response = await self._client.chat.complete_async(
                model=self._model,
                messages=messages,
            )
            choice: ChatCompletionChoice = response.choices[0]
            msg = choice.message
            text = msg.content if msg else ""
            return text if isinstance(text, str) else ""
        except Exception as e:
            logger.error("[MistralAdapter] API error: %s", e)
            raise
        finally:
            self._rate_limiter.release()

    @with_rate_limit_retry()
    async def complete_structured(
        self, prompt: str, schema: dict[str, Any], system: str | None = None, max_tokens: int = 2048
    ) -> dict[str, Any]:
        await self._rate_limiter.acquire()
        try:
            messages: list[SystemMessage | UserMessage] = []
            if system:
                messages = [SystemMessage(content=system)]
            messages = messages + [UserMessage(content=prompt)]

            response = await self._client.chat.complete_async(
                model=self._model,
                messages=messages,
                response_format={"type": "json_object"},
            )
            choice: ChatCompletionChoice = response.choices[0]
            msg = choice.message
            text = msg.content if msg else ""
            return parse_json_response(text if isinstance(text, str) else "", "MistralAdapter")
        except Exception as e:
            logger.error("[MistralAdapter] structured API error: %s", e)
            raise
        finally:
            self._rate_limiter.release()

    def model_name(self) -> str:
        return self._model
