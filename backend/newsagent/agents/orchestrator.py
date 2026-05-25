import logging
from uuid import uuid4

from newsagent.core.events import make_event
from newsagent.core.state import ArticleState, ArticleStatus

logger = logging.getLogger(__name__)


class OrchestratorAgent:
    async def run(self, state: ArticleState) -> ArticleState:
        logger.info("[Orchestrator] mulai pipeline — article_id=%s", state["article_id"])

        try:
            if "article_id" not in state or not state["article_id"]:
                state = {**state, "article_id": uuid4().hex[:12]}

            rev = state.get("revision_count", 0) + 1
            logger.info("[Orchestrator] revision_count=%d (MAX=%d)", rev, 2)

            return {
                **state,
                "status": ArticleStatus.PROCESSING.value,
                "revision_count": rev,
                "events": state["events"]
                + [
                    make_event(
                        "Orchestrator",
                        "init_pipeline",
                        f"pipeline dimulai untuk {state['input_type']} (rev={rev})",
                    )
                ],
            }
        except Exception as e:
            logger.error("[Orchestrator] gagal: %s", e)
            return {
                **state,
                "status": ArticleStatus.FAILED.value,
                "events": state["events"] + [make_event("Orchestrator", "failed", str(e))],
            }
