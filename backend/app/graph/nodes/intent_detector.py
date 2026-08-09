import re
from typing import Dict, Any, List
from app.graph.state import GraphState
from app.core.logger import logger
from app.core.security import check_prompt_injection, check_private_request, check_credential_request


# ─── Targeted Keyword Routing Maps ──────────────────────────────────────────

_COLLECTION_KEYWORDS: Dict[str, List[str]] = {
    "projects": [
        "project", "build", "built", "architecture", "app", "application",
        "demo", "case study", "mail automation", "email automation",
        "youtube", "youtube assistant", "youtube ai",
        "student portal", "digital twin", "personal ai",
        "portfolio assistant", "chatbot", "automation", "system",
    ],
    "skills": [
        "skill", "stack", "tech", "technology", "technologies", "tool", "tools",
        "python", "javascript", "js", "react", "fastapi", "django", "drf",
        "langchain", "langgraph", "hugging face", "huggingface", "chromadb",
        "chroma", "rag", "retrieval", "embedding", "vector", "sql", "mysql",
        "sqlite", "git", "github", "docker", "api", "rest", "ai", "ml",
        "machine learning", "deep learning", "nlp", "llm", "language model",
        "database", "backend", "frontend", "fullstack",
    ],
    "experience": [
        "experience", "work", "worked", "working", "company", "companies",
        "role", "job", "career", "history", "employment", "internship",
        "intern", "position", "industry",
    ],
    "resume": [
        "resume", "cv", "curriculum vitae", "education", "degree",
        "university", "college", "study", "studied", "graduate", "graduation",
        "bachelor", "bca", "qualification",
    ],
    "about_me": [
        "tell me about yourself", "about yourself",
        "introduce", "introduction", "bio", "profile",
        "background", "career goal",
    ],
    "contact_info": [
        "contact", "email", "reach", "hire", "freelance", "get in touch",
        "phone", "message", "connect",
    ],
    "github": [
        "github", "repository", "repo", "open source", "code",
        "commit", "pull request", "contribution",
    ],
    "linkedin": [
        "linkedin", "professional network", "profile link",
    ],
    "certificates": [
        "certif", "license", "certification", "credential", "course",
        "training", "badge", "achievement",
    ],
    "blogs": [
        "blog", "article", "post", "publication", "medium",
    ],
    "services": [
        "service", "services", "offer", "offering", "provide", "providing",
        "consulting", "consultant", "freelance", "freelancer", "hire",
        "available for", "work together", "collaborate",
    ],
    "faqs": [
        "faq", "frequently",
    ],
}

# Compound routing rules (max 2 collections per rule)
_COMPOUND_ROUTING: List[Dict] = [
    {"triggers": ["education", "study", "degree", "university", "college", "bca"],
     "target_collections": ["about_me", "resume"]},
    {"triggers": ["experience", "work history", "career"],
     "target_collections": ["experience", "resume"]},
    {"triggers": ["contact", "email", "reach me"],
     "target_collections": ["contact_info"]},
]

# Strong off-topic indicators — checked BEFORE collection routing
_STRONG_OFF_TOPIC_PATTERNS: List[str] = [
    "capital of",
    "who is the president",
    "who won the",
    "tell me a joke",
    "solve this math",
    "solve math",
    "math problem",
    "explain quantum",
    "what happened in the news",
    "today's news",
    "news today",
    "current news",
    "weather in",
    "recipe for",
    "write a poem",
    "write an essay",
    "generate a random",
    "create a random",
    "write a script",
    "write a scraper",
    "write a program",
    "write me a program",
    "write me a script",
    "write code for",
    "python scraper",
    "web scraper",
    "unrelated math",
]

# Resume download / delivery request patterns
# NOTE: "what is in your resume" is intentionally NOT here — that goes through RAG
_RESUME_PATTERNS: List[str] = [
    "give me your resume",
    "give me your cv",
    "send me your resume",
    "send me your cv",
    "can i get your resume",
    "can i get your cv",
    "i want your resume",
    "i want your cv",
    "download your resume",
    "download your cv",
    "download resume",
    "download cv",
    "share your resume",
    "share your cv",
    "resume please",
    "cv please",
    "show me your resume",
    "provide your resume",
    "provide your cv",
    "can you share your resume",
    "can you send me your resume",
    "where can i download your resume",
    "where can i get your resume",
    "where can i get your cv",
    "get your resume",
    "get your cv",
    "your resume please",
    "your cv please",
    "send your resume",
    "send your cv",
]


