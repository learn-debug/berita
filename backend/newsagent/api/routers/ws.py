import asyncio
import logging

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from newsagent.api.event_bus import EventBus
from newsagent.api.store import ArticleStore

logger = logging.getLogger(__name__)

router = APIRouter()


@router.websocket("/ws/{article_id}")
async def pipeline_ws(websocket: WebSocket, article_id: str, _token: str | None = None) -> None:
    from newsagent.api.auth import verify_ws_token
    from newsagent.api.main import _event_bus, _store

    if not await verify_ws_token(websocket):
        await websocket.close(code=4001)
        return

    event_bus: EventBus = _event_bus
    store: ArticleStore = _store

    await websocket.accept()

    article = await store.get(article_id)
    if not article:
        await websocket.send_json({"type": "error", "message": "Article not found"})
        await websocket.close()
        return

    q = event_bus.subscribe(article_id)
    try:
        await websocket.send_json(
            {
                "type": "connected",
                "article_id": article_id,
                "status": article.get("status", "unknown"),
            }
        )

        while True:
            try:
                event = await asyncio.wait_for(q.get(), timeout=30.0)
                await websocket.send_json(event)
                if event.get("type") in ("pipeline_complete", "pipeline_error"):
                    break
            except TimeoutError:
                try:
                    await websocket.send_json({"type": "ping"})
                except Exception:
                    break
    except WebSocketDisconnect:
        logger.info("[WS] client disconnected: %s", article_id)
    finally:
        event_bus.unsubscribe(article_id, q)
