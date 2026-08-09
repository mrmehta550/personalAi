from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

class ChatRequest(BaseModel):
    thread_id: str = Field(..., description="Unique thread/session ID")
    message: str = Field(..., description="User query message")
    stream: bool = Field(True, description="Enable SSE token streaming")

class SourceItem(BaseModel):
    collection: str
    source: Optional[str] = None
    content_snippet: str

class ChatResponse(BaseModel):
    thread_id: str
    message: str
    intent: str
    collections: List[str]
    sources: List[SourceItem] = []
    is_grounded: bool = True

class SuggestionsResponse(BaseModel):
    suggestions: List[str]
