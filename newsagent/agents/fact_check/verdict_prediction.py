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

        claims = state.get("fact_check_report", {}).get("claims", "")
        evidence = state.get("fact_check_report", {}).get("evidence", "")

        result = await self.llm.complete(
            system=self._system_prompt(),
            prompt=f"Klaim:\n{claims}\n\nBukti:\n{evidence}\n\nBerikan putusan untuk setiap klaim.",
        )

        return {
            **state,
            "fact_check_report": {
                "claims": claims,
                "evidence": evidence,
                "verdict": result,
            },
            "events": state["events"] + [make_event("VerdictPrediction", "predict_verdict", result[:200])],
        }

    def _system_prompt(self) -> str:
        return (
            "Berdasarkan klaim dan bukti yang diberikan, berikan putusan untuk setiap klaim: "
            "SUPPORTED, REFUTED, atau NOT_ENOUGH_EVIDENCE. Sertakan penjelasan singkat."
        )
