try:
    from langchain_huggingface import HuggingFaceEmbeddings
except ImportError:
    from langchain_community.embeddings import HuggingFaceEmbeddings

from app.core.config import settings
from app.core.logger import logger

_embedding_instance = None

def get_embedding_model():
    global _embedding_instance
    if _embedding_instance is None:
        logger.info(f"Loading embedding model: {settings.EMBEDDING_MODEL_NAME}")
        try:
            _embedding_instance = HuggingFaceEmbeddings(
                model_name=settings.EMBEDDING_MODEL_NAME,
                model_kwargs={'device': 'cpu'},
                encode_kwargs={'normalize_embeddings': True}
            )
            logger.info("Embedding model loaded successfully.")
        except Exception as e:
            logger.error(f"Failed to load HuggingFace embedding model: {e}. Falling back to default sentence-transformers model.")
            _embedding_instance = HuggingFaceEmbeddings(
                model_name="sentence-transformers/all-MiniLM-L6-v2",
                model_kwargs={'device': 'cpu'},
                encode_kwargs={'normalize_embeddings': True}
            )
    return _embedding_instance
