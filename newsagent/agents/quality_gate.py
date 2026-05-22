import logging
import re

from newsagent.core.events import make_event
from newsagent.core.state import ArticleState
from newsagent.llm.base_adapter import BaseLLMAdapter
from newsagent.resilience.retry_policy import with_retry
from newsagent.tools.scoring import compute_credibility, routing

logger = logging.getLogger(__name__)


class QualityGateAgent:
    def __init__(self, llm: BaseLLMAdapter):
        self.llm = llm

    def _parse_scores(self, text: str) -> dict[str, float]:
        scores = {"fact_accuracy": 0.0, "narrative_consistency": 0.0, "conflict_resolution": 0.0, "source_quality": 0.0}
        for key in scores:
            match = re.search(rf"{key}[:\s]+([0-9]*\.?[0-9]+)", text, re.IGNORECASE)
            if match:
                val = float(match.group(1))
                scores[key] = max(0.0, min(1.0, val))
        return scores

    @with_retry(max_attempts=3)
    async def run(self, state: ArticleState) -> ArticleState:
        logger.info("[QualityGate] mulai — article_id=%s", state["article_id"])

        article = state.get("aggregated_article") or state.get("edited_draft") or state["draft"]
        report = state.get("fact_check_report", {})

        try:
            result = await self.llm.complete(
                system=self._system_prompt(),
                prompt=f"Artikel:\n{article}\n\nLaporan Fact-Check:\n{report}",
            )
            scores = self._parse_scores(result)
        except Exception as e:
            logger.error("[QualityGate] gagal: %s", e)
            scores = {}

        score = compute_credibility(
            fact_accuracy=scores.get("fact_accuracy", 0.0),
            narrative_consistency=scores.get("narrative_consistency", 0.0),
            conflict_resolution=scores.get("conflict_resolution", 0.0),
            source_quality=scores.get("source_quality", 0.0),
        )
        route = routing(score)

        status = state["status"]
        if route == "editor-review":
            status = "review"
        elif route == "full-revision":
            status = "revision"

        logger.info("[QualityGate] skor=%.2f routing=%s", score, route)

        return {
            **state,
            "credibility_score": score,
            "status": status,
            "events": state["events"]
            + [make_event("QualityGate", "score_article", f"skor={score}, routing={route}")],
        }

    def _system_prompt(self) -> str:
        return (
            "Evaluasi artikel ini untuk credibility scoring. Nilai 4 dimensi berikut dengan skor 0.0-1.0:\n"
            "- fact_accuracy: akurasi faktual berdasarkan laporan fact-check\n"
            "- narrative_consistency: konsistensi narasi dan alur artikel\n"
            "- conflict_resolution: resolusi konflik antar klaim\n"
            "- source_quality: kualitas sumber bukti yang digunakan\n\n"
            "Format output:\n"
            "fact_accuracy: 0.85\n"
            "narrative_consistency: 0.90\n"
            "conflict_resolution: 0.75\n"
            "source_quality: 0.80"
        )
