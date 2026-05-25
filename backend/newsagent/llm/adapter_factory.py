import logging

from newsagent.core.config import settings
from newsagent.llm.base_adapter import BaseLLMAdapter
from newsagent.llm.claude_adapter import ClaudeAdapter
from newsagent.llm.deepseek_adapter import DeepSeekAdapter
from newsagent.llm.fallback_adapter import FallbackAdapter
from newsagent.llm.gemini_adapter import GeminiAdapter
from newsagent.llm.hf_adapter import HuggingFaceAdapter
from newsagent.llm.mistral_adapter import MistralAdapter
from newsagent.llm.openai_adapter import OpenAIAdapter
from newsagent.llm.openrouter_adapter import OpenRouterAdapter
from newsagent.llm.qwen_adapter import QwenAdapter

logger = logging.getLogger(__name__)

_HF_MODEL_KEYS: dict[str, str] = {
    "orchestrator": "orchestrator_hf_model",
    "draft_agent": "draft_agent_hf_model",
    "editor_agent": "editor_agent_hf_model",
    "fact_check": "fact_check_hf_model",
    "publisher_agent": "publisher_agent_hf_model",
    "rag": "rag_hf_model",
}

_ADAPTER_CLASSES: dict[str, type[BaseLLMAdapter]] = {
    "claude": ClaudeAdapter,
    "deepseek": DeepSeekAdapter,
    "gemini": GeminiAdapter,
    "mistral": MistralAdapter,
    "openai": OpenAIAdapter,
    "qwen": QwenAdapter,
}


def _build_single_adapter(provider: str, agent_key: str) -> BaseLLMAdapter:
    if provider == "openrouter":
        return OpenRouterAdapter(agent_key)
    if provider == "hf":
        model_key = _HF_MODEL_KEYS.get(agent_key, "orchestrator_hf_model")
        model = getattr(settings, model_key, "Qwen/Qwen2.5-7B-Instruct")
        return HuggingFaceAdapter(model=model)
    cls = _ADAPTER_CLASSES.get(provider)
    if cls is None:
        raise ValueError(
            f"Unknown LLM provider '{provider}'. Valid: {', '.join(_ADAPTER_CLASSES)}, openrouter, hf"
        )
    return cls()


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

    if settings.llm_fallback_chain:
        chain = [p.strip() for p in settings.llm_fallback_chain.split(",") if p.strip()]
        adapters = [_build_single_adapter(p, agent_key) for p in chain]
        logger.info(
            "[Factory] %s fallback chain: %s", agent_key, " -> ".join(a.model_name() for a in adapters)
        )
        return FallbackAdapter(adapters)

    return _build_single_adapter(provider, agent_key)
