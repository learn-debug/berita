import logging
import re

from newsagent.core.events import make_event
from newsagent.core.state import ArticleState
from newsagent.cost.token_budget import with_budget
from newsagent.llm.base_adapter import BaseLLMAdapter
from newsagent.resilience.retry_policy import with_retry
from newsagent.security.prompt_hardening import PromptHardener
from newsagent.tools.cms_client import CMSClient
from newsagent.utils.prompt_loader import load_prompt

logger = logging.getLogger(__name__)


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
            prompt = PromptHardener.wrap_user_input(
                f"Buat judul dan siapkan artikel berikut untuk publikasi:\n\n{content}"
            )
            result = await self.llm.complete(
                system=self._system_prompt(),
                prompt=prompt,
            )
            logger.info("[PublisherAgent] LLM selesai — %d karakter", len(result))
        except Exception as e:
            logger.error("[PublisherAgent] LLM gagal: %s", e)
            return self._fail(state, str(e))

        title, body = self._parse_result(result)
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
            "status": "published",
            "published_title": title,
            "published_body": body,
            "published_url": published_url,
            "events": state["events"]
            + [make_event("PublisherAgent", "publish_article", "artikel dipublikasikan")],
        }

    def _parse_result(self, text: str) -> tuple[str, str]:
        title_match = re.search(r"JUDUL:\s*(.+)$", text, re.IGNORECASE | re.MULTILINE)
        konten_match = re.search(r"KONTEN:\s*(.+)", text, re.IGNORECASE | re.DOTALL)

        title = title_match.group(1).strip() if title_match else ""
        body = konten_match.group(1).strip() if konten_match else ""
        return title, body

    def _fail(self, state: ArticleState, reason: str) -> ArticleState:
        return {
            **state,
            "status": "failed",
            "events": state["events"] + [make_event("PublisherAgent", "publish_failed", reason)],
        }

    def _system_prompt(self) -> str:
        return PromptHardener.SYSTEM_GUARD + "\n\n" + load_prompt("publisher_agent.md")
