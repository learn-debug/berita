from functools import lru_cache
from pathlib import Path

PROMPTS_DIR = Path(__file__).parent


class PromptLoader:
    @staticmethod
    @lru_cache(maxsize=None)
    def _read(name: str) -> str:
        path = PROMPTS_DIR / f"{name}.md"
        return path.read_text(encoding="utf-8").strip()

    @classmethod
    def raw(cls, name: str, **kwargs) -> str:
        text = cls._read(name)
        if kwargs:
            text = text.format(**kwargs)
        return text

    @classmethod
    def system(cls, name: str) -> str:
        guard = cls.raw("_system_guard")
        specific = cls.raw(f"{name}_system")
        return f"{guard}\n\n{specific}"

    @classmethod
    def user(cls, name: str, **kwargs) -> str:
        raw_input = cls.raw(f"{name}_user", **kwargs)
        return cls.raw("_user_wrapper", user_input=raw_input)

    @classmethod
    def clear_cache(cls) -> None:
        cls._read.cache_clear()
