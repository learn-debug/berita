import logging
from uuid import uuid4

from newsagent.core.events import make_event
from newsagent.core.state import ArticleState

logger = logging.getLogger(__name__)


class OrchestratorAgent:
    async def run(self, state: ArticleState) -> ArticleState:
        logger.info("[Orchestrator] mulai pipeline — article_id=%s", state["article_id"])

        try:
            if "article_id" not in state or not state["article_id"]:
                state = {**state, "article_id": uuid4().hex[:12]}

            return {
                **state,
                "status": "processing",
                "events": state["events"]
                + [
                    make_event(
                        "Orchestrator", "init_pipeline", f"pipeline dimulai untuk {state['input_type']}"
                    )
                ],
            }
        except Exception as e:
            logger.error("[Orchestrator] gagal: %s", e)
            return {
                **state,
                "status": "failed",
                "events": state["events"] + [make_event("Orchestrator", "failed", str(e))],
            }
