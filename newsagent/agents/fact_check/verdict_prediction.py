import logging

from newsagent.core.events import make_event
from newsagent.core.state import ArticleState
from newsagent.llm.base_adapter import BaseLLMAdapter
from newsagent.resilience.retry_policy import with_retry

logger = logging.getLogger(__name__)


class VerdictPredictionAgent:
    def __init__(self, llm: BaseLLMAdapter):
        self.llm = llm

    @with_retry(max_attempts=3)
    async def run(self, state: ArticleState) -> ArticleState:
        logger.info("[VerdictPrediction] mulai — article_id=%s", state["article_id"])

        report = state.get("fact_check_report", {})
        claims = report.get("claims", "")
        evidence = report.get("evidence", "")

        try:
            result = await self.llm.complete(
                system=self._system_prompt(),
                prompt=f"Klaim:\n{claims}\n\nBukti:\n{evidence}\n\nBerikan putusan untuk setiap klaim.",
            )
            verdict = result
        except Exception as e:
            logger.error("[VerdictPrediction] gagal: %s", e)
            verdict = ""

        fact_check = {**report, "verdict": verdict}

        return {
            **state,
            "fact_check_report": fact_check,
            "events": state["events"]
            + [make_event("VerdictPrediction", "predict_verdict", f"{len(verdict)} chars")],
        }

    def _system_prompt(self) -> str:
        return (
            "Berdasarkan klaim dan bukti yang diberikan, berikan putusan untuk setiap klaim: "
            "SUPPORTED, REFUTED, atau NOT_ENOUGH_EVIDENCE. Sertakan penjelasan singkat."
        )
