from abc import ABC, abstractmethod
from typing import Any


class BaseLLMAdapter(ABC):
    @abstractmethod
    async def complete(self, prompt: str, system: str | None = None) -> str: ...

    @abstractmethod
    async def complete_structured(
        self, prompt: str, schema: dict[str, Any], system: str | None = None
    ) -> dict[str, Any]: ...

    @abstractmethod
    def model_name(self) -> str: ...
