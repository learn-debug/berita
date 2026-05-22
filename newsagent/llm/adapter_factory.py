from newsagent.core.config import settings
from newsagent.llm.base_adapter import BaseLLMAdapter
from newsagent.llm.claude_adapter import ClaudeAdapter
from newsagent.llm.gemini_adapter import GeminiAdapter
from newsagent.llm.openai_adapter import OpenAIAdapter


def adapter_factory(agent_key: str) -> BaseLLMAdapter:
    provider_map: dict[str, str] = {
        "orchestrator": settings.orchestrator_llm,
        "draft_agent": settings.draft_agent_llm,
        "editor_agent": settings.editor_agent_llm,
        "fact_check": settings.fact_check_llm,
        "publisher_agent": settings.publisher_agent_llm,
    }
    provider = provider_map.get(agent_key, "claude")

    adapters: dict[str, type[BaseLLMAdapter]] = {
        "claude": ClaudeAdapter,
        "openai": OpenAIAdapter,
        "gemini": GeminiAdapter,
    }
    cls = adapters.get(provider, ClaudeAdapter)
    return cls()
