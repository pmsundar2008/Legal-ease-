from fastapi import APIRouter, HTTPException
from fastapi.responses import Response

from backend.config import get_settings
from backend.schemas import DocumentRequest, ExportRequest, GenerateResponse
from backend.ai_core.gemini_generator import GeminiDocumentGenerator
from backend.services.exporters import format_docx, format_pdf, format_txt

router = APIRouter()
settings = get_settings()

@router.get("/health")
def health():
    return {
        "status": "ok",
        "service": settings.app_name,
        "gemini_configured": bool(settings.gemini_api_key),
    }

@router.post("/generate", response_model=GenerateResponse)
def generate_document(request: DocumentRequest):
    try:
        generator = GeminiDocumentGenerator(settings)
        content = generator.generate_document(
            request.document_type, request.parties, request.terms, request.effective_date
        )
        return GenerateResponse(
            document_type=request.document_type,
            content=content,
            model=settings.gemini_model,
        )
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"Document generation failed: {exc}") from exc

@router.post("/export/txt")
def export_txt(request: ExportRequest):
    return Response(
        content=format_txt(request.content),
        media_type="text/plain; charset=utf-8",
        headers={"Content-Disposition": 'attachment; filename="legalease_document.txt"'},
    )

@router.post("/export/docx")
def export_docx(request: ExportRequest):
    try:
        data = format_docx(request.content, request.document_type, request.terms, request.logo_base64)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return Response(
        content=data,
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        headers={"Content-Disposition": 'attachment; filename="legalease_document.docx"'},
    )

@router.post("/export/pdf")
def export_pdf(request: ExportRequest):
    try:
        data = format_pdf(request.content, request.document_type, request.logo_base64)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return Response(
        content=data,
        media_type="application/pdf",
        headers={"Content-Disposition": 'attachment; filename="legalease_document.pdf"'},
    )
