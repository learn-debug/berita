import logging

from newsagent.core.events import make_event
from newsagent.core.state import ArticleState
from newsagent.llm.base_adapter import BaseLLMAdapter
from newsagent.resilience.retry_policy import with_retry
from newsagent.tools.scoring import compute_credibility, routing

logger = logging.getLogger(__name__)


class QualityGateAgent:
    def __init__(self, llm: BaseLLMAdapter):
        self.llm = llm

    @with_retry(max_attempts=3)
    async def run(self, state: ArticleState) -> ArticleState:
        logger.info("[QualityGate] mulai — article_id=%s", state["article_id"])

        result = await self.llm.complete(
            system=self._system_prompt(),
            prompt=f"Artikel:\n{state.get('aggregated_article', state.get('edited_draft', state['draft']))}",
        )

        score = compute_credibility()
        route = routing(score)

        logger.info("[QualityGate] skor=%.2f routing=%s", score, route)

        return {
            **state,
            "credibility_score": score,
            "status": "review" if route == "editor-review" else state["status"],
            "events": state["events"]
            + [make_event("QualityGate", "score_article", f"skor={score}, routing={route}")],
        }

    def _system_prompt(self) -> str:
        return (
            "Evaluasi artikel ini untuk credibility scoring. "
            "Pertimbangkan akurasi faktual, konsistensi narasi, resolusi konflik, dan kualitas sumber."
        )
