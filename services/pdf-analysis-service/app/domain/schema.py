from __future__ import annotations

from datetime import UTC, datetime
from typing import Literal

from pydantic import BaseModel, Field


class BoundingBox(BaseModel):
    x0: float
    y0: float
    x1: float
    y1: float


class TextBlock(BaseModel):
    id: str
    bbox: BoundingBox
    text: str
    confidence: float = Field(ge=0.0, le=1.0)
    source: Literal["embedded_text", "ocr"]


class TableCell(BaseModel):
    row: int
    col: int
    text: str
    bbox: BoundingBox | None = None


class TableBlock(BaseModel):
    id: str
    bbox: BoundingBox | None = None
    cells: list[TableCell] = Field(default_factory=list)
    confidence: float = Field(ge=0.0, le=1.0)


class PageAnalysis(BaseModel):
    page_number: int
    width: float
    height: float
    blocks: list[TextBlock] = Field(default_factory=list)
    tables: list[TableBlock] = Field(default_factory=list)
    quality_flags: list[str] = Field(default_factory=list)


class AnalysisError(BaseModel):
    code: str
    message: str
    recoverable: bool = True


class AnalysisResult(BaseModel):
    schema_version: str
    document_id: str
    analyzed_at: datetime
    runtime: dict[str, str | bool | int | float | None]
    pages: list[PageAnalysis]
    errors: list[AnalysisError] = Field(default_factory=list)
    quality_flags: list[str] = Field(default_factory=list)

    @classmethod
    def new(
        cls,
        *,
        schema_version: str,
        document_id: str,
        runtime: dict[str, str | bool | int | float | None],
        pages: list[PageAnalysis],
        errors: list[AnalysisError],
        quality_flags: list[str],
    ) -> "AnalysisResult":
        return cls(
            schema_version=schema_version,
            document_id=document_id,
            analyzed_at=datetime.now(UTC),
            runtime=runtime,
            pages=pages,
            errors=errors,
            quality_flags=quality_flags,
        )
