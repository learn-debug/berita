from __future__ import annotations

import json
import logging
from typing import Any

from newsagent.memory.engine import get_engine

logger = logging.getLogger(__name__)


class KnowledgeGraphRepository:
    async def upsert_entity(
        self,
        name: str,
        type: str = "concept",
        description: str = "",
        embedding: list[float] | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        engine = await get_engine()
        row = await engine.fetchrow(
            """
            INSERT INTO knowledge_entities (name, type, description, embedding, metadata)
            VALUES ($1, $2, $3, $4::vector, $5::jsonb)
            ON CONFLICT (name, type) DO UPDATE SET
                description = EXCLUDED.description,
                embedding = CASE WHEN EXCLUDED.embedding IS NOT NULL
                    THEN EXCLUDED.embedding ELSE knowledge_entities.embedding END,
                metadata = knowledge_entities.metadata || EXCLUDED.metadata
            RETURNING *
            """,
            name,
            type,
            description,
            embedding,
            json.dumps(metadata or {}),
        )
        return dict(row) if row else {}

    async def get_entity(self, entity_id: str) -> dict[str, Any] | None:
        engine = await get_engine()
        row = await engine.fetchrow("SELECT * FROM knowledge_entities WHERE id = $1", entity_id)
        return dict(row) if row else None

    async def get_entity_by_name(self, name: str, type: str = "") -> dict[str, Any] | None:
        engine = await get_engine()
        if type:
            row = await engine.fetchrow(
                "SELECT * FROM knowledge_entities WHERE name = $1 AND type = $2",
                name,
                type,
            )
        else:
            row = await engine.fetchrow("SELECT * FROM knowledge_entities WHERE name = $1", name)
        return dict(row) if row else None

    async def search_entities_by_vector(
        self,
        query_embedding: list[float],
        limit: int = 20,
        type_filter: str | None = None,
    ) -> list[dict[str, Any]]:
        engine = await get_engine()
        if type_filter:
            rows = await engine.fetch(
                """
                SELECT *, (embedding <=> $1::vector) AS distance
                FROM knowledge_entities
                WHERE type = $2 AND embedding IS NOT NULL
                ORDER BY embedding <=> $1::vector
                LIMIT $3
                """,
                query_embedding,
                type_filter,
                limit,
            )
        else:
            rows = await engine.fetch(
                """
                SELECT *, (embedding <=> $1::vector) AS distance
                FROM knowledge_entities
                WHERE embedding IS NOT NULL
                ORDER BY embedding <=> $1::vector
                LIMIT $2
                """,
                query_embedding,
                limit,
            )
        return [dict(r) for r in rows]

    async def search_entities_by_text(
        self,
        query: str,
        limit: int = 20,
        type_filter: str | None = None,
    ) -> list[dict[str, Any]]:
        engine = await get_engine()
        if type_filter:
            rows = await engine.fetch(
                """
                SELECT *, similarity(name, $1) AS score
                FROM knowledge_entities
                WHERE type = $2 AND name % $1
                ORDER BY score DESC
                LIMIT $3
                """,
                query,
                type_filter,
                limit,
            )
        else:
            rows = await engine.fetch(
                """
                SELECT *, similarity(name, $1) AS score
                FROM knowledge_entities
                WHERE name % $1
                ORDER BY score DESC
                LIMIT $2
                """,
                query,
                limit,
            )
        return [dict(r) for r in rows]

    async def upsert_relationship(
        self,
        source_id: str,
        target_id: str,
        relation_type: str,
        weight: float = 1.0,
        metadata: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        engine = await get_engine()
        row = await engine.fetchrow(
            """
            INSERT INTO knowledge_relationships (source_id, target_id, relation_type, weight, metadata)
            VALUES ($1, $2, $3, $4, $5::jsonb)
            ON CONFLICT (source_id, target_id, relation_type) DO UPDATE SET
                weight = EXCLUDED.weight,
                metadata = knowledge_relationships.metadata || EXCLUDED.metadata
            RETURNING *
            """,
            source_id,
            target_id,
            relation_type,
            weight,
            json.dumps(metadata or {}),
        )
        return dict(row) if row else {}

    async def get_relationships(
        self,
        entity_id: str,
        relation_type: str | None = None,
        direction: str = "forward",
    ) -> list[dict[str, Any]]:
        engine = await get_engine()
        if direction == "forward":
            if relation_type:
                rows = await engine.fetch(
                    """
                    SELECT r.*, e.name AS target_name, e.type AS target_type
                    FROM knowledge_relationships r
                    JOIN knowledge_entities e ON e.id = r.target_id
                    WHERE r.source_id = $1 AND r.relation_type = $2
                    ORDER BY r.weight DESC, r.created_at DESC
                    """,
                    entity_id,
                    relation_type,
                )
            else:
                rows = await engine.fetch(
                    """
                    SELECT r.*, e.name AS target_name, e.type AS target_type
                    FROM knowledge_relationships r
                    JOIN knowledge_entities e ON e.id = r.target_id
                    WHERE r.source_id = $1
                    ORDER BY r.weight DESC, r.created_at DESC
                    """,
                    entity_id,
                )
        elif direction == "reverse":
            if relation_type:
                rows = await engine.fetch(
                    """
                    SELECT r.*, e.name AS source_name, e.type AS source_type
                    FROM knowledge_relationships r
                    JOIN knowledge_entities e ON e.id = r.source_id
                    WHERE r.target_id = $1 AND r.relation_type = $2
                    ORDER BY r.weight DESC, r.created_at DESC
                    """,
                    entity_id,
                    relation_type,
                )
            else:
                rows = await engine.fetch(
                    """
                    SELECT r.*, e.name AS source_name, e.type AS source_type
                    FROM knowledge_relationships r
                    JOIN knowledge_entities e ON e.id = r.source_id
                    WHERE r.target_id = $1
                    ORDER BY r.weight DESC, r.created_at DESC
                    """,
                    entity_id,
                )
        else:
            rows = await engine.fetch(
                """
                SELECT r.*,
                    e_src.name AS source_name, e_src.type AS source_type,
                    e_tgt.name AS target_name, e_tgt.type AS target_type
                FROM knowledge_relationships r
                JOIN knowledge_entities e_src ON e_src.id = r.source_id
                JOIN knowledge_entities e_tgt ON e_tgt.id = r.target_id
                WHERE r.source_id = $1 OR r.target_id = $1
                ORDER BY r.weight DESC, r.created_at DESC
                """,
                entity_id,
            )
        return [dict(r) for r in rows]

    async def traverse(
        self,
        start_entity_id: str,
        max_depth: int = 2,
        relation_types: list[str] | None = None,
        direction: str = "forward",
    ) -> list[dict[str, Any]]:
        engine = await get_engine()
        if relation_types:
            rows = await engine.fetch(
                """
                WITH RECURSIVE graph_walk AS (
                    SELECT id, name, type, 0 AS depth, ARRAY[id] AS path
                    FROM knowledge_entities WHERE id = $1

                    UNION

                    SELECT e.id, e.name, e.type, gw.depth + 1, gw.path || e.id
                    FROM graph_walk gw
                    JOIN knowledge_relationships r ON
                        ($4 = 'forward' AND r.source_id = gw.id)
                        OR ($4 = 'reverse' AND r.target_id = gw.id)
                        OR ($4 = 'both' AND (r.source_id = gw.id OR r.target_id = gw.id))
                    JOIN knowledge_entities e ON e.id = CASE
                        WHEN $4 = 'forward' THEN r.target_id
                        WHEN $4 = 'reverse' THEN r.source_id
                        ELSE CASE WHEN r.source_id = gw.id THEN r.target_id ELSE r.source_id END
                    END
                    WHERE gw.depth < $2
                        AND r.relation_type = ANY($3::text[])
                        AND NOT (e.id = ANY(gw.path))
                )
                SELECT DISTINCT ON (id) id, name, type, MIN(depth) AS depth
                FROM graph_walk
                GROUP BY id, name, type
                ORDER BY depth, name
                """,
                start_entity_id,
                max_depth,
                relation_types,
                direction,
            )
        else:
            rows = await engine.fetch(
                """
                WITH RECURSIVE graph_walk AS (
                    SELECT id, name, type, 0 AS depth, ARRAY[id] AS path
                    FROM knowledge_entities WHERE id = $1

                    UNION

                    SELECT e.id, e.name, e.type, gw.depth + 1, gw.path || e.id
                    FROM graph_walk gw
                    JOIN knowledge_relationships r ON
                        ($3 = 'forward' AND r.source_id = gw.id)
                        OR ($3 = 'reverse' AND r.target_id = gw.id)
                        OR ($3 = 'both' AND (r.source_id = gw.id OR r.target_id = gw.id))
                    JOIN knowledge_entities e ON e.id = CASE
                        WHEN $3 = 'forward' THEN r.target_id
                        WHEN $3 = 'reverse' THEN r.source_id
                        ELSE CASE WHEN r.source_id = gw.id THEN r.target_id ELSE r.source_id END
                    END
                    WHERE gw.depth < $2
                        AND NOT (e.id = ANY(gw.path))
                )
                SELECT DISTINCT ON (id) id, name, type, MIN(depth) AS depth
                FROM graph_walk
                GROUP BY id, name, type
                ORDER BY depth, name
                """,
                start_entity_id,
                max_depth,
                direction,
            )
        return [dict(r) for r in rows]

    async def link_article_entity(
        self,
        article_id: str,
        entity_id: str,
        context: str = "",
    ) -> dict[str, Any]:
        engine = await get_engine()
        row = await engine.fetchrow(
            """
            INSERT INTO article_entities (article_id, entity_id, mention_count, context)
            VALUES ($1, $2, 1, $3)
            ON CONFLICT (article_id, entity_id) DO UPDATE SET
                mention_count = article_entities.mention_count + 1,
                context = CASE WHEN $3 <> ''
                    THEN $3 ELSE article_entities.context END
            RETURNING *
            """,
            article_id,
            entity_id,
            context,
        )
        return dict(row) if row else {}

    async def get_article_entities(self, article_id: str) -> list[dict[str, Any]]:
        engine = await get_engine()
        rows = await engine.fetch(
            """
            SELECT e.*, ae.mention_count, ae.context
            FROM article_entities ae
            JOIN knowledge_entities e ON e.id = ae.entity_id
            WHERE ae.article_id = $1
            ORDER BY ae.mention_count DESC
            """,
            article_id,
        )
        return [dict(r) for r in rows]

    async def get_entity_articles(self, entity_id: str) -> list[dict[str, Any]]:
        engine = await get_engine()
        rows = await engine.fetch(
            """
            SELECT a.id, a.title, a.status, a.credibility_score, a.created_at,
                   ae.mention_count, ae.context
            FROM article_entities ae
            JOIN articles a ON a.id = ae.article_id
            WHERE ae.entity_id = $1
            ORDER BY a.created_at DESC
            """,
            entity_id,
        )
        return [dict(r) for r in rows]

    async def stats(self) -> dict[str, Any]:
        engine = await get_engine()
        entities = await engine.fetchval("SELECT COUNT(*) FROM knowledge_entities") or 0
        relationships = await engine.fetchval("SELECT COUNT(*) FROM knowledge_relationships") or 0
        linked = await engine.fetchval("SELECT COUNT(*) FROM article_entities") or 0
        entity_types = await engine.fetch(
            "SELECT type, COUNT(*) AS count FROM knowledge_entities GROUP BY type ORDER BY count DESC"
        )
        return {
            "total_entities": entities,
            "total_relationships": relationships,
            "total_article_links": linked,
            "entity_types": [dict(r) for r in entity_types],
        }
