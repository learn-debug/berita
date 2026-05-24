import logging
from typing import Any, cast

from newsagent.core.events import make_event
from newsagent.core.state import ArticleState, FactCheckReport
from newsagent.cost.token_budget import with_budget
from newsagent.llm.base_adapter import BaseLLMAdapter
from newsagent.memory.verdict_cache import VerdictCache
from newsagent.resilience.retry_policy import with_retry
from newsagent.security.prompt_hardening import PromptHardener
from newsagent.utils.prompt_loader import load_prompt

logger = logging.getLogger(__name__)

VERDICT_SCHEMA: dict[str, object] = {
    "type": "object",
    "properties": {
        "claims": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "claim": {"type": "string"},
                    "premis_fakta": {"type": "string"},
                    "premis_bukti": {"type": "string"},
                    "premis_sumber": {"type": "string"},
                    "analisis": {"type": "string"},
                    "putusan": {
                        "type": "string",
                        "enum": ["SUPPORTED", "REFUTED", "NOT_ENOUGH_EVIDENCE"],
                    },
                    "alasan": {"type": "string"},
                    "keyakinan": {"type": "string", "enum": ["TINGGI", "SEDANG", "RENDAH"]},
                },
                "required": [
                    "claim",
                    "premis_fakta",
                    "premis_bukti",
                    "premis_sumber",
                    "analisis",
                    "putusan",
                    "alasan",
                    "keyakinan",
                ],
            },
        },
    },
    "required": ["claims"],
}


def _format_verdict(data: dict[str, Any]) -> str:
    parts: list[str] = []
    for i, c in enumerate(data.get("claims", []), 1):
        parts.append(
            f"KLAIM_{i}: {c.get('claim', '')}\n"
            f"  PREMIS_FAKTA:   {c.get('premis_fakta', '')}\n"
            f"  PREMIS_BUKTI:   {c.get('premis_bukti', '')}\n"
            f"  PREMIS_SUMBER:  {c.get('premis_sumber', '')}\n"
            f"  ANALISIS:       {c.get('analisis', '')}\n"
            f"  PUTUSAN:        {c.get('putusan', '')}\n"
            f"  ALASAN:         {c.get('alasan', '')}\n"
            f"  KEYAKINAN:      {c.get('keyakinan', '')}"
        )
    return "\n\n".join(parts)


class VerdictPredictionAgent:
    def __init__(self, llm: BaseLLMAdapter, cache: VerdictCache | None = None):
        self.llm = llm
        self._cache = cache

    @with_retry(max_attempts=3)
    @with_budget(max_tokens=4000)
    async def run(self, state: ArticleState) -> ArticleState:
        logger.info("[VerdictPrediction] mulai — article_id=%s", state["article_id"])

        report = state.get("fact_check_report", {})
        claims = report.get("claims", "")
        evidence = report.get("evidence", "")

        claim_list = [c.strip() for c in claims.split("\n") if c.strip()]

        cached_parts: list[str] = []
        uncached_claims: list[str] = []

        if self._cache:
            for claim in claim_list:
                cached = await self._cache.get(claim)
                if cached and cached.get("verdict"):
                    cached_parts.append(f"Klaim: {claim}\nPutusan (dari cache): {cached['verdict']}")
                    logger.info("[VerdictPrediction] cache hit: %.60s...", claim)
                else:
                    uncached_claims.append(claim)
        else:
            uncached_claims = claim_list

        verdict_text = ""
        verdict_raw: list[dict[str, Any]] = []

        if uncached_claims:
            try:
                user_prompt = (
                    "Klaim:\n"
                    + "\n".join(uncached_claims)
                    + f"\n\nBukti:\n{evidence}\n\nBerikan putusan untuk setiap klaim."
                )
                result = await self.llm.complete_structured(
                    system=self._system_prompt(),
                    prompt=PromptHardener.wrap_user_input(user_prompt),
                    schema=VERDICT_SCHEMA,
                    max_tokens=4096,
                )
                verdict_text = _format_verdict(result)
                verdict_raw = result.get("claims", [])

                if self._cache:
                    for claim in uncached_claims:
                        await self._cache.set(claim, verdict_text, evidence, 0.5)
            except Exception as e:
                logger.error("[VerdictPrediction] gagal: %s", e)
                verdict_text = ""
                verdict_raw = []

        if cached_parts:
            if verdict_text:
                combined = "\n\n".join(cached_parts)
                verdict_text = f"--- HASIL DARI CACHE ---\n{combined}\n\n--- HASIL BARU ---\n{verdict_text}"
            else:
                verdict_text = "\n\n".join(cached_parts)

        fact_check = cast(FactCheckReport, {**report, "verdict": verdict_text, "verdict_raw": verdict_raw})

        return {
            **state,
            "fact_check_report": fact_check,
            "events": state["events"]
            + [make_event("VerdictPrediction", "predict_verdict", f"{len(verdict_text)} chars")],
        }

    def _system_prompt(self) -> str:
        return PromptHardener.SYSTEM_GUARD + "\n\n" + load_prompt("fact_check/verdict_prediction.md")
