from abc import ABC, abstractmethod


class SearchProvider(ABC):
    @abstractmethod
    async def search(self, query: str, max_results: int = 5) -> list[str]: ...

    async def close(self) -> None:
        pass
