from unittest.mock import patch

from newsagent.tools.search_factory import search_provider_factory
from newsagent.tools.serper_provider import SerperSearchProvider
from newsagent.tools.tavily_provider import TavilySearchProvider
from newsagent.tools.web_search import WebSearchTool


def test_factory_returns_tavily_when_configured() -> None:
    with patch("newsagent.tools.search_factory.settings") as mock_settings:
        mock_settings.search_provider = "tavily"
        mock_settings.tavily_api_key = "tavily-key"
        mock_settings.serper_api_key = ""

        provider = search_provider_factory()

    assert isinstance(provider, TavilySearchProvider)


def test_factory_returns_serper_when_configured() -> None:
    with patch("newsagent.tools.search_factory.settings") as mock_settings:
        mock_settings.search_provider = "serper"
        mock_settings.tavily_api_key = ""
        mock_settings.serper_api_key = "serper-key"

        provider = search_provider_factory()

    assert isinstance(provider, SerperSearchProvider)


def test_factory_fallback_to_websearch_when_no_api_key() -> None:
    with patch("newsagent.tools.search_factory.settings") as mock_settings:
        mock_settings.search_provider = "tavily"
        mock_settings.tavily_api_key = ""
        mock_settings.serper_api_key = ""

        provider = search_provider_factory()

    assert isinstance(provider, WebSearchTool)


def test_factory_fallback_for_unknown_provider() -> None:
    with patch("newsagent.tools.search_factory.settings") as mock_settings:
        mock_settings.search_provider = "unknown"
        mock_settings.tavily_api_key = ""
        mock_settings.serper_api_key = ""

        provider = search_provider_factory()

    assert isinstance(provider, WebSearchTool)
