import logging

from newsagent.core.events import make_event
from newsagent.core.state import ArticleState, ArticleStatus
from newsagent.cost.token_budget import with_budget
from newsagent.llm.base_adapter import BaseLLMAdapter
from newsagent.memory.draft_memory import DraftMemory
from newsagent.resilience.retry_policy import with_retry
from newsagent.security.prompt_hardening import PromptHardener
from newsagent.tools.scoring import compute_credibility, routing
from newsagent.utils.prompt_loader import load_prompt

logger = logging.getLogger(__name__)

QUALITY_GATE_SCHEMA: dict[str, object] = {
    "type": "object",
    "properties": {
        "fact_accuracy": {"type": "number", "minimum": 0.0, "maximum": 1.0},
        "narrative_consistency": {"type": "number", "minimum": 0.0, "maximum": 1.0},
        "conflict_resolution": {"type": "number", "minimum": 0.0, "maximum": 1.0},
        "source_quality": {"type": "number", "minimum": 0.0, "maximum": 1.0},
    },
    "required": ["fact_accuracy", "narrative_consistency", "conflict_resolution", "source_quality"],
}


class QualityGateAgent:
    def __init__(self, llm: BaseLLMAdapter, draft_memory: DraftMemory | None = None):
        self.llm = llm
        self._draft_memory = draft_memory

    @with_retry(max_attempts=3)
    @with_budget(max_tokens=1024)
    async def run(self, state: ArticleState) -> ArticleState:
        logger.info("[QualityGate] mulai — article_id=%s", state["article_id"])

        article = state.get("aggregated_article") or state.get("edited_draft") or state["draft"]
        report = str(state.get("fact_check_report", {}))

        if len(article) > 10000:
            article = article[:10000] + "\n...[truncated]"
        if len(report) > 10000:
            report = report[:10000] + "\n...[truncated]"

        try:
            result = await self.llm.complete_structured(
                system=self._system_prompt(),
                prompt=f"Artikel:\n{article}\n\nLaporan Fact-Check:\n{report}",
                schema=QUALITY_GATE_SCHEMA,
                max_tokens=1024,
            )
            scores = result
        except Exception as e:
            logger.error("[QualityGate] gagal: %s", e)
            scores = {}
            if state.get("credibility_score", 0.0) > 0.0:
                return {
                    **state,
                    "events": state["events"]
                    + [make_event("QualityGate", "score_fallback", "LLM fail, retain previous score")],
                }

        score = compute_credibility(
            fact_accuracy=scores.get("fact_accuracy", 0.0),
            narrative_consistency=scores.get("narrative_consistency", 0.0),
            conflict_resolution=scores.get("conflict_resolution", 0.0),
            source_quality=scores.get("source_quality", 0.0),
        )
        route = routing(score)

        status = state["status"]
        if route == "editor-review":
            status = ArticleStatus.REVIEW.value
        elif route == "full-revision":
            status = ArticleStatus.REVISION.value

        logger.info("[QualityGate] skor=%.2f routing=%s", score, route)

        if self._draft_memory:
            try:
                await self._draft_memory.save(
                    topic=state["raw_input"],
                    draft=article[:1000],
                    credibility_score=score,
                    feedback=route,
                )
            except Exception as e:
                logger.warning("[QualityGate] save memory gagal: %s", e)

        return {
            **state,
            "credibility_score": score,
            "status": status,
            "events": state["events"]
            + [make_event("QualityGate", "score_article", f"skor={score}, routing={route}")],
        }

    def _system_prompt(self) -> str:
        return PromptHardener.SYSTEM_GUARD + "\n\n" + load_prompt("quality_gate.md")
