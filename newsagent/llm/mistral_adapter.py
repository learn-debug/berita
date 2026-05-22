import logging
from collections.abc import Sequence
from typing import Any

from mistralai.client import Mistral
from mistralai.client.models import ChatCompletionChoice, SystemMessage, UserMessage

from newsagent.core.config import settings
from newsagent.llm.base_adapter import BaseLLMAdapter

logger = logging.getLogger(__name__)


class MistralAdapter(BaseLLMAdapter):
    _model = "mistral-small-latest"

    def __init__(self) -> None:
        self._client = Mistral(api_key=settings.mistral_api_key)

    async def complete(self, prompt: str, system: str | None = None) -> str:
        try:
            messages: Sequence[SystemMessage | UserMessage] = []
            if system:
                messages = [SystemMessage(content=system)]
            messages = list(messages) + [UserMessage(content=prompt)]

            response = await self._client.chat.complete_async(
                model=self._model,
                messages=messages,  # type: ignore[arg-type]
            )
            choice: ChatCompletionChoice = response.choices[0]
            msg = choice.message
            text = msg.content if msg else ""
            return text if isinstance(text, str) else ""
        except Exception as e:
            logger.error("[MistralAdapter] API error: %s", e)
            raise

    async def complete_structured(
        self, prompt: str, schema: dict[str, Any], system: str | None = None
    ) -> dict[str, Any]:
        try:
            messages: Sequence[SystemMessage | UserMessage] = []
            if system:
                messages = [SystemMessage(content=system)]
            messages = list(messages) + [UserMessage(content=prompt)]

            response = await self._client.chat.complete_async(
                model=self._model,
                messages=messages,  # type: ignore[arg-type]
                response_format={"type": "json_object"},
            )
            choice: ChatCompletionChoice = response.choices[0]
            msg = choice.message
            text = msg.content if msg else ""
            return {"raw": text if isinstance(text, str) else ""}
        except Exception as e:
            logger.error("[MistralAdapter] structured API error: %s", e)
            raise

    def model_name(self) -> str:
        return self._model