# Project count queries — answered deterministically, no RAG needed
_PROJECT_COUNT_PATTERNS: List[str] = [
    "how many projects",
    "how many project",
    "number of projects",
    "total projects",
    "projects have you built",
    "projects have you done",
    "projects did you build",
    "projects do you have",
    "how many things have you built",
]

# ─── Greeting Detection ───────────────────────────────────────────────────────

# Exact-match greetings after normalizing (strip punctuation, collapse spaces,
# normalize repeated chars like "hii" → "hi", "heyyy" → "hey")
_GREETING_EXACT: frozenset = frozenset({
    "hi", "hello", "hey", "hey there", "howdy", "sup",
    "what's up", "whats up", "good morning", "good afternoon", "good evening",
    "how are you", "how are you doing", "how's it going", "hows it going",
    "how do you do", "nice to meet you", "greetings", "good day",
    "who are you", "what are you", "what can you do",
    "what can you help me with", "how can you help me",
    "hello there", "hi there",
})

# Prefix greetings — if normalized query STARTS with one of these, it's a greeting
_GREETING_PREFIXES: tuple = (
    "hi ", "hi,", "hi!", "hello ", "hello,", "hello!",
    "hey ", "hey,", "hey!", "good morning", "good afternoon", "good evening",
    "greetings", "hello there", "hi there",
)

# Substring greetings with max-length cap
_GREETING_SUBSTRINGS: List[tuple] = [
    ("how are you", 40),
    ("how's it going", 40),
    ("hows it going", 40),
    ("how do you do", 40),
    ("who are you", 35),
    ("what can you do", 45),
    ("what are you", 35),
    ("nice to meet you", 40),
]

# Regex: repeated-char greetings like "hii", "hiii", "heyyy", "hellooo"
_GREETING_REPEATED_CHAR_RE = re.compile(
    r"^(h+i+|h+e+y+|h+e+l+o+|h+e+l+l+o+)\s*[!?.,]*$",
    re.IGNORECASE
)


def _normalize_query(query: str) -> str:
    """
    Normalize a query for greeting detection:
    - Strip leading/trailing whitespace
    - Strip trailing punctuation
    - Collapse internal whitespace
    - Lowercase
    Does NOT collapse repeated chars (that's done separately via regex).
    """
    q = query.strip()
    q = q.rstrip("?.!,;:")
    q = " ".join(q.split())   # collapse multiple spaces
    return q.lower()


def _is_greeting(query: str) -> bool:
    """
    Robust, deterministic greeting detection.
    Runs BEFORE any LLM call, query rewriting, or ChromaDB access.

    Handles:
      - "hi", "hello", "hey"
      - "hii", "hiii", "heyyy"  (repeated chars)
      - "HI", "Hello!", "hey!!"  (case / punctuation variants)
      - " hi "  (extra whitespace)
      - "how are you?", "who are you?"
      - "good morning", "good evening"
    """
    # 1. Regex: catch repeated-char variants like "hii", "hiii", "heyyy"
    #    Check on raw (stripped) query before any lowering/normalization
    raw_stripped = query.strip()
    if _GREETING_REPEATED_CHAR_RE.match(raw_stripped):
        return True

    normalized = _normalize_query(query)

    # 2. Exact match (normalized, punctuation stripped)
    if normalized in _GREETING_EXACT:
        return True

    # 3. Prefix match
    if normalized.startswith(_GREETING_PREFIXES):
        return True

    # 4. Substring + length cap
    for phrase, max_len in _GREETING_SUBSTRINGS:
        if phrase in normalized and len(normalized) <= max_len:
            return True

    return False


def _is_resume_request(query: str) -> bool:
    """
    Detect resume/CV download requests.
    Normalizes the query (lowercase, strip punctuation, collapse whitespace)
    then checks against the known resume request phrases.

    Intentionally excludes "what is in your resume" / "tell me about your resume"
    — those are RAG questions, not download requests.
    """
    normalized = _normalize_query(query)
    return any(pattern in normalized for pattern in _RESUME_PATTERNS)


def _is_project_count_query(query_lower: str) -> bool:
    """Detect project-count questions that should return a hardcoded answer."""
    return any(pattern in query_lower for pattern in _PROJECT_COUNT_PATTERNS)


# ─── Main Intent Detection Node ──────────────────────────────────────────────

