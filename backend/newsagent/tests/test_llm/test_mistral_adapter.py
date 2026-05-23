from newsagent.llm.mistral_adapter import MistralAdapter


def test_model_name() -> None:
    adapter = MistralAdapter()
    assert "mistral" in adapter.model_name()
