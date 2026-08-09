from fastapi import APIRouter
from app.api.v1.endpoints import chat, kb, health, suggestions, resume

api_router = APIRouter()
api_router.include_router(health.router, tags=["Health"])
api_router.include_router(chat.router, tags=["Chat Engine"])
api_router.include_router(kb.router, tags=["Knowledge Base"])
api_router.include_router(suggestions.router, tags=["Suggestions"])
api_router.include_router(resume.router, tags=["Resume"])

