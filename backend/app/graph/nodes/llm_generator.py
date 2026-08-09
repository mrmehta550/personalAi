import os
import asyncio
import httpx
from typing import Dict, Any, AsyncGenerator
from app.graph.state import GraphState
from app.graph.prompts.system_persona import (
    SYSTEM_PERSONA_PROMPT,
    OFF_TOPIC_REJECTION,
    PRIVATE_REJECTION,
    CREDENTIAL_REJECTION,
    INJECTION_REJECTION,
)
from app.core.config import settings
from app.core.logger import logger


# ── Greeting responses — short, natural, first-person ───────────────────────

# Deterministic project count — update this if more projects are added
_PROJECT_COUNT_RESPONSE = (
    "I've built 4 major projects documented in my portfolio:\n\n"
    "1. **AI Mail Automation** — AI-powered email processing and response generation system\n"
    "2. **YouTube AI Assistant** — AI assistant that answers questions about YouTube video content\n"
    "3. **Student Portal** — Web platform for student management and academic workflows\n"
    "4. **Personal AI Assistant (Digital Twin)** — This portfolio AI assistant you're talking to right now\n\n"
    "Feel free to ask me about any of these projects for more details!"
)


def _greeting_response(raw_query: str = "") -> str:
    lower = raw_query.lower().strip().rstrip("?.!,;")

    if any(p in lower for p in ["how are you", "how's it going", "how do you do", "hows it going"]):
        return (
            "I'm doing great, thanks for asking! "
            "I'm here to help you learn about my projects, skills, and experience. "
            "What would you like to know?"
        )
    elif any(p in lower for p in ["who are you", "what are you", "what can you do", "what can you help"]):
        return (
            "I'm Vishal's AI portfolio assistant — a digital twin built to represent his professional background. "
            "Ask me about his projects, technical skills, work experience, education, or how to get in touch."
        )
    elif any(p in lower for p in ["good morning", "good afternoon", "good evening", "good day"]):
        return (
            "Good day! I'm Vishal's AI portfolio assistant. "
            "Feel free to ask me about my projects, skills, or experience."
        )
    else:
        return (
            "Hi! \U0001F44B I'm Vishal's AI portfolio assistant. "
            "I can tell you about my projects, skills, experience, and technical background. "
            "What would you like to know?"
        )


# ── Meta-phrase prefixes to strip from LLM output ───────────────────────────

_META_PREFIXES = [
    "Based on my portfolio records,",
    "Based on my portfolio records:",
    "Based on my portfolio records",
    "Based on the retrieved sources,",
    "Based on the retrieved sources:",
    "Based on the information provided,",
    "Based on the information provided:",
    "Based on the context provided,",
    "Based on the context provided:",
    "According to my portfolio,",
    "According to my portfolio:",
    "According to the knowledge base,",
    "According to the knowledge base:",
    "According to the context,",
    "According to the context:",
    "As per my records,",
    "As per my records:",
    "From my portfolio data,",
    "From my portfolio data:",
    "The context shows that",
    "The records indicate that",
    "My portfolio shows that",
    "My portfolio shows:",
]


# ── Helper: run async call from sync context ─────────────────────────────────

def _run_async(coro):
    """Run an async coroutine from a synchronous context safely."""
    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            import concurrent.futures
            with concurrent.futures.ThreadPoolExecutor() as pool:
                future = pool.submit(asyncio.run, coro)
                return future.result()
        else:
            return loop.run_until_complete(coro)
    except RuntimeError:
        return asyncio.run(coro)


# ── Main generator node (SYNC — required by LangGraph sync .invoke()) ────────

def llm_generator_node(state: GraphState) -> Dict[str, Any]:
    intent = state.get("intent", "PERSONAL_INQUIRY")
    raw_query = state.get("raw_query", "")
    rewritten_query = state.get("rewritten_query") or raw_query
    context_str = state.get("context_str", "")

    logger.info(f"[GENERATOR] intent={intent}")

    if intent == "GREETING":
        response = _greeting_response(raw_query)
        logger.info(f"[GENERATOR] GREETING response → no LLM call, no retrieval")
        return {"llm_raw_response": response, "final_response": response}

    if intent == "RESUME_REQUEST":
        logger.info(f"[GENERATOR] RESUME_REQUEST -> returning PDF metadata, no LLM call")
        # Use a short conversational intro; the actual PDF card is rendered by the frontend
        # based on the resume_data field attached by chat.py to the SSE metadata event.
        response = "Sure! Here is my latest resume. You can view or download it below."
        return {
            "llm_raw_response": response,
            "final_response": response,
            "resume_request": True,  # signal to chat.py to attach resume metadata
        }

    if intent == "PROJECT_COUNT":
        logger.info(f"[GENERATOR] PROJECT_COUNT → deterministic response, no LLM call")
        return {"llm_raw_response": _PROJECT_COUNT_RESPONSE, "final_response": _PROJECT_COUNT_RESPONSE}

    if intent == "OFF_TOPIC":
        return {"llm_raw_response": OFF_TOPIC_REJECTION, "final_response": OFF_TOPIC_REJECTION}

    if intent == "PRIVATE_REQUEST":
        return {"llm_raw_response": PRIVATE_REJECTION, "final_response": PRIVATE_REJECTION}

    if intent == "CREDENTIAL_REQUEST":
        return {"llm_raw_response": CREDENTIAL_REJECTION, "final_response": CREDENTIAL_REJECTION}

    if intent == "PROMPT_INJECTION":
        return {"llm_raw_response": INJECTION_REJECTION, "final_response": INJECTION_REJECTION}

    # For PERSONAL_INQUIRY: format prompt and call LLM
    prompt = SYSTEM_PERSONA_PROMPT.format(
        context_str=context_str,
        query=rewritten_query
    )

    response = _run_async(call_llm_engine(prompt, context_str))
    return {"llm_raw_response": response, "final_response": response}


