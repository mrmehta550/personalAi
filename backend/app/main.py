import os
import sys

# Ensure backend root directory is in sys.path when running `python app/main.py` directly
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.core.logger import logger
from app.api.v1.router import api_router
from app.seed.seed_ingest import seed_knowledge_base

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Enterprise-grade Digital Twin Persona Agent powered by LangGraph, ChromaDB, and FastAPI.",
    version="1.0.0",
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Routers
app.include_router(api_router, prefix=settings.API_V1_STR)

@app.on_event("startup")
async def startup_event():
    logger.info(f"Starting {settings.PROJECT_NAME}...")
    try:
        # Seed initial portfolio knowledge base data across collections
        seed_knowledge_base()
    except Exception as e:
        logger.error(f"Error during startup seed ingestion: {e}")

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
