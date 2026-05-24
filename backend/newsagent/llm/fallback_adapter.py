import logging
from typing import Any

from newsagent.llm.base_adapter import BaseLLMAdapter

logger = logging.getLogger(__name__)


class FallbackAdapter(BaseLLMAdapter):
    def __init__(self, adapters: list[BaseLLMAdapter]) -> None:
        if not adapters:
            raise ValueError("FallbackAdapter requires at least one adapter")
        self.adapters = adapters

    async def complete(self, prompt: str, system: str | None = None, max_tokens: int = 2048) -> str:
        last_error: Exception | None = None
        for i, adapter in enumerate(self.adapters):
            try:
                return await adapter.complete(prompt, system, max_tokens)
            except Exception as e:
                last_error = e
                logger.warning(
                    "[Fallback] %s (%s) gagal, coba berikutnya: %s",
                    adapter.model_name(),
                    type(e).__name__,
                    e,
                )
                if i < len(self.adapters) - 1:
                    nxt = self.adapters[i + 1].model_name()
                    logger.info("[Fallback] %s -> %s", adapter.model_name(), nxt)
        raise last_error  # type: ignore[misc]

    async def complete_structured(
        self, prompt: str, schema: dict[str, Any], system: str | None = None, max_tokens: int = 2048
    ) -> dict[str, Any]:
        last_error: Exception | None = None
        for i, adapter in enumerate(self.adapters):
            try:
                return await adapter.complete_structured(prompt, schema, system, max_tokens)
            except Exception as e:
                last_error = e
                logger.warning(
                    "[Fallback] %s structured gagal, coba berikutnya: %s",
                    adapter.model_name(),
                    e,
                )
                if i < len(self.adapters) - 1:
                    nxt = self.adapters[i + 1].model_name()
                    logger.info("[Fallback] %s -> %s", adapter.model_name(), nxt)
        raise last_error  # type: ignore[misc]

    def model_name(self) -> str:
        return "+".join(a.model_name() for a in self.adapters)