def intent_detector_node(state: GraphState) -> Dict[str, Any]:
    raw_query = state.get("raw_query", "").strip()
    logger.info(f"[ROUTER] query=\"{raw_query}\"")

    lower = raw_query.lower()

    # ── GUARD 1: Prompt Injection ────────────────────────────────────────────
    if check_prompt_injection(raw_query):
        logger.warning(f"[ROUTER] intent=PROMPT_INJECTION retrieval_skipped=true")
        return {"intent": "PROMPT_INJECTION", "target_collections": []}

    # ── GUARD 2: Credential Request ──────────────────────────────────────────
    if check_credential_request(raw_query):
        logger.warning(f"[ROUTER] intent=CREDENTIAL_REQUEST retrieval_skipped=true")
        return {"intent": "CREDENTIAL_REQUEST", "target_collections": []}

    # ── GUARD 3: Private/Personal Life Request ───────────────────────────────
    if check_private_request(raw_query):
        logger.warning(f"[ROUTER] intent=PRIVATE_REQUEST retrieval_skipped=true")
        return {"intent": "PRIVATE_REQUEST", "target_collections": []}

    # ── GUARD 4: Greeting (MUST be before ALL routing/retrieval) ─────────────
    # This is the primary guard. "hi", "hii", "hello!", "how are you?" etc.
    # are caught here and NEVER reach ChromaDB.
    if _is_greeting(raw_query):
        logger.info(f"[ROUTER] intent=GREETING retrieval_skipped=true")
        return {"intent": "GREETING", "target_collections": []}

    # ── GUARD 4.5: Resume Download Request ───────────────────────────────────
    # Detected BEFORE off-topic check and BEFORE all collection routing.
    # Returns RESUME_REQUEST so the generator serves the PDF metadata directly.
    if _is_resume_request(raw_query):
        logger.info(f"[ROUTER] intent=RESUME_REQUEST retrieval_skipped=true")
        return {"intent": "RESUME_REQUEST", "target_collections": []}

    # ── GUARD 5: Strong Off-Topic ────────────────────────────────────────────
    if any(ind in lower for ind in _STRONG_OFF_TOPIC_PATTERNS):
        logger.info(f"[ROUTER] intent=OFF_TOPIC retrieval_skipped=true")
        return {"intent": "OFF_TOPIC", "target_collections": []}

    # ── GUARD 6: Project Count (deterministic, no RAG needed) ────────────────
    if _is_project_count_query(lower):
        logger.info(f"[ROUTER] intent=PROJECT_COUNT retrieval_skipped=true")
        return {"intent": "PROJECT_COUNT", "target_collections": []}

    # ── ROUTING: Targeted Collection Selection ───────────────────────────────
    collections: List[str] = []

    # Known specific project names
    _PROJECT_NAMES = [
        "mail automation", "email automation",
        "youtube", "youtube assistant", "youtube ai",
        "student portal",
        "digital twin", "personal ai assistant",
    ]

    # Tech/stack keywords — indicate a technology question
    _TECH_KEYWORDS = [
        "technology", "technologies", "tech stack", "stack",
        "tool", "tools", "database", "backend", "frontend",
        "framework", "library", "libraries", "used",
    ]

    is_project_query = any(p in lower for p in _PROJECT_NAMES)
    is_tech_query = any(t in lower for t in _TECH_KEYWORDS)

    if is_project_query and is_tech_query:
        collections = ["projects", "skills"]
    elif is_project_query:
        collections = ["projects"]
    else:
        for col, keywords in _COLLECTION_KEYWORDS.items():
            for kw in keywords:
                if kw in lower:
                    if col not in collections:
                        collections.append(col)
                    break

        for rule in _COMPOUND_ROUTING:
            if any(t in lower for t in rule["triggers"]):
                for target in rule["target_collections"]:
                    if target not in collections:
                        collections.append(target)

    # Limit to 2 collections for sharp targeting
    collections = list(dict.fromkeys(collections))[:2]

    # ── FALLBACK: unmatched queries ───────────────────────────────────────────
    if not collections:
        logger.info(f"[ROUTER] No collection matched — falling back to about_me/resume")
        collections = ["about_me", "resume"]

    logger.info(f"[ROUTER] intent=PERSONAL_INQUIRY collections={collections}")
    return {
        "intent": "PERSONAL_INQUIRY",
        "target_collections": collections,
    }
