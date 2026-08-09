import json
import asyncio
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from app.schemas.chat_schema import ChatRequest, ChatResponse, SourceItem
from app.graph.workflow import langgraph_app
from app.graph.nodes.memory_node import memory_store
from app.core.security import sanitize_input, check_prompt_injection, check_private_request, check_credential_request
from app.core.logger import logger

router = APIRouter()


@router.post("/chat/stream")
async def chat_stream(request: ChatRequest):
    raw_input = sanitize_input(request.message)
    if not raw_input:
        raise HTTPException(status_code=400, detail="Empty or invalid query message.")

    logger.info(f"[ENDPOINT] POST /chat/stream message=\"{raw_input[:80]}\"")

    # Log suspicious patterns at endpoint level (guard runs again inside graph)
    if check_prompt_injection(raw_input):
        logger.warning(f"[ENDPOINT] Prompt injection flagged: '{raw_input[:80]}'")
    elif check_private_request(raw_input):
        logger.warning(f"[ENDPOINT] Private request flagged: '{raw_input[:80]}'")
    elif check_credential_request(raw_input):
        logger.warning(f"[ENDPOINT] Credential request flagged: '{raw_input[:80]}'")

    thread_id = request.thread_id or "default_session"

    # Fetch conversation memory turns
    messages = memory_store.get_messages(thread_id)

    # Initial state for LangGraph
    initial_state = {
        "messages": messages,
        "raw_query": raw_input,
        "rewritten_query": raw_input,
        "intent": "PERSONAL_INQUIRY",
        "target_collections": [],
        "retrieved_docs": [],
        "context_str": "",
        "llm_raw_response": "",
        "is_grounded": True,
        "final_response": "",
        "session_id": thread_id
    }

    # Execute the full LangGraph pipeline — ONE call, result is reused for streaming
    try:
        final_graph_state = await asyncio.to_thread(langgraph_app.invoke, initial_state)
    except Exception as e:
        logger.error(f"LangGraph execution error: {e}")
        final_graph_state = {
            **initial_state,
            "intent": "PERSONAL_INQUIRY",
            "context_str": "",
            "final_response": "I'm sorry, I encountered an issue processing your request. Please try again.",
        }

    intent = final_graph_state.get("intent", "PERSONAL_INQUIRY")
    collections = final_graph_state.get("target_collections", [])
    docs = final_graph_state.get("retrieved_docs", [])

    # Use the final_response already computed by the graph — NO second LLM call
    final_response_text = final_graph_state.get("final_response", "").strip()

    if not final_response_text:
        final_response_text = "I don't have that specific detail recorded in my knowledge base records. Please feel free to reach out to me directly through my contact details."

    # Build source metadata (0 sources for non-RAG intents)
    _non_rag_intents = {
        "GREETING",
        "PRIVATE_REQUEST",
        "CREDENTIAL_REQUEST",
        "PROMPT_INJECTION",
        "OFF_TOPIC",
        "PROJECT_COUNT",  # deterministic answer, no ChromaDB
        "RESUME_REQUEST", # PDF file served directly, no ChromaDB
    }
    sources = []
    if intent not in _non_rag_intents:
        for d in docs:
            meta = d.get("metadata", {})
            sources.append({
                "collection": meta.get("collection", "general"),
                "source": meta.get("source", meta.get("source_file", "knowledge_base")),
                "content_snippet": d.get("content", "")[:120]
            })

    # Build resume metadata if this is a RESUME_REQUEST
    resume_data = None
    if intent == "RESUME_REQUEST":
        resume_data = {
            "type": "resume",
            "file_name": "Vishal_Kumar_Resume.pdf",
            "download_url": "/api/v1/resume",
        }
        logger.info("[RESUME] Attaching resume PDF card metadata to SSE response")

    logger.info(
        f"[RETRIEVAL] intent={intent} "
        f"collections={collections} "
        f"sources={len(sources)}"
    )

    async def event_generator():
        # ── Event 1: metadata ────────────────────────────────────────────────────
        meta_event = {
            "event": "metadata",
            "thread_id": thread_id,
            "intent": intent,
            "collections": collections if intent not in _non_rag_intents else [],
            "sources": sources,
        }
        # Attach resume card data when intent is RESUME_REQUEST
        if resume_data:
            meta_event["resume_data"] = resume_data
        yield f"data: {json.dumps(meta_event)}\n\n"
        await asyncio.sleep(0.02)

        # ── Event 2: stream the pre-computed final_response word-by-word ────
        # This avoids a second LLM call. The LangGraph graph already ran the
        # full pipeline (intent detection → retrieval → generation → validation).
        words = final_response_text.split(" ")
        for i, word in enumerate(words):
            token = word + (" " if i < len(words) - 1 else "")
            token_event = {
                "event": "token",
                "content": token
            }
            yield f"data: {json.dumps(token_event)}\n\n"
            await asyncio.sleep(0.01)

        # Save conversation turn to memory (only if not already saved by memory_node)
        # memory_node in graph already saves; this avoids a duplicate save
        # memory_store.save_turn(thread_id, raw_input, final_response_text)

        # ── Event 3: end ────────────────────────────────────────────────────
        end_event = {
            "event": "end",
            "status": "completed",
            "sources": sources
        }
        yield f"data: {json.dumps(end_event)}\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")


@router.get("/chat/history/{thread_id}")
async def get_chat_history(thread_id: str):
    history = memory_store.get_messages(thread_id)
    return {"thread_id": thread_id, "messages": history}


@router.delete("/chat/history/{thread_id}")
async def clear_chat_history(thread_id: str):
    memory_store.clear_memory(thread_id)
    return {"thread_id": thread_id, "status": "cleared"}
