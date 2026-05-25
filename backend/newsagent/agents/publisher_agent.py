import logging

from newsagent.core.events import make_event
from newsagent.core.state import ArticleState, ArticleStatus
from newsagent.cost.token_budget import with_budget
from newsagent.llm.base_adapter import BaseLLMAdapter
from newsagent.resilience.retry_policy import with_retry
from newsagent.security.prompt_hardening import PromptHardener
from newsagent.tools.cms_client import CMSClient
from newsagent.utils.prompt_loader import load_prompt

logger = logging.getLogger(__name__)

PUBLISHER_SCHEMA: dict[str, object] = {
    "type": "object",
    "properties": {
        "judul": {"type": "string", "description": "Judul artikel, maks 12 kata, akurat dan menarik"},
        "konten": {"type": "string", "description": "Isi artikel lengkap siap tayang"},
    },
    "required": ["judul", "konten"],
}


class PublisherAgent:
    def __init__(self, llm: BaseLLMAdapter, cms: CMSClient | None = None):
        self.llm = llm
        self.cms = cms

    @with_retry(max_attempts=3)
    @with_budget(max_tokens=4000)
    async def run(self, state: ArticleState) -> ArticleState:
        logger.info("[PublisherAgent] mulai — article_id=%s", state["article_id"])

        content = state.get("aggregated_article") or state.get("edited_draft") or state["draft"]

        try:
            result = await self.llm.complete_structured(
                system=self._system_prompt(),
                prompt=PromptHardener.wrap_user_input(
                    f"Buat judul dan siapkan artikel berikut untuk publikasi:\n\n{content}"
                ),
                schema=PUBLISHER_SCHEMA,
                max_tokens=4096,
            )
            title = result.get("judul", "")
            body = result.get("konten", "")
            logger.info("[PublisherAgent] LLM selesai — judul=%s, body=%d karakter", title[:50], len(body))
        except Exception as e:
            logger.error("[PublisherAgent] LLM gagal: %s", e)
            return self._fail(state, str(e))

        if not title or not body:
            logger.warning(
                "[PublisherAgent] parse gagal (title=%s, body=%s), fallback ke raw",
                bool(title),
                bool(body),
            )
            title = title or f"Artikel {state['article_id']}"
            body = body or content

        published_url: str | None = None
        if self.cms:
            try:
                cms_result = await self.cms.publish(title, body)
                published_url = cms_result.get("link") or cms_result.get("id", "")
                logger.info("[PublisherAgent] CMS publish sukses — id=%s", published_url)
            except Exception as e:
                logger.error("[PublisherAgent] CMS publish gagal: %s", e)
                return self._fail(state, f"CMS error: {e}")

        return {
            **state,
            "status": ArticleStatus.PUBLISHED.value,
            "published_title": title,
            "published_body": body,
            "published_url": published_url,
            "events": state["events"]
            + [make_event("PublisherAgent", "publish_article", "artikel dipublikasikan")],
        }

    def _fail(self, state: ArticleState, reason: str) -> ArticleState:
        return {
            **state,
            "status": ArticleStatus.FAILED.value,
            "events": state["events"] + [make_event("PublisherAgent", "publish_failed", reason)],
        }

    def _system_prompt(self) -> str:
        return PromptHardener.SYSTEM_GUARD + "\n\n" + load_prompt("publisher_agent.md")