# ── Hugging Face API caller (async) ──────────────────────────────────────────

async def call_llm_engine(prompt: str, context_str: str) -> str:
    hf_token = settings.HF_TOKEN
    model = settings.HF_MODEL

    if hf_token:
        try:
            logger.info(f"Invoking Hugging Face Inference API: model={model}")
            headers = {
                "Authorization": f"Bearer {hf_token}",
                "Content-Type": "application/json",
            }
            payload = {
                "inputs": prompt,
                "parameters": {
                    "max_new_tokens": settings.HF_MAX_TOKENS,
                    "temperature": settings.HF_TEMPERATURE,
                    "return_full_text": False,
                    "do_sample": True,
                }
            }
            async with httpx.AsyncClient(timeout=45.0) as client:
                res = await client.post(
                    f"https://api-inference.huggingface.co/models/{model}",
                    headers=headers,
                    json=payload
                )
                logger.info(f"HF API response status: {res.status_code}")

                if res.status_code == 200:
                    data = res.json()
                    if isinstance(data, list) and len(data) > 0:
                        item = data[0]
                        text = item.get("generated_text", "")
                        if text:
                            return _clean_generated_text(text, prompt)
                    elif isinstance(data, dict):
                        text = data.get("generated_text", "")
                        if text:
                            return _clean_generated_text(text, prompt)
                elif res.status_code == 503:
                    logger.warning("HF model loading (503). Using grounded response.")

        except Exception as e:
            logger.error(f"HF API call error: {e}. Using grounded response.")

    return generate_grounded_fallback_response(context_str)


def _clean_generated_text(text: str, prompt: str) -> str:
    """Clean LLM output: strip prompt echo, meta-prefixes, third-person references."""
    # Remove prompt echo if the model returned the full text
    if text.startswith(prompt):
        text = text[len(prompt):]

    text = text.strip().lstrip(":\n ")

    # Strip all known meta-prefix phrases (case-insensitive check, exact strip)
    for prefix in _META_PREFIXES:
        if text.startswith(prefix):
            text = text[len(prefix):].strip().lstrip(", ")
            break

    # Also catch lowercase variants
    text_lower_start = text[:60].lower()
    for prefix in _META_PREFIXES:
        if text_lower_start.startswith(prefix.lower()):
            text = text[len(prefix):].strip().lstrip(", ")
            break

    # Remove lingering third-person owner name references at the start
    owner = settings.OWNER_NAME
    if owner and text.startswith(owner):
        text = "I" + text[len(owner):]

    return text.strip()


def generate_grounded_fallback_response(context_str: str) -> str:
    """
    Deterministic first-person response from retrieved context.
    Used when the HF API is unavailable or fails.
    Returns exact specified message when no context is available.
    """
    if not context_str or "No specific background records found" in context_str:
        return (
            "I don't have that specific detail recorded in my knowledge base records. "
            "Please feel free to reach out to me directly through my contact details."
        )

    # Extract informative lines from context
    lines = [
        line.strip() for line in context_str.split("\n")
        if line.strip()
        and not line.startswith("---")
        and not line.startswith("[Collection:")
        and not line.startswith("Document Chunk")
    ]

    good_lines = [l for l in lines if len(l) > 20][:3]

    if not good_lines:
        return (
            "I don't have that specific detail recorded in my knowledge base records. "
            "Please feel free to reach out to me directly through my contact details."
        )

    synthesis = " ".join(good_lines[:2])
    synthesis = synthesis.replace(settings.OWNER_NAME, "I")
    synthesis = synthesis.replace("Vishal", "I")

    return synthesis


# ── SSE Streaming (kept for legacy compatibility if needed) ──────────────────

async def stream_llm_tokens(
    prompt: str, context_str: str, intent: str, raw_query: str = ""
) -> AsyncGenerator[str, None]:
    """
    Legacy streaming helper. NOTE: chat.py no longer calls this directly;
    it streams the pre-computed final_response from the LangGraph state.
    Kept for backward compatibility with any other callers.
    """
    if intent == "GREETING":
        full_text = _greeting_response(raw_query)
    elif intent == "OFF_TOPIC":
        full_text = OFF_TOPIC_REJECTION
    elif intent == "PRIVATE_REQUEST":
        full_text = PRIVATE_REJECTION
    elif intent == "CREDENTIAL_REQUEST":
        full_text = CREDENTIAL_REJECTION
    elif intent == "PROMPT_INJECTION":
        full_text = INJECTION_REJECTION
    else:
        full_text = await call_llm_engine(prompt, context_str)

    words = full_text.split(" ")
    for i, word in enumerate(words):
        token = word + (" " if i < len(words) - 1 else "")
        yield token
