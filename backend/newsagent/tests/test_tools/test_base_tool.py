import pytest

from newsagent.tools.base import BaseTool


class ConcreteTool(BaseTool):
    @property
    def name(self) -> str:
        return "concrete_tool"


class ToolWithDescription(BaseTool):
    @property
    def name(self) -> str:
        return "described_tool"

    @property
    def description(self) -> str:
        return "A tool with a description"


def test_base_tool_name_abstract() -> None:
    tool = ConcreteTool()
    assert tool.name == "concrete_tool"


def test_base_tool_default_description() -> None:
    tool = ConcreteTool()
    assert tool.description == ""


def test_base_tool_custom_description() -> None:
    tool = ToolWithDescription()
    assert tool.description == "A tool with a description"


@pytest.mark.asyncio
async def test_base_tool_setup_default() -> None:
    tool = ConcreteTool()
    await tool.setup()


@pytest.mark.asyncio
async def test_base_tool_close_default() -> None:
    tool = ConcreteTool()
    await tool.close()


def test_base_tool_validate_default() -> None:
    tool = ConcreteTool()
    result = tool._validate(key1="value1", key2=42)
    assert result == {"key1": "value1", "key2": 42}


def test_base_tool_validate_empty() -> None:
    tool = ConcreteTool()
    result = tool._validate()
    assert result == {}
