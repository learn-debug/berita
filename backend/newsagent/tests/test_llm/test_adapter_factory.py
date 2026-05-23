import pytest

from newsagent.llm.adapter_factory import adapter_factory
from newsagent.llm.base_adapter import BaseLLMAdapter


def test_adapter_factory_returns_adapter() -> None:
    adapter = adapter_factory("orchestrator")
    assert isinstance(adapter, BaseLLMAdapter)
    assert adapter.model_name() is not None


def test_adapter_factory_unknown_key_raises() -> None:
    with pytest.raises(ValueError, match="Unknown agent key"):
        adapter_factory("unknown_agent")


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


def test_adapter_factory_empty_key_raises() -> None:
    with pytest.raises(ValueError, match="Unknown agent key"):
        adapter_factory("")
