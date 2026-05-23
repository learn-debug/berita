from newsagent.core.config import settings
from newsagent.llm.base_adapter import BaseLLMAdapter
from newsagent.llm.claude_adapter import ClaudeAdapter
from newsagent.llm.deepseek_adapter import DeepSeekAdapter
from newsagent.llm.gemini_adapter import GeminiAdapter
from newsagent.llm.mistral_adapter import MistralAdapter
from newsagent.llm.openai_adapter import OpenAIAdapter
from newsagent.llm.qwen_adapter import QwenAdapter


def adapter_factory(agent_key: str) -> BaseLLMAdapter:
    provider_map: dict[str, str] = {
        "orchestrator": settings.orchestrator_llm,
        "draft_agent": settings.draft_agent_llm,
        "editor_agent": settings.editor_agent_llm,
        "fact_check": settings.fact_check_llm,
        "publisher_agent": settings.publisher_agent_llm,
        "rag": settings.rag_llm,
    }
    provider = provider_map.get(agent_key)
    if provider is None:
        raise ValueError(f"Unknown agent key '{agent_key}'. Valid keys: {', '.join(provider_map)}")

    adapters: dict[str, type[BaseLLMAdapter]] = {
        "claude": ClaudeAdapter,
        "openai": OpenAIAdapter,
        "gemini": GeminiAdapter,
        "mistral": MistralAdapter,
        "qwen": QwenAdapter,
        "deepseek": DeepSeekAdapter,
    }
    cls = adapters.get(provider)
    if cls is None:
        raise ValueError(
            f"Unknown LLM provider '{provider}' for agent '{agent_key}'. "
            f"Valid providers: {', '.join(adapters)}"
        )
    return cls()
