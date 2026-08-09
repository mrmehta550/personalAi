from typing import Dict, List, Any
from pydantic import BaseModel

class CollectionStatsResponse(BaseModel):
    collections: Dict[str, int]
    total_documents: int

class UploadDocumentResponse(BaseModel):
    filename: str
    collection_name: str
    chunks_created: int
    status: str
