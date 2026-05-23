import logging

from newsagent.core.events import make_event
from newsagent.core.state import ArticleState
from newsagent.llm.base_adapter import BaseLLMAdapter
from newsagent.memory.verdict_cache import VerdictCache
from newsagent.resilience.retry_policy import with_retry
from newsagent.security.prompt_hardening import PromptHardener
from newsagent.utils.prompt_loader import load_prompt

logger = logging.getLogger(__name__)


class VerdictPredictionAgent:
    def __init__(self, llm: BaseLLMAdapter):
        self.llm = llm
        self._cache = VerdictCache()

    @with_retry(max_attempts=3)
    async def run(self, state: ArticleState) -> ArticleState:
        logger.info("[VerdictPrediction] mulai — article_id=%s", state["article_id"])

        report = state.get("fact_check_report", {})
        claims = report.get("claims", "")
        evidence = report.get("evidence", "")

        claim_list = [c.strip() for c in claims.split("\n") if c.strip()]

        cached_parts: list[str] = []
        uncached_claims: list[str] = []

        for claim in claim_list:
            cached = await self._cache.get(claim)
            if cached and cached.get("verdict"):
                cached_parts.append(f"Klaim: {claim}\nPutusan (dari cache): {cached['verdict']}")
                logger.info("[VerdictPrediction] cache hit: %.60s...", claim)
            else:
                uncached_claims.append(claim)

        verdict = ""

        if uncached_claims:
            try:
                user_prompt = (
                    f"Klaim:\n" + "\n".join(uncached_claims) +
                    f"\n\nBukti:\n{evidence}\n\nBerikan putusan untuk setiap klaim."
                )
                result = await self.llm.complete(
                    system=self._system_prompt(),
                    prompt=PromptHardener.wrap_user_input(user_prompt),
                )
                verdict = result

                for claim in uncached_claims:
                    await self._cache.set(claim, verdict, evidence, 0.5)
            except Exception as e:
                logger.error("[VerdictPrediction] gagal: %s", e)
                verdict = ""

        if cached_parts:
            if verdict:
                verdict = "--- HASIL DARI CACHE ---\n" + "\n\n".join(cached_parts) + "\n\n--- HASIL BARU ---\n" + verdict
            else:
                verdict = "\n\n".join(cached_parts)

        fact_check = {**report, "verdict": verdict}

        return {
            **state,
            "fact_check_report": fact_check,
            "events": state["events"]
            + [make_event("VerdictPrediction", "predict_verdict", f"{len(verdict)} chars")],
        }

    def _system_prompt(self) -> str:
        return PromptHardener.SYSTEM_GUARD + "\n\n" + load_prompt("fact_check/verdict_prediction.md")
