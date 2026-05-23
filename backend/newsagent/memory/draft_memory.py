import logging
from typing import Any

from newsagent.memory.engine import get_engine

logger = logging.getLogger(__name__)


class DraftMemory:
    def __init__(self) -> None:
        self._ready = False

    async def _ensure(self) -> None:
        if self._ready:
            return
        engine = await get_engine()
        await engine.execute("""
            CREATE TABLE IF NOT EXISTS draft_memory (
                id SERIAL PRIMARY KEY,
                topic TEXT NOT NULL,
                draft TEXT NOT NULL,
                credibility_score REAL DEFAULT 0.0,
                feedback TEXT DEFAULT '',
                embedding vector(384),
                created_at TIMESTAMPTZ DEFAULT NOW()
            )
        """)
        await engine.execute("""
            CREATE INDEX IF NOT EXISTS idx_draft_topic ON draft_memory (topic)
        """)
        self._ready = True

    async def save(
        self,
        topic: str,
        draft: str,
        credibility_score: float = 0.0,
        feedback: str = "",
    ) -> None:
        await self._ensure()
        engine = await get_engine()
        await engine.execute(
            """
            INSERT INTO draft_memory (topic, draft, credibility_score, feedback)
            VALUES ($1, $2, $3, $4)
            """,
            topic,
            draft,
            credibility_score,
            feedback,
        )

    async def find_best(self, topic: str, limit: int = 3) -> list[dict[str, Any]]:
        await self._ensure()
        engine = await get_engine()
        words = [w for w in topic.lower().split() if len(w) > 2]
        if not words:
            return []

        conditions = " OR ".join(f"topic ILIKE '%' || ${i + 1} || '%'" for i in range(len(words)))
        query = f"""
            SELECT topic, draft, credibility_score, feedback, created_at
            FROM draft_memory
            WHERE ({conditions})
            ORDER BY credibility_score DESC, created_at DESC
            LIMIT ${len(words) + 1}
        """
        rows = await engine.fetch(query, *words, limit)
        return [dict(r) for r in rows]

    async def find_high_score(self, min_score: float = 0.75, limit: int = 5) -> list[dict[str, Any]]:
        await self._ensure()
        engine = await get_engine()
        rows = await engine.fetch(
            """
            SELECT topic, draft, credibility_score, feedback, created_at
            FROM draft_memory
            WHERE credibility_score >= $1
            ORDER BY credibility_score DESC, created_at DESC
            LIMIT $2
            """,
            min_score,
            limit,
        )
        return [dict(r) for r in rows]

    async def stats(self) -> dict[str, Any]:
        await self._ensure()
        engine = await get_engine()
        total = await engine.fetchval("SELECT COUNT(*) FROM draft_memory")
        avg_score = await engine.fetchval(
            "SELECT COALESCE(AVG(credibility_score), 0) FROM draft_memory WHERE credibility_score > 0"
        )
        return {"total_drafts": total, "avg_credibility_score": round(float(avg_score), 3)}
