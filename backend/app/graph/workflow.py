from langgraph.graph import StateGraph, END
from app.graph.state import GraphState
from app.graph.nodes.intent_detector import intent_detector_node
from app.graph.nodes.query_rewriter import query_rewriter_node
from app.graph.nodes.retriever import retriever_node
from app.graph.nodes.context_builder import context_builder_node
from app.graph.nodes.llm_generator import llm_generator_node
from app.graph.nodes.validator import validator_node
from app.graph.nodes.memory_node import memory_node
from app.core.logger import logger

# Intents that skip the RAG retrieval pipeline entirely
_SKIP_RETRIEVAL_INTENTS = {
    "GREETING",
    "OFF_TOPIC",
    "PRIVATE_REQUEST",
    "CREDENTIAL_REQUEST",
    "PROMPT_INJECTION",
    "PROJECT_COUNT",   # answered deterministically
    "RESUME_REQUEST",  # served as PDF file metadata, no ChromaDB
}


def route_intent(state: GraphState) -> str:
    """Routes graph flow based on intent classification."""
    intent = state.get("intent", "PERSONAL_INQUIRY")
    if intent in _SKIP_RETRIEVAL_INTENTS:
        logger.info(f"[WORKFLOW] intent={intent} → skipping RAG → generator")
        return "generator"
    logger.info(f"[WORKFLOW] intent={intent} → RAG pipeline → rewriter")
    return "rewriter"


def build_workflow():
    logger.info("Building LangGraph State Machine Workflow DAG...")
    workflow = StateGraph(GraphState)

    # ── Add Nodes ────────────────────────────────────────────────────────────
    workflow.add_node("intent_detector", intent_detector_node)
    workflow.add_node("rewriter", query_rewriter_node)
    workflow.add_node("retriever", retriever_node)
    workflow.add_node("context_builder", context_builder_node)
    workflow.add_node("generator", llm_generator_node)
    workflow.add_node("validator", validator_node)
    workflow.add_node("memory", memory_node)

    # ── Entry Point ──────────────────────────────────────────────────────────
    workflow.set_entry_point("intent_detector")

    # ── Conditional Routing ──────────────────────────────────────────────────
    # GREETING / OFF_TOPIC / PRIVATE / CREDENTIAL / INJECTION / PROJECT_COUNT
    #   → generator directly (no retrieval)
    # PERSONAL_INQUIRY
    #   → rewriter → retriever → context_builder → generator
    workflow.add_conditional_edges(
        "intent_detector",
        route_intent,
        {
            "generator": "generator",
            "rewriter": "rewriter",
        }
    )

    # ── RAG Pipeline Flow ────────────────────────────────────────────────────
    workflow.add_edge("rewriter", "retriever")
    workflow.add_edge("retriever", "context_builder")
    workflow.add_edge("context_builder", "generator")

    # ── Validation & Memory ──────────────────────────────────────────────────
    workflow.add_edge("generator", "validator")
    workflow.add_edge("validator", "memory")
    workflow.add_edge("memory", END)

    app = workflow.compile()
    logger.info("LangGraph workflow compiled successfully.")
    return app


# Graph singleton instance
langgraph_app = build_workflow()
