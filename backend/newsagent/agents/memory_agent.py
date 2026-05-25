import logging
from typing import Any

from newsagent.core.events import make_event
from newsagent.core.state import ArticleState
from newsagent.database.kg_repository import KnowledgeGraphRepository
from newsagent.memory.draft_memory import DraftMemory
from newsagent.memory.verdict_cache import VerdictCache
from newsagent.tools.ner_extractor import extract_entities

logger = logging.getLogger(__name__)

CONSOLIDATION_MIN_SCORE = 0.50


class MemoryAgent:
    def __init__(
        self,
        draft_memory: DraftMemory | None = None,
        verdict_cache: VerdictCache | None = None,
        kg_repo: KnowledgeGraphRepository | None = None,
    ):
        self._draft_memory = draft_memory
        self._verdict_cache = verdict_cache
        self._kg_repo = kg_repo

    async def run(self, state: ArticleState) -> ArticleState:
        logger.info("[MemoryAgent] mulai — article_id=%s", state["article_id"])
        events: list[dict[str, Any]] = []
        score = state.get("credibility_score", 0.0)

        if score >= CONSOLIDATION_MIN_SCORE:
            await self._consolidate_draft(state, events)
            await self._consolidate_verdicts(state, events)

        if self._kg_repo and score >= CONSOLIDATION_MIN_SCORE:
            await self._extract_and_link_entities(state, events)

        if not events:
            events.append(make_event("MemoryAgent", "skip", "skor < threshold, lewati konsolidasi"))

        return {
            **state,
            "events": state["events"] + events,
        }

    async def _consolidate_draft(self, state: ArticleState, events: list[dict[str, Any]]) -> None:
        if not self._draft_memory:
            return
        article = state.get("aggregated_article") or state.get("edited_draft") or state.get("draft", "")
        if not article:
            return
        try:
            await self._draft_memory.save(
                topic=state["raw_input"],
                draft=article[:1000],
                credibility_score=state.get("credibility_score", 0.0),
                feedback=state.get("status", "unknown"),
            )
            events.append(make_event("MemoryAgent", "draft_saved", "draft disimpan ke memori"))
        except Exception as e:
            logger.warning("[MemoryAgent] draft save gagal: %s", e)

    async def _consolidate_verdicts(self, state: ArticleState, events: list[dict[str, Any]]) -> None:
        if not self._verdict_cache:
            return
        report = state.get("fact_check_report", {})
        verdict_raw = report.get("verdict_raw", []) if isinstance(report, dict) else []
        if not verdict_raw:
            return
        cached = 0
        for claim in verdict_raw:
            if isinstance(claim, dict):
                claim_text = claim.get("claim") or claim.get("claim_text", "")
                verdict_text = claim.get("verdict") or claim.get("result", "")
                evidence = claim.get("evidence", "")
                trust = float(claim.get("trust_score", 0.5))
                if claim_text and verdict_text:
                    try:
                        await self._verdict_cache.set(claim_text, verdict_text, evidence, trust)
                        cached += 1
                    except Exception as e:
                        logger.warning("[MemoryAgent] verdict cache gagal: %s", e)
        if cached:
            events.append(make_event("MemoryAgent", "verdicts_cached", f"{cached} klaim di-cache"))

    async def _extract_and_link_entities(self, state: ArticleState, events: list[dict[str, Any]]) -> None:
        article = state.get("aggregated_article") or state.get("edited_draft") or state.get("draft", "")
        if not article:
            return

        entities = await self._extract_entities(article, state["raw_input"])
        article_id = state["article_id"]
        linked = 0

        for ent in entities:
            try:
                entity = await self._kg_repo.upsert_entity(
                    name=ent["name"],
                    type=ent["type"],
                    description=ent["description"],
                )
                await self._kg_repo.link_article_entity(
                    article_id=article_id,
                    entity_id=entity["id"],
                    context=ent.get("context", ""),
                )
                linked += 1
            except Exception as e:
                logger.warning("[MemoryAgent] entity link gagal: %s", e)

        if linked:
            events.append(
                make_event(
                    "MemoryAgent",
                    "entities_linked",
                    f"{linked} entitas dari artikel dikaitkan ke knowledge graph",
                )
            )

    async def _extract_entities(self, article: str, topic: str) -> list[dict[str, str]]:
        return await extract_entities(article, topic=topic)
