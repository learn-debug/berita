import pytest

from newsagent.api.store import ArticleStore
from newsagent.core.state import ArticleState, ArticleStatus


@pytest.mark.asyncio
async def test_claim_and_release() -> None:
    store = ArticleStore()
    assert await store.claim_for_processing("art-1", 0)
    await store.release_claim("art-1", 0)
    assert await store.claim_for_processing("art-1", 0)


@pytest.mark.asyncio
async def test_claim_prevents_duplicate() -> None:
    store = ArticleStore()
    assert await store.claim_for_processing("art-1", 0)
    assert not await store.claim_for_processing("art-1", 0)


@pytest.mark.asyncio
async def test_claim_allows_different_revision() -> None:
    store = ArticleStore()
    assert await store.claim_for_processing("art-1", 0)
    assert await store.claim_for_processing("art-1", 1)


@pytest.mark.asyncio
async def test_claim_rejects_published_article() -> None:
    store = ArticleStore()
    state: ArticleState = {
        "article_id": "art-1",
        "input_type": "topic",
        "raw_input": "test",
        "rag_context": "",
        "draft": "",
        "fact_check_report": {},
        "edited_draft": "",
        "aggregated_article": "",
        "credibility_score": 0.85,
        "status": ArticleStatus.PUBLISHED.value,
        "revision_count": 0,
        "events": [],
    }
    await store.save("art-1", state)
    assert not await store.claim_for_processing("art-1", 0)


@pytest.mark.asyncio
async def test_claim_rejects_rejected_article() -> None:
    store = ArticleStore()
    state: ArticleState = {
        "article_id": "art-1",
        "input_type": "topic",
        "raw_input": "test",
        "rag_context": "",
        "draft": "",
        "fact_check_report": {},
        "edited_draft": "",
        "aggregated_article": "",
        "credibility_score": 0.0,
        "status": ArticleStatus.REJECTED.value,
        "revision_count": 0,
        "events": [],
    }
    await store.save("art-1", state)
    assert not await store.claim_for_processing("art-1", 0)


@pytest.mark.asyncio
async def test_claim_rejects_already_processing() -> None:
    store = ArticleStore()
    state: ArticleState = {
        "article_id": "art-1",
        "input_type": "topic",
        "raw_input": "test",
        "rag_context": "",
        "draft": "",
        "fact_check_report": {},
        "edited_draft": "",
        "aggregated_article": "",
        "credibility_score": 0.0,
        "status": ArticleStatus.PROCESSING.value,
        "revision_count": 0,
        "events": [],
    }
    await store.save("art-1", state)
    assert not await store.claim_for_processing("art-1", 0)


@pytest.mark.asyncio
async def test_claim_allows_failed_article_retry() -> None:
    store = ArticleStore()
    state: ArticleState = {
        "article_id": "art-1",
        "input_type": "topic",
        "raw_input": "test",
        "rag_context": "",
        "draft": "",
        "fact_check_report": {},
        "edited_draft": "",
        "aggregated_article": "",
        "credibility_score": 0.0,
        "status": ArticleStatus.FAILED.value,
        "revision_count": 0,
        "events": [],
    }
    await store.save("art-1", state)
    assert await store.claim_for_processing("art-1", 0)


@pytest.mark.asyncio
async def test_claim_allows_review_article_retry() -> None:
    store = ArticleStore()
    state: ArticleState = {
        "article_id": "art-1",
        "input_type": "topic",
        "raw_input": "test",
        "rag_context": "",
        "draft": "",
        "fact_check_report": {},
        "edited_draft": "",
        "aggregated_article": "",
        "credibility_score": 0.0,
        "status": ArticleStatus.REVIEW.value,
        "revision_count": 0,
        "events": [],
    }
    await store.save("art-1", state)
    assert await store.claim_for_processing("art-1", 0)


@pytest.mark.asyncio
async def test_reset_stale_processing() -> None:
    store = ArticleStore()
    state: ArticleState = {
        "article_id": "art-1",
        "input_type": "topic",
        "raw_input": "test",
        "rag_context": "",
        "draft": "",
        "fact_check_report": {},
        "edited_draft": "",
        "aggregated_article": "",
        "credibility_score": 0.0,
        "status": ArticleStatus.PROCESSING.value,
        "revision_count": 0,
        "events": [],
    }
    await store.save("art-1", state)
    count = await store.reset_stale_processing()
    assert count == 1
    article = await store.get("art-1")
    assert article is not None
    assert article["status"] == ArticleStatus.FAILED.value


