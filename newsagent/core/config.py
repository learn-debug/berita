from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = "postgresql+asyncpg://newsagent:newsagent_dev@localhost:5432/newsagent"
    redis_url: str = "redis://localhost:6379/0"

    anthropic_api_key: str = ""
    openai_api_key: str = ""
    gemini_api_key: str = ""
    mistral_api_key: str = ""
    qwen_api_key: str = ""

    orchestrator_llm: str = "claude"
    draft_agent_llm: str = "claude"
    editor_agent_llm: str = "claude"
    fact_check_llm: str = "claude"
    publisher_agent_llm: str = "claude"
    rag_llm: str = "claude"

    quality_gate_auto_publish: float = 0.75
    quality_gate_review_threshold: float = 0.50

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


settings = Settings()
