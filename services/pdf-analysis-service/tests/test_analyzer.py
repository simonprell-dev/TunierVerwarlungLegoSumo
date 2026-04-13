import fitz

from app.domain.analyzer import PDFAnalyzer


def _pdf_with_text(text: str) -> bytes:
    doc = fitz.open()
    page = doc.new_page()
    page.insert_text((72, 72), text)
    return doc.tobytes()


def test_analyzer_returns_versioned_schema() -> None:
    analyzer = PDFAnalyzer()
    result = analyzer.analyze(_pdf_with_text("Hallo BauDoc"), document_id="doc-123")

    assert result.schema_version == "1.0.0"
    assert result.document_id == "doc-123"
    assert result.pages
    assert result.pages[0].blocks[0].source == "embedded_text"


def test_quality_flag_for_low_text_coverage() -> None:
    analyzer = PDFAnalyzer(min_text_chars=999)
    result = analyzer.analyze(_pdf_with_text("kurz"))

    assert "low_text_coverage" in result.quality_flags
