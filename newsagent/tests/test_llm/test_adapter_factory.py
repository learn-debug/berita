from newsagent.llm.adapter_factory import adapter_factory
from newsagent.llm.base_adapter import BaseLLMAdapter


def test_adapter_factory_returns_adapter() -> None:
    adapter = adapter_factory("orchestrator")
    assert isinstance(adapter, BaseLLMAdapter)
    assert adapter.model_name() is not None


def test_adapter_factory_unknown_key_falls_back_to_claude() -> None:
    adapter = adapter_factory("unknown_agent")
    assert isinstance(adapter, BaseLLMAdapter)


def test_adapter_factory_all_keys() -> None:
    for key in (
        "orchestrator",
        "draft_agent",
        "editor_agent",
        "fact_check",
        "publisher_agent",
        "rag",
    ):
        adapter = adapter_factory(key)
        assert isinstance(adapter, BaseLLMAdapter), f"Failed for key '{key}'"


def test_adapter_factory_empty_key() -> None:
    adapter = adapter_factory("")
    assert isinstance(adapter, BaseLLMAdapter)
