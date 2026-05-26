-- ============================================================================
-- NewsAgent Database Schema
-- PostgreSQL 17 + pgvector
-- Naming convention: snake_case, plural tables, singular FK columns
-- ============================================================================

BEGIN;

-- ============================================================================
-- EXTENSIONS
-- ============================================================================
CREATE EXTENSION IF NOT EXISTS vector;
CREATE EXTENSION IF NOT EXISTS pgcrypto;
CREATE EXTENSION IF NOT EXISTS pg_trgm;

-- ============================================================================
-- ENUMS
-- ============================================================================
DO $$ BEGIN
    CREATE TYPE article_input_type AS ENUM ('topic', 'draft', 'url');
EXCEPTION
    WHEN duplicate_object THEN NULL;
END $$;

DO $$ BEGIN
    CREATE TYPE article_status AS ENUM (
        'pending', 'processing', 'review', 'revision',
        'approved', 'rejected', 'published', 'failed'
    );
EXCEPTION
    WHEN duplicate_object THEN NULL;
END $$;

DO $$ BEGIN
    CREATE TYPE source_type AS ENUM ('rss', 'website', 'api', 'manual');
EXCEPTION
    WHEN duplicate_object THEN NULL;
END $$;

-- ============================================================================
-- TABLE: users
-- Owner dan Editor accounts
-- ============================================================================
CREATE TABLE IF NOT EXISTS users (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email           TEXT UNIQUE NOT NULL,
    password_hash   TEXT NOT NULL,
    name            TEXT NOT NULL DEFAULT '',
    role            TEXT NOT NULL DEFAULT 'editor' CHECK (role IN ('owner', 'editor')),
    is_active       BOOLEAN NOT NULL DEFAULT TRUE,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

COMMENT ON TABLE users IS 'User accounts: owner (super admin) and editors';

-- ============================================================================
-- TABLE: sources
-- News sources untuk auto-ingestion (RSS, website, API)
-- ============================================================================
CREATE TABLE IF NOT EXISTS sources (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name            TEXT NOT NULL,
    url             TEXT NOT NULL,
    type            source_type NOT NULL DEFAULT 'rss',
    category        TEXT NOT NULL DEFAULT 'general',
    is_active       BOOLEAN NOT NULL DEFAULT TRUE,
    metadata        JSONB NOT NULL DEFAULT '{}'::jsonb,
    last_scraped_at TIMESTAMPTZ,
    article_count   INTEGER NOT NULL DEFAULT 0 CHECK (article_count >= 0),
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

COMMENT ON TABLE sources IS 'News sources registered for content ingestion and tracking';
COMMENT ON COLUMN sources.type IS 'Source type: rss (feed), website (scrape), api (API endpoint), manual (manual submit)';
COMMENT ON COLUMN sources.is_active IS 'Whether this source is actively being monitored for new content';
COMMENT ON COLUMN sources.last_scraped_at IS 'Last successful content pull timestamp';
COMMENT ON COLUMN sources.article_count IS 'Total number of articles ingested from this source';

-- ============================================================================
-- TABLE: articles
-- Main article storage (replaces in-memory ArticleStore)
-- ============================================================================
CREATE TABLE IF NOT EXISTS articles (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    article_id_str      TEXT UNIQUE,
    input_type          article_input_type NOT NULL,
    raw_input           TEXT NOT NULL,
    title               TEXT,
    rag_context         TEXT,
    draft               TEXT,
    fact_check_report   JSONB NOT NULL DEFAULT '{}'::jsonb,
    edited_draft        TEXT,
    aggregated_article  TEXT,
    credibility_score   REAL NOT NULL DEFAULT 0.0
                        CHECK (credibility_score >= 0.0 AND credibility_score <= 1.0),
    status              article_status NOT NULL DEFAULT 'pending',
    revision_count      INTEGER NOT NULL DEFAULT 0
                        CHECK (revision_count >= 0),
    published_title     TEXT,
    published_body      TEXT,
    published_url       TEXT,
    source_id           UUID REFERENCES sources(id) ON DELETE SET NULL,
    source_url          TEXT,
    created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at          TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

COMMENT ON TABLE articles IS 'Main article storage for the news production pipeline';
COMMENT ON COLUMN articles.input_type IS 'Source type: topic (generate), draft (edit), url (scrape)';
COMMENT ON COLUMN articles.status IS 'Current lifecycle state in the article state machine';
COMMENT ON COLUMN articles.source_id IS 'Reference to the news source this article was scraped from';
COMMENT ON COLUMN articles.source_url IS 'Original URL of the article if scraped from web';
COMMENT ON COLUMN articles.revision_count IS 'Number of revision cycles (max 2)';
COMMENT ON COLUMN articles.credibility_score IS 'Overall credibility score 0.0–1.0 from Quality Gate';
COMMENT ON COLUMN articles.fact_check_report IS 'Structured JSON: claims, queries, evidence, verdict';
COMMENT ON COLUMN articles.published_url IS 'CMS URL after successful publication';

-- ============================================================================
-- TABLE: article_events
-- State machine audit trail (event sourcing log)
-- ============================================================================
CREATE TABLE IF NOT EXISTS article_events (
    id          BIGSERIAL PRIMARY KEY,
    article_id  UUID NOT NULL REFERENCES articles(id) ON DELETE CASCADE,
    agent       VARCHAR(50) NOT NULL DEFAULT 'system',
    action      VARCHAR(50) NOT NULL,
    detail      TEXT,
    metadata    JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

COMMENT ON TABLE article_events IS 'Immutable event log for article state machine transitions';
COMMENT ON COLUMN article_events.agent IS 'Agent or system component that produced the event';
COMMENT ON COLUMN article_events.action IS 'Event type (pipeline_start, agent_complete, status_change, etc)';

-- ============================================================================
-- TABLE: draft_memory
-- Persistent draft storage with embeddings for few-shot retrieval
-- ============================================================================
CREATE TABLE IF NOT EXISTS draft_memory (
    id                SERIAL PRIMARY KEY,
    topic             TEXT NOT NULL,
    draft             TEXT NOT NULL,
    credibility_score REAL NOT NULL DEFAULT 0.0
                      CHECK (credibility_score >= 0.0 AND credibility_score <= 1.0),
    feedback          TEXT NOT NULL DEFAULT '',
    embedding         vector(384),
    created_at        TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at        TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

COMMENT ON TABLE draft_memory IS 'Cache of high-quality drafts for few-shot learning in DraftAgent';
COMMENT ON COLUMN draft_memory.embedding IS 'pgvector embedding (384-dim) for semantic similarity search';

-- ============================================================================
-- TABLE: verdict_cache
-- Fact-check result cache, keyed by SHA-256 claim hash
-- ============================================================================
CREATE TABLE IF NOT EXISTS verdict_cache (
    id          SERIAL PRIMARY KEY,
    claim_hash  VARCHAR(64) NOT NULL,
    claim_text  TEXT NOT NULL,
    verdict     TEXT NOT NULL,
    evidence    TEXT NOT NULL DEFAULT '',
    trust_score REAL NOT NULL DEFAULT 0.0
                CHECK (trust_score >= 0.0 AND trust_score <= 1.0),
    created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    accessed_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

COMMENT ON TABLE verdict_cache IS 'Cache of fact-check verdicts keyed by SHA-256 claim hash';
COMMENT ON COLUMN verdict_cache.claim_hash IS 'First 32 hex chars of SHA-256(claim_text)';

-- ============================================================================
-- TABLE: knowledge_entities
-- GraphRAG nodes — entities extracted from articles (people, orgs, etc.)
-- ============================================================================
CREATE TABLE IF NOT EXISTS knowledge_entities (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name        TEXT NOT NULL,
    type        VARCHAR(50) NOT NULL DEFAULT 'concept',
    description TEXT,
    embedding   vector(384),
    metadata    JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at  TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

COMMENT ON TABLE knowledge_entities IS 'Knowledge graph nodes for GraphRAG — entities extracted from article content';
COMMENT ON COLUMN knowledge_entities.type IS 'Entity type: person, organization, location, concept, event, date, etc';
COMMENT ON COLUMN knowledge_entities.embedding IS 'pgvector embedding (384-dim) for semantic entity search';

-- ============================================================================
-- TABLE: knowledge_relationships
-- GraphRAG edges — typed connections between entities
-- ============================================================================
CREATE TABLE IF NOT EXISTS knowledge_relationships (
    id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    source_id     UUID NOT NULL REFERENCES knowledge_entities(id) ON DELETE CASCADE,
    target_id     UUID NOT NULL REFERENCES knowledge_entities(id) ON DELETE CASCADE,
    relation_type VARCHAR(100) NOT NULL,
    weight        REAL NOT NULL DEFAULT 1.0
                  CHECK (weight >= 0.0 AND weight <= 1.0),
    metadata      JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at    TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

COMMENT ON TABLE knowledge_relationships IS 'Knowledge graph edges — typed directional relationships between entities';
COMMENT ON COLUMN knowledge_relationships.relation_type IS 'Relation label: works_at, located_in, part_of, founded_by, etc';
COMMENT ON COLUMN knowledge_relationships.weight IS 'Relationship strength 0.0–1.0 (confidence, frequency, or relevance)';

-- ============================================================================
-- TABLE: article_entities
-- Junction: which entities appear in which articles
-- ============================================================================
CREATE TABLE IF NOT EXISTS article_entities (
    article_id    UUID NOT NULL REFERENCES articles(id) ON DELETE CASCADE,
    entity_id     UUID NOT NULL REFERENCES knowledge_entities(id) ON DELETE CASCADE,
    mention_count INTEGER NOT NULL DEFAULT 1
                  CHECK (mention_count > 0),
    context       TEXT,
    created_at    TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    PRIMARY KEY (article_id, entity_id)
);

COMMENT ON TABLE article_entities IS 'Links articles to entities mentioned within them for traceability';
COMMENT ON COLUMN article_entities.mention_count IS 'Number of times the entity appears in the article';
COMMENT ON COLUMN article_entities.context IS 'First/relevant snippet of text where entity was mentioned';


-- ============================================================================
-- INDEXES
-- ============================================================================

-- articles
CREATE INDEX IF NOT EXISTS idx_articles_status
    ON articles (status);
CREATE INDEX IF NOT EXISTS idx_articles_created_at
    ON articles (created_at DESC);
CREATE INDEX IF NOT EXISTS idx_articles_credibility_score
    ON articles (credibility_score DESC);

-- article_events
CREATE INDEX IF NOT EXISTS idx_article_events_lookup
    ON article_events (article_id, created_at DESC);

-- draft_memory
CREATE INDEX IF NOT EXISTS idx_draft_memory_topic
    ON draft_memory (topic);
CREATE INDEX IF NOT EXISTS idx_draft_memory_credibility_score
    ON draft_memory (credibility_score DESC);

-- verdict_cache
CREATE UNIQUE INDEX IF NOT EXISTS uq_verdict_cache_claim_hash
    ON verdict_cache (claim_hash);

-- knowledge_entities
CREATE UNIQUE INDEX IF NOT EXISTS uq_knowledge_entity_name_type
    ON knowledge_entities (name, type);
CREATE INDEX IF NOT EXISTS idx_knowledge_entity_type
    ON knowledge_entities (type);
CREATE INDEX IF NOT EXISTS idx_knowledge_entity_embedding
    ON knowledge_entities USING hnsw (embedding vector_cosine_ops) WITH (m = 16, ef_construction = 64);
CREATE INDEX IF NOT EXISTS idx_knowledge_entity_name_trgm
    ON knowledge_entities USING gin (name gin_trgm_ops);
CREATE INDEX IF NOT EXISTS idx_knowledge_entity_metadata
    ON knowledge_entities USING gin (metadata);

-- knowledge_relationships
CREATE UNIQUE INDEX IF NOT EXISTS uq_knowledge_relationship
    ON knowledge_relationships (source_id, target_id, relation_type);
CREATE INDEX IF NOT EXISTS idx_knowledge_rel_source
    ON knowledge_relationships (source_id, relation_type);
CREATE INDEX IF NOT EXISTS idx_knowledge_rel_target
    ON knowledge_relationships (target_id, relation_type);
CREATE INDEX IF NOT EXISTS idx_knowledge_rel_metadata
    ON knowledge_relationships USING gin (metadata);

-- article_entities
CREATE INDEX IF NOT EXISTS idx_article_entities_article
    ON article_entities (article_id);
CREATE INDEX IF NOT EXISTS idx_article_entities_entity
    ON article_entities (entity_id);

-- ============================================================================
-- TRIGGERS: auto-update updated_at
-- ============================================================================
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_articles_updated_at ON articles;
CREATE TRIGGER trg_articles_updated_at
    BEFORE UPDATE ON articles
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS trg_draft_memory_updated_at ON draft_memory;
CREATE TRIGGER trg_draft_memory_updated_at
    BEFORE UPDATE ON draft_memory
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS trg_knowledge_entities_updated_at ON knowledge_entities;
CREATE TRIGGER trg_knowledge_entities_updated_at
    BEFORE UPDATE ON knowledge_entities
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

COMMIT;
