from abc import ABC, abstractmethod
from typing import Any


class BaseTool(ABC):
    @property
    @abstractmethod
    def name(self) -> str: ...

    @property
    def description(self) -> str:
        return ""

    async def setup(self) -> None:
        pass

    async def close(self) -> None:
        pass

    def _validate(self, **kwargs: Any) -> dict[str, Any]:
        return kwargs
