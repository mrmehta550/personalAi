import os
from typing import List
from pydantic_settings import BaseSettings
from pydantic import ConfigDict


class Settings(BaseSettings):
    model_config = ConfigDict(env_file=".env", case_sensitive=True)

    PROJECT_NAME: str = "Personal AI Assistant ('Digital Twin')"
    API_V1_STR: str = "/api/v1"

    # Owner & Persona details — set via environment variables in .env
    # NEVER hardcode real personal identity here.
    OWNER_NAME: str = os.getenv("OWNER_NAME", "Vishal Kumar")
    OWNER_TITLE: str = os.getenv("OWNER_TITLE", "Python & AI Developer")

    # Storage & DB
    CHROMA_PERSIST_DIR: str = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "data", "chroma"
    )
    SQLITE_MEMORY_DB: str = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "data", "memory.db"
    )

    # Models & Embeddings
    # Embeddings are always local (BAAI/bge-base-en-v1.5) — not configurable via HF token
    EMBEDDING_MODEL_NAME: str = "BAAI/bge-base-en-v1.5"
    EMBEDDING_DIMENSION: int = 768

    # Hugging Face LLM settings — configured via .env, never hardcoded
    HF_TOKEN: str = os.getenv("HF_TOKEN", "")
    # HF_MODEL is the primary env var (HF_MODEL_REPO kept as legacy alias)
    HF_MODEL: str = os.getenv("HF_MODEL", os.getenv("HF_MODEL_REPO", "mistralai/Mistral-7B-Instruct-v0.2"))
    # Optional LLM generation parameters
    HF_TEMPERATURE: float = float(os.getenv("HF_TEMPERATURE", "0.3"))
    HF_MAX_TOKENS: int = int(os.getenv("HF_MAX_TOKENS", "512"))

    # Collections — all 12 domain collections for the knowledge base
    COLLECTIONS: List[str] = [
        "about_me",
        "resume",
        "projects",
        "experience",
        "skills",
        "certificates",
        "blogs",
        "github",
        "linkedin",
        "faqs",
        "services",
        "contact_info"
    ]

    # CORS & Security
    CORS_ORIGINS: List[str] = ["http://localhost:5173", "http://localhost:3000", "http://localhost:8080", "*"]
    RATE_LIMIT_PER_MINUTE: int = 30


settings = Settings()
