from __future__ import annotations

import io
import logging
import os
import uuid

import fitz

from app.core.version import ANALYSIS_SCHEMA_VERSION
from app.domain.schema import (
    AnalysisError,
    AnalysisResult,
    BoundingBox,
    PageAnalysis,
    TableBlock,
    TextBlock,
)

logger = logging.getLogger(__name__)


class PDFAnalyzer:
    def __init__(self, min_text_chars: int = 60) -> None:
        self.min_text_chars = min_text_chars

    def analyze(self, pdf_bytes: bytes, document_id: str | None = None) -> AnalysisResult:
        assigned_document_id = document_id or str(uuid.uuid4())
        errors: list[AnalysisError] = []
        doc_quality_flags: list[str] = []

        try:
            pdf = fitz.open(stream=pdf_bytes, filetype="pdf")
        except Exception as exc:
            raise ValueError(f"invalid_pdf: {exc}") from exc

        pages: list[PageAnalysis] = []
        total_text_chars = 0
        ocr_used = False
        ocr_available = self._ocr_is_available()

        for page_idx, page in enumerate(pdf):
            page_no = page_idx + 1
            blocks: list[TextBlock] = []
            tables: list[TableBlock] = []
            page_quality_flags: list[str] = []

            for block_idx, block in enumerate(page.get_text("blocks")):
                text = (block[4] or "").strip()
                if not text:
                    continue
                blocks.append(
                    TextBlock(
                        id=f"p{page_no}-b{block_idx}",
                        bbox=BoundingBox(x0=block[0], y0=block[1], x1=block[2], y1=block[3]),
                        text=text,
                        confidence=0.99,
                        source="embedded_text",
                    )
                )
                total_text_chars += len(text)

            if not blocks:
                page_quality_flags.append("no_embedded_text")

            for table_idx, table in enumerate(page.find_tables().tables):
                extracted = table.extract() or []
                cells = []
                for row_idx, row in enumerate(extracted):
                    for col_idx, cell in enumerate(row):
                        if cell:
                            cells.append(
                                {
                                    "row": row_idx,
                                    "col": col_idx,
                                    "text": str(cell).strip(),
                                }
                            )
                tables.append(
                    TableBlock(
                        id=f"p{page_no}-t{table_idx}",
                        bbox=BoundingBox(
                            x0=table.bbox[0],
                            y0=table.bbox[1],
                            x1=table.bbox[2],
                            y1=table.bbox[3],
                        ),
                        cells=cells,
                        confidence=0.85,
                    )
                )

            if not blocks and ocr_available:
                ocr_text = self._run_ocr(page)
                if ocr_text:
                    blocks.append(
                        TextBlock(
                            id=f"p{page_no}-ocr0",
                            bbox=BoundingBox(x0=0.0, y0=0.0, x1=page.rect.width, y1=page.rect.height),
                            text=ocr_text,
                            confidence=0.65,
                            source="ocr",
                        )
                    )
                    total_text_chars += len(ocr_text)
                    ocr_used = True
                else:
                    page_quality_flags.append("ocr_no_text_detected")
            elif not blocks and not ocr_available:
                errors.append(
                    AnalysisError(
                        code="ocr_not_available",
                        message="OCR fallback requested but pytesseract/tesseract is unavailable.",
                        recoverable=True,
                    )
                )

            pages.append(
                PageAnalysis(
                    page_number=page_no,
                    width=page.rect.width,
                    height=page.rect.height,
                    blocks=blocks,
                    tables=tables,
                    quality_flags=page_quality_flags,
                )
            )

        if total_text_chars < self.min_text_chars:
            doc_quality_flags.append("low_text_coverage")

        runtime = {
            "ocr_engine": "pytesseract" if ocr_available else "none",
            "ocr_used": ocr_used,
            "gpu_mode": os.getenv("OCR_DEVICE", "cpu") == "gpu",
            "page_count": len(pages),
        }

        return AnalysisResult.new(
            schema_version=ANALYSIS_SCHEMA_VERSION,
            document_id=assigned_document_id,
            runtime=runtime,
            pages=pages,
            errors=errors,
            quality_flags=doc_quality_flags,
        )

    @staticmethod
    def _ocr_is_available() -> bool:
        try:
            import pytesseract  # noqa: F401
            from PIL import Image  # noqa: F401

            return True
        except Exception:
            return False

    @staticmethod
    def _run_ocr(page: fitz.Page) -> str:
        try:
            import pytesseract
            from PIL import Image
        except Exception:
            return ""

        pix = page.get_pixmap(dpi=300)
        image = Image.open(io.BytesIO(pix.tobytes("png")))
        try:
            return pytesseract.image_to_string(image).strip()
        except Exception as exc:
            logger.warning("OCR failed: %s", exc)
            return ""
