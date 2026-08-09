from fastapi import APIRouter
from app.schemas.chat_schema import SuggestionsResponse

router = APIRouter()

@router.get("/suggestions", response_model=SuggestionsResponse)
async def get_suggested_questions():
    return SuggestionsResponse(
        suggestions=[
            "Tell me about your projects",
            "Tell me about your AI Mail Automation project",
            "What technologies do you use?",
            "What are your strongest technical skills?",
            "Tell me about your AI experience",
            "Explain your Personal AI Assistant",
            "How does your RAG system work?",
            "What is your experience with Django?",
            "What is your experience with FastAPI?",
            "What kind of roles are you looking for?",
            "How can I contact you?"
        ]
    )
