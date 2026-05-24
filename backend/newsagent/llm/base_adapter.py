from abc import ABC, abstractmethod
from typing import Any


class BaseLLMAdapter(ABC):
    @abstractmethod
    async def complete(
        self, prompt: str, system: str | None = None, max_tokens: int = 2048
    ) -> str: ...

    @abstractmethod
    async def complete_structured(
        self, prompt: str, schema: dict[str, Any], system: str | None = None, max_tokens: int = 2048
    ) -> dict[str, Any]: ...

    @abstractmethod
    def model_name(self) -> str: ...
