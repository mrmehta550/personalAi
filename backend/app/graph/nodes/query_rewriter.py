import re
from typing import Dict, Any, Optional
from app.graph.state import GraphState
from app.core.logger import logger

# Project names to track across conversation turns
_KNOWN_PROJECTS = [
    "ai mail automation",
    "mail automation",
    "email automation",
    "youtube ai assistant",
    "youtube assistant",
    "student portal",
    "personal ai assistant",
    "digital twin",
    "portfolio assistant",
]

# Canonical project title mapping
_PROJECT_TITLE_MAP = {
    "mail": "AI Mail Automation",
    "email": "AI Mail Automation",
    "youtube": "YouTube AI Assistant",
    "student": "Student Portal",
    "digital twin": "Personal AI Assistant",
    "personal ai": "Personal AI Assistant",
    "portfolio assistant": "Personal AI Assistant",
}

# Follow-up indicator pronouns/phrases that signal a query needs context injection
_FOLLOWUP_TRIGGERS = [
    " it", " that", " this", " those", " these",
    "what stack", "which stack", "what tech", "which tech",
    "what technologies", "which technologies",
    "what tools", "which tools",
    "what technology", "which technology",
    "what problem", "which problem",
    "how does it", "how did you",
    "what database", "which database",
    "why did you", "how long",
    "what backend", "what frontend", "what api",
    "how does that work", "how did that work",
    "tell me more", "more details", "elaborate", "expand",
    "what about", "and what", "what else",
    # Handle bare "what technologies did you use" as follow-up
    "what technologies did you use",
    "what technology did you use",
    "what tools did you use",
    "which technologies did you use",
    "which technology did you use",
    "technologies used",
    "tech stack used",
    "what was the stack",
    "what was the tech",
]


def _extract_last_project(messages) -> Optional[str]:
    """Scan recent assistant + user messages for the last mentioned known project name."""
    for msg in reversed(messages):
        content = msg.get("content", "").lower()
        for project in _KNOWN_PROJECTS:
            if project in content:
                # Map to official project title
                if "mail" in project or "email" in project:
                    return "AI Mail Automation"
                elif "youtube" in project:
                    return "YouTube AI Assistant"
                elif "student" in project:
                    return "Student Portal"
                elif "digital twin" in project or "personal ai" in project:
                    return "Personal AI Assistant"
                return project.title()
    return None


def _contains_project_name(text: str) -> bool:
    """Check if the text already contains a specific project name."""
    lower = text.lower()
    return any(p in lower for p in _KNOWN_PROJECTS)


def query_rewriter_node(state: GraphState) -> Dict[str, Any]:
    raw_query = state.get("raw_query", "").strip()
    messages = state.get("messages", [])

    logger.info(f"Executing query_rewriter_node. Raw query: '{raw_query}', Message turns: {len(messages)}")

    # First message — no prior context to rewrite against
    if not messages or len(messages) <= 1:
        return {"rewritten_query": raw_query}

    lower_query = raw_query.lower()

    # If the query already names a specific project, no rewrite needed
    if _contains_project_name(raw_query):
        logger.info(f"Query already contains project name, no rewrite needed.")
        return {"rewritten_query": raw_query}

    # Check if this query contains follow-up triggers
    is_followup = any(trigger in lower_query for trigger in _FOLLOWUP_TRIGGERS)

    if not is_followup:
        return {"rewritten_query": raw_query}

    # Context injection for follow-up queries
    last_project = _extract_last_project(messages)
    rewritten = raw_query

    if last_project:
        # Technology/stack questions
        tech_patterns = [
            r"what (tech|technology|technologies|tools|stack|libraries|frameworks?) did (you|i) use",
            r"what (tech|technology|technologies|tools|stack|libraries|frameworks?) (do|does) it use",
            r"what (tech|technology|technologies|tools|stack|libraries|frameworks?) (are|were) (used|involved)",
            r"which (tech|technology|technologies|tools|stack) (did|do) (you|i) use",
            r"what (is|was) the (tech|technology|stack|backend|frontend)",
            r"technologies (used|involved)",
            r"tech stack",
        ]
        # Database questions
        db_patterns = [
            r"what database (did|do) (you|i) use",
            r"what database (does|did) it use",
            r"which database (did|do) (you|i) use",
        ]
        # Problem/purpose questions
        problem_patterns = [
            r"what problem (does|did) it solve",
            r"what problem (does|did) (that|this) solve",
            r"what('s| is) the problem",
            r"what('s| is) it for",
            r"what does it do",
        ]
        # Architecture/design questions
        arch_patterns = [
            r"how (does|did) it work",
            r"how (is|was) it built",
            r"(explain|describe) the architecture",
            r"how (is|was) it structured",
        ]

        matched = False
        for pat in tech_patterns:
            if re.search(pat, lower_query):
                rewritten = f"What technologies did I use in my {last_project} project?"
                matched = True
                break

        if not matched:
            for pat in db_patterns:
                if re.search(pat, lower_query):
                    rewritten = f"What database did I use in my {last_project} project?"
                    matched = True
                    break

        if not matched:
            for pat in problem_patterns:
                if re.search(pat, lower_query):
                    rewritten = f"What problem does my {last_project} project solve?"
                    matched = True
                    break

        if not matched:
            for pat in arch_patterns:
                if re.search(pat, lower_query):
                    rewritten = f"How does my {last_project} project work?"
                    matched = True
                    break

        if not matched:
            # Generic follow-up — append project context
            rewritten = f"{raw_query} (regarding my {last_project} project)"

    if rewritten != raw_query:
        logger.info(f"Query rewritten: '{raw_query}' → '{rewritten}'")

    return {"rewritten_query": rewritten}
