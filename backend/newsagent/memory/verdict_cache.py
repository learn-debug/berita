import json
import logging
from typing import Any

from newsagent.memory.engine import get_engine

logger = logging.getLogger(__name__)


class VerdictCache:
    async def ensure_table(self) -> None:
        engine = await get_engine()
        await engine.execute("""
            CREATE TABLE IF NOT EXISTS verdict_cache (
                id SERIAL PRIMARY KEY,
                claim_hash TEXT UNIQUE NOT NULL,
                claim_text TEXT NOT NULL,
                verdict TEXT NOT NULL,
                evidence TEXT DEFAULT '',
                trust_score REAL DEFAULT 0.0,
                created_at TIMESTAMPTZ DEFAULT NOW(),
                accessed_at TIMESTAMPTZ DEFAULT NOW()
            )
        """)
        await engine.execute("""
            CREATE INDEX IF NOT EXISTS idx_verdict_hash ON verdict_cache (claim_hash)
        """)

    async def get(self, claim_text: str) -> dict[str, Any] | None:
        import hashlib
        claim_hash = hashlib.sha256(claim_text.encode()).hexdigest()[:32]
        engine = await get_engine()
        row = await engine.fetchrow(
            "SELECT * FROM verdict_cache WHERE claim_hash = $1", claim_hash
        )
        if row:
            await engine.execute(
                "UPDATE verdict_cache SET accessed_at = NOW() WHERE claim_hash = $1",
                claim_hash,
            )
            return dict(row)
        return None

    async def set(
        self, claim_text: str, verdict: str, evidence: str = "", trust_score: float = 0.0
    ) -> None:
        import hashlib
        claim_hash = hashlib.sha256(claim_text.encode()).hexdigest()[:32]
        await self.ensure_table()
        engine = await get_engine()
        await engine.execute(
            """
            INSERT INTO verdict_cache (claim_hash, claim_text, verdict, evidence, trust_score)
            VALUES ($1, $2, $3, $4, $5)
            ON CONFLICT (claim_hash) DO UPDATE SET
                verdict = EXCLUDED.verdict,
                evidence = EXCLUDED.evidence,
                trust_score = EXCLUDED.trust_score,
                accessed_at = NOW()
            """,
            claim_hash,
            claim_text,
            verdict,
            evidence,
            trust_score,
        )

    async def stats(self) -> dict[str, Any]:
        await self.ensure_table()
        engine = await get_engine()
        total = await engine.fetchval("SELECT COUNT(*) FROM verdict_cache")
        return {"total_cached_verdicts": total}
