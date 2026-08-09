import os
import tempfile
from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from app.ingest.loader import DocumentLoader
from app.ingest.splitter import split_documents
from app.vectorstore.collection_manager import collection_manager
from app.schemas.kb_schema import CollectionStatsResponse, UploadDocumentResponse
from app.core.config import settings
from app.core.logger import logger

router = APIRouter()

@router.get("/kb/collections", response_model=CollectionStatsResponse)
async def get_collections_stats():
    stats = collection_manager.get_collection_stats()
    total = sum(stats.values())
    return CollectionStatsResponse(
        collections=stats,
        total_documents=total
    )

@router.post("/documents/upload", response_model=UploadDocumentResponse)
async def upload_document(
    file: UploadFile = File(...),
    collection_name: str = Form("about_me")
):
    if collection_name not in settings.COLLECTIONS:
        raise HTTPException(status_code=400, detail=f"Invalid collection name: {collection_name}")

    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in [".pdf", ".docx", ".txt", ".md"]:
        raise HTTPException(status_code=400, detail=f"Unsupported file format '{ext}'. Allowed: .pdf, .docx, .txt, .md")

    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=ext) as tmp:
            content = await file.read()
            tmp.write(content)
            tmp_path = tmp.name

        raw_docs = DocumentLoader.load_file(tmp_path, file.filename)
        chunks = split_documents(raw_docs, collection_name=collection_name)
        count = collection_manager.add_documents(collection_name, chunks)

        os.remove(tmp_path)

        return UploadDocumentResponse(
            filename=file.filename,
            collection_name=collection_name,
            chunks_created=count,
            status="success"
        )
    except Exception as e:
        logger.error(f"Upload document error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
