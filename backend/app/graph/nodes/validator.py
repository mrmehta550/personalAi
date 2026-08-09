import re
from typing import Dict, Any
from app.graph.state import GraphState
from app.core.config import settings
from app.core.logger import logger

# Intents that are already pre-validated static responses — skip validation
_SKIP_VALIDATION_INTENTS = {
    "GREETING",
    "OFF_TOPIC",
    "PRIVATE_REQUEST",
    "CREDENTIAL_REQUEST",
    "PROMPT_INJECTION",
}

# Third-person violation patterns (case-insensitive)
_THIRD_PERSON_PATTERNS = [
    r"\bhe (is|has|was|works|built|created|developed|studied|knows|uses|worked)\b",
    r"\bshe (is|has|was|works|built|created|developed|studied|knows|uses|worked)\b",
    r"\bthey (are|have|were|work|built|created|developed|studied|know|use|worked)\b",
    r"\bthe (author|developer|candidate|applicant|person) (is|has|built|created)\b",
    r"\bvishal (is|has|was|works|built|created|developed|studied|knows|uses|worked)\b",
]


def validator_node(state: GraphState) -> Dict[str, Any]:
    intent = state.get("intent", "PERSONAL_INQUIRY")
    llm_response = state.get("llm_raw_response", "")

    logger.info(f"Executing validator_node for intent '{intent}'")

    # Pre-validated static responses don't need further validation
    if intent in _SKIP_VALIDATION_INTENTS:
        return {"is_grounded": True, "final_response": llm_response}

    # ── First-person validation ───────────────────────────────────────────────
    owner_name = settings.OWNER_NAME
    owner_first = owner_name.split()[0] if owner_name else ""
    response_lower = llm_response.lower()

    violations_found = []

    # Check dynamic owner name references in third person
    if owner_name and owner_name.lower() in response_lower:
        # e.g. "Vishal Kumar built..." → should be "I built..."
        violations_found.append(("owner_name_third_person", owner_name))

    # Check standard third-person pronoun patterns
    for pattern in _THIRD_PERSON_PATTERNS:
        if re.search(pattern, response_lower, re.IGNORECASE):
            violations_found.append(("pronoun_violation", pattern))

    if not violations_found:
        return {"is_grounded": True, "final_response": llm_response}

    # ── Correction ───────────────────────────────────────────────────────────
    logger.warning(f"Third-person violations detected: {violations_found}. Correcting response.")
    corrected = llm_response

    # Fix owner name references
    if owner_name:
        corrected = re.sub(
            rf"\b{re.escape(owner_name)}\b",
            "I",
            corrected,
            flags=re.IGNORECASE
        )
    if owner_first:
        # Fix "Vishal built" → "I built" but avoid over-matching
        corrected = re.sub(
            rf"\b{re.escape(owner_first)} (is|has|was|works|built|created|developed|studied|knows|uses)\b",
            r"I \1",
            corrected,
            flags=re.IGNORECASE
        )

    # Fix pronoun violations
    replacements = [
        (r"\bHe (is|has)\b", r"I \1"),
        (r"\bHe (was)\b", r"I \1"),
        (r"\bHe (works|worked|built|created|developed|studied|knows|uses)\b", r"I \1"),
        (r"\bShe (is|has)\b", r"I \1"),
        (r"\bShe (was)\b", r"I \1"),
        (r"\bShe (works|worked|built|created|developed|studied|knows|uses)\b", r"I \1"),
        (r"\bThey (are|have)\b", r"I \1"),
        (r"\bThey (were)\b", r"I was"),
        (r"\bthe (author|developer|candidate|applicant) (is|has|built|was)\b", r"I \2"),
        (r"\bHis\b", "My"),
        (r"\bHer\b", "My"),
        (r"\bTheir\b", "My"),
    ]

    for pattern, replacement in replacements:
        corrected = re.sub(pattern, replacement, corrected, flags=re.IGNORECASE)

    logger.info(f"Corrected response (first 100 chars): '{corrected[:100]}'")
    return {"is_grounded": True, "final_response": corrected}
