from __future__ import annotations

from fastapi import APIRouter, File, Form, HTTPException, UploadFile

from app.domain.analyzer import PDFAnalyzer

router = APIRouter()
analyzer = PDFAnalyzer()


@router.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@router.post("/analyze")
async def analyze_pdf(
    file: UploadFile = File(...),
    document_id: str | None = Form(default=None),
) -> dict:
    if file.content_type not in {"application/pdf", "application/octet-stream"}:
        raise HTTPException(status_code=400, detail="file must be a PDF")

    payload = await file.read()
    if not payload:
        raise HTTPException(status_code=400, detail="empty file")

    try:
        result = analyzer.analyze(payload, document_id=document_id)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    return result.model_dump(mode="json")
