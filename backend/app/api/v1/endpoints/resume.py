"""
Resume PDF delivery endpoint.

Serves the configured resume PDF securely.
Only the single configured resume file can be returned — no arbitrary paths.

Place the actual PDF here:
    backend/app/static/resume/Vishal_Kumar_Resume.pdf
"""
import os
from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from app.core.logger import logger

router = APIRouter()

# ── Configured resume file — only this file can ever be served ───────────────
_RESUME_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "static", "resume"
)
_RESUME_FILENAME = "Vishal_Kumar_Resume.pdf"
_RESUME_PATH = os.path.join(_RESUME_DIR, _RESUME_FILENAME)


@router.get("/resume", summary="Download Vishal Kumar's Resume PDF")
async def get_resume():
    """
    Serves the portfolio owner's resume PDF.
    Only the configured PDF can be returned — no arbitrary file paths are possible.
    """
    if not os.path.isfile(_RESUME_PATH):
        logger.warning(
            f"[RESUME] PDF not found at expected path: {_RESUME_PATH}. "
            f"Please place the file at: backend/app/static/resume/{_RESUME_FILENAME}"
        )
        raise HTTPException(
            status_code=404,
            detail=(
                f"Resume PDF not available yet. "
                f"Please place '{_RESUME_FILENAME}' at: "
                f"backend/app/static/resume/{_RESUME_FILENAME}"
            )
        )

    logger.info(f"[RESUME] Serving {_RESUME_FILENAME}")
    return FileResponse(
        path=_RESUME_PATH,
        media_type="application/pdf",
        filename=_RESUME_FILENAME,
        headers={
            "Content-Disposition": f'inline; filename="{_RESUME_FILENAME}"',
            "Cache-Control": "no-store",
        }
    )
