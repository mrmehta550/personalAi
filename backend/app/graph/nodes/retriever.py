from typing import Dict, Any
from app.graph.state import GraphState
from app.vectorstore.collection_manager import collection_manager
from app.core.logger import logger

# Intents that must NEVER touch ChromaDB
_NO_RETRIEVAL_INTENTS = {
    "GREETING",
    "PRIVATE_REQUEST",
    "CREDENTIAL_REQUEST",
    "PROMPT_INJECTION",
    "OFF_TOPIC",
    "PROJECT_COUNT",
    "RESUME_REQUEST",
}


def retriever_node(state: GraphState) -> Dict[str, Any]:
    intent = state.get("intent", "PERSONAL_INQUIRY")
    target_collections = state.get("target_collections", [])

    # Hard gate — certain intents must NEVER reach ChromaDB
    if intent in _NO_RETRIEVAL_INTENTS or not target_collections:
        logger.info(
            f"[RETRIEVER] Skipping ChromaDB — "
            f"intent={intent} collections={target_collections}"
        )
        return {"retrieved_docs": []}

    query = state.get("rewritten_query") or state.get("raw_query", "")
    logger.info(
        f"[RETRIEVER] Querying ChromaDB — "
        f"intent={intent} collections={target_collections} query=\"{query[:80]}\""
    )

    docs = collection_manager.search_collections(
        query=query,
        collection_names=target_collections,
        top_k=3,
        use_mmr=True
    )

    logger.info(f"[RETRIEVER] Retrieved {len(docs)} chunks from ChromaDB")
    return {"retrieved_docs": docs}
