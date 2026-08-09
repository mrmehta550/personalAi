from typing import TypedDict, List, Dict, Any, Optional

class GraphState(TypedDict, total=False):
    messages: List[Dict[str, str]]
    raw_query: str
    rewritten_query: str
    intent: str
    target_collections: List[str]
    retrieved_docs: List[Dict[str, Any]]
    context_str: str
    llm_raw_response: str
    is_grounded: bool
    final_response: str
    session_id: str
    resume_request: bool   # True when RESUME_REQUEST intent — signals PDF card to frontend
