from collections.abc import Sequence
from typing import Any

from mistralai.client import Mistral
from mistralai.client.models import ChatCompletionChoice, SystemMessage, UserMessage

from newsagent.core.config import settings
from newsagent.llm.base_adapter import BaseLLMAdapter


class MistralAdapter(BaseLLMAdapter):
    _model = "mistral-small-latest"

    def __init__(self) -> None:
        self._client = Mistral(api_key=settings.mistral_api_key)

    async def complete(self, prompt: str, system: str | None = None) -> str:
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

    async def complete_structured(
        self, prompt: str, schema: dict[str, Any], system: str | None = None
    ) -> dict[str, Any]:
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

    def model_name(self) -> str:
        return self._model
