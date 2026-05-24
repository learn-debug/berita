from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = "postgresql+asyncpg://newsagent:newsagent_dev@localhost:5432/newsagent"
    redis_url: str = "redis://localhost:6379/0"

    anthropic_api_key: str = ""
    openai_api_key: str = ""
    gemini_api_key: str = ""
    mistral_api_key: str = ""
    qwen_api_key: str = ""
    deepseek_api_key: str = ""
    openrouter_api_key: str = ""
    tavily_api_key: str = ""
    serper_api_key: str = ""
    hf_api_key: str = ""

    search_provider: str = "tavily"

    orchestrator_llm: str = "mistral"
    draft_agent_llm: str = "mistral"
    editor_agent_llm: str = "mistral"
    fact_check_llm: str = "mistral"
    publisher_agent_llm: str = "mistral"
    rag_llm: str = "mistral"

    orchestrator_openrouter_model: str = "openai/gpt-4o"
    draft_agent_openrouter_model: str = "openai/gpt-4o-mini"
    editor_agent_openrouter_model: str = "openai/gpt-4o-mini"
    fact_check_openrouter_model: str = "openai/gpt-4o"
    publisher_agent_openrouter_model: str = "openai/gpt-4o-mini"
    rag_openrouter_model: str = "openai/gpt-4o-mini"

    orchestrator_hf_model: str = "Qwen/Qwen2.5-7B-Instruct"
    draft_agent_hf_model: str = "Qwen/Qwen2.5-7B-Instruct"
    editor_agent_hf_model: str = "Qwen/Qwen2.5-7B-Instruct"
    fact_check_hf_model: str = "Qwen/Qwen2.5-7B-Instruct"
    publisher_agent_hf_model: str = "Qwen/Qwen2.5-7B-Instruct"
    rag_hf_model: str = "Qwen/Qwen2.5-7B-Instruct"

    llm_fallback_chain: str = ""

    quality_gate_auto_publish: float = 0.75
    quality_gate_review_threshold: float = 0.50

    api_key: str = ""

    cms_base_url: str = ""
    cms_api_key: str = ""

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


settings = Settings()