@pytest.mark.asyncio
async def test_reset_stale_skips_non_processing() -> None:
    store = ArticleStore()
    for st in (ArticleStatus.PUBLISHED, ArticleStatus.FAILED, ArticleStatus.REVIEW, ArticleStatus.REJECTED):
        state: ArticleState = {
            "article_id": f"art-{st.value}",
            "input_type": "topic",
            "raw_input": "test",
            "rag_context": "",
            "draft": "",
            "fact_check_report": {},
            "edited_draft": "",
            "aggregated_article": "",
            "credibility_score": 0.0,
            "status": st.value,
            "revision_count": 0,
            "events": [],
        }
        await store.save(f"art-{st.value}", state)
    count = await store.reset_stale_processing()
    assert count == 0


@pytest.mark.asyncio
async def test_save_and_get() -> None:
    store = ArticleStore()
    state: ArticleState = {
        "article_id": "art-1",
        "input_type": "topic",
        "raw_input": "test",
        "rag_context": "",
        "draft": "",
        "fact_check_report": {},
        "edited_draft": "",
        "aggregated_article": "",
        "credibility_score": 0.0,
        "status": ArticleStatus.PROCESSING.value,
        "revision_count": 0,
        "events": [],
    }
    await store.save("art-1", state)
    article = await store.get("art-1")
    assert article is not None
    assert article["article_id"] == "art-1"
    assert article["status"] == ArticleStatus.PROCESSING.value
    assert "created_at" in article
    assert "updated_at" in article


@pytest.mark.asyncio
async def test_delete() -> None:
    store = ArticleStore()
    state: ArticleState = {
        "article_id": "art-1",
        "input_type": "topic",
        "raw_input": "test",
        "rag_context": "",
        "draft": "",
        "fact_check_report": {},
        "edited_draft": "",
        "aggregated_article": "",
        "credibility_score": 0.0,
        "status": ArticleStatus.PROCESSING.value,
        "revision_count": 0,
        "events": [],
    }
    await store.save("art-1", state)
    assert await store.delete("art-1")
    assert await store.get("art-1") is None
    assert not await store.delete("art-1")


@pytest.mark.asyncio
async def test_list_with_status_filter() -> None:
    store = ArticleStore()
    for i in range(3):
        state: ArticleState = {
            "article_id": f"art-{i}",
            "input_type": "topic",
            "raw_input": f"test {i}",
            "rag_context": "",
            "draft": "",
            "fact_check_report": {},
            "edited_draft": "",
            "aggregated_article": "",
            "credibility_score": 0.0,
            "status": ArticleStatus.PROCESSING.value if i < 2 else ArticleStatus.PUBLISHED.value,
            "revision_count": 0,
            "events": [],
        }
        await store.save(f"art-{i}", state)
    result = await store.list(status=ArticleStatus.PROCESSING.value)
    assert result["total"] == 2


@pytest.mark.asyncio
async def test_list_with_min_score() -> None:
    store = ArticleStore()
    for i in range(3):
        state: ArticleState = {
            "article_id": f"art-{i}",
            "input_type": "topic",
            "raw_input": f"test {i}",
            "rag_context": "",
            "draft": "",
            "fact_check_report": {},
            "edited_draft": "",
            "aggregated_article": "",
            "credibility_score": 0.5 + (i * 0.2),
            "status": ArticleStatus.PUBLISHED.value,
            "revision_count": 0,
            "events": [],
        }
        await store.save(f"art-{i}", state)
    result = await store.list(min_score=0.8)
    assert result["total"] == 1


@pytest.mark.asyncio
async def test_list_pagination() -> None:
    store = ArticleStore()
    for i in range(5):
        state: ArticleState = {
            "article_id": f"art-{i}",
            "input_type": "topic",
            "raw_input": f"test {i}",
            "rag_context": "",
            "draft": "",
            "fact_check_report": {},
            "edited_draft": "",
            "aggregated_article": "",
            "credibility_score": 0.0,
            "status": ArticleStatus.PROCESSING.value,
            "revision_count": 0,
            "events": [],
        }
        await store.save(f"art-{i}", state)
    result = await store.list(page=1, limit=2)
    assert result["total"] == 5
    assert len(result["articles"]) == 2
    assert result["page"] == 1

    result = await store.list(page=2, limit=2)
    assert len(result["articles"]) == 2
