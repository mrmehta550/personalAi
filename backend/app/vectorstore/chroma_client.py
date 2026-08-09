import os
import chromadb
from chromadb.config import Settings as ChromaSettings
from app.core.config import settings
from app.core.logger import logger

class ChromaClientManager:
    _instance = None

    @classmethod
    def get_client(cls):
        if cls._instance is None:
            os.makedirs(settings.CHROMA_PERSIST_DIR, exist_ok=True)
            logger.info(f"Initializing ChromaDB Persistent Client at {settings.CHROMA_PERSIST_DIR}")
            cls._instance = chromadb.PersistentClient(
                path=settings.CHROMA_PERSIST_DIR,
                settings=ChromaSettings(anonymized_telemetry=False, allow_reset=True)
            )
            # Ensure standard collections exist
            for col_name in settings.COLLECTIONS:
                cls._instance.get_or_create_collection(
                    name=col_name,
                    metadata={"hnsw:space": "cosine"}
                )
        return cls._instance

def get_chroma_client():
    return ChromaClientManager.get_client()
