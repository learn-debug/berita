import logging

from newsagent.core.config import settings
from newsagent.tools.search_provider import SearchProvider
from newsagent.tools.serper_provider import SerperSearchProvider
from newsagent.tools.tavily_provider import TavilySearchProvider
from newsagent.tools.web_search import WebSearchTool

logger = logging.getLogger(__name__)


def search_provider_factory() -> SearchProvider:
    provider = settings.search_provider

    providers: dict[str, type[SearchProvider]] = {
        "tavily": TavilySearchProvider,
        "serper": SerperSearchProvider,
    }

    cls = providers.get(provider)

    if cls is TavilySearchProvider:
        if settings.tavily_api_key:
            logger.info("[SearchFactory] menggunakan TavilySearchProvider")
            return cls(api_key=settings.tavily_api_key)
        logger.warning("[SearchFactory] TAVILY_API_KEY tidak dikonfigurasi")

    if cls is SerperSearchProvider:
        if settings.serper_api_key:
            logger.info("[SearchFactory] menggunakan SerperSearchProvider")
            return cls(api_key=settings.serper_api_key)
        logger.warning("[SearchFactory] SERPER_API_KEY tidak dikonfigurasi")

    logger.warning(
        "[SearchFactory] search_provider='%s' tanpa API key, fallback ke DuckDuckGo",
        provider,
    )
    return WebSearchTool()
