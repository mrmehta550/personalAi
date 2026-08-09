from typing import Dict, Any
from app.graph.state import GraphState
from app.core.logger import logger

def context_builder_node(state: GraphState) -> Dict[str, Any]:
    docs = state.get("retrieved_docs", [])
    
    logger.info(f"Executing context_builder_node with {len(docs)} chunks.")

    if not docs:
        context_str = "No specific background records found for this inquiry."
    else:
        seen_snippets = set()
        context_parts = []
        
        for idx, doc in enumerate(docs, 1):
            meta = doc.get("metadata", {})
            col = meta.get("collection", "general")
            src = meta.get("source_file", meta.get("source", "knowledge_base"))
            content = doc.get("content", "").strip()
            
            # Simple sentence/content deduplication
            content_key = content[:100].lower()
            if content_key in seen_snippets:
                continue
            seen_snippets.add(content_key)
            
            context_parts.append(f"--- Document Chunk {idx} [Collection: {col} | Source: {src}] ---\n{content}")
            
        context_str = "\n\n".join(context_parts) if context_parts else "No specific background records found for this inquiry."

    return {"context_str": context_str}
