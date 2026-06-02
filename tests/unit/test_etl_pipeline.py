"""Unit tests for ETL pipeline modules (Phases 0–7 and v3 helpers)."""
from __future__ import annotations

from pathlib import Path

import pytest

from app.services.etl.etl_pipeline import (
    ChunkType,
    Chunker,
    Document,
    DocumentType,
    EduboostETL,
    ExtractionResult,
    Extractor,
    IngestRequest,
    LicenseStatus,
    Normalizer,
    ProcessingStatus,
    QualityCheckResult,
    QualityValidator,
    SourceType,
    _sha256,
    _token_count,
    _uid,
)
from app.services.etl.etl_pipeline_v3_additions import EduboostETLv3


def _sample_document(**overrides) -> Document:
    base = dict(
        document_id="doc-1",
        source_id="src-1",
        title="Grade 4 Mathematics",
        description="",
        document_type=DocumentType.textbook.value,
        subject="mathematics",
        grade=4,
        phase="Intermediate Phase",
        curriculum="CAPS",
        country="ZA",
        province=None,
        language="en",
        publisher=None,
        author=None,
        publication_year=2024,
        version="1.0",
        license_status=LicenseStatus.open_license.value,
        source_url=None,
        checksum="abc123",
        file_path_raw="/tmp/sample.txt",
        file_size_bytes=100,
        page_count=1,
        mime_type="text/plain",
        processing_status=ProcessingStatus.raw.value,
        quality_score=0.0,
        training_readiness=False,
        created_at="2026-01-01T00:00:00+00:00",
        updated_at="2026-01-01T00:00:00+00:00",
    )
    base.update(overrides)
    return Document(**base)


@pytest.mark.unit
def test_token_count_minimum_one():
    assert _token_count("") == 1
    assert _token_count("abcd") == 1
    assert _token_count("a" * 40) == 10


@pytest.mark.unit
def test_uid_and_sha256_helpers(tmp_path: Path):
    sample = tmp_path / "sample.txt"
    sample.write_text("hello etl", encoding="utf-8")
    digest = _sha256(str(sample))
    assert len(digest) == 64
    assert _uid() != _uid()


@pytest.mark.unit
def test_normalizer_cleans_ocr_and_page_artifacts():
    normalizer = Normalizer()
    noisy = "Page 1 of 10\n\nGrade  4   maths\nLO123 content here."
    result = normalizer.normalize(noisy, DocumentType.textbook.value)
    assert "Page 1 of 10" not in result["normalized_text"]
    assert result["language"] == "en"
    assert "LO123" in result["curriculum_codes"]


@pytest.mark.unit
def test_normalizer_detects_afrikaans():
    normalizer = Normalizer()
    text = "die van is en dat het nie met die skool"
    assert normalizer._detect_language(text) == "af"


@pytest.mark.unit
def test_normalizer_infer_metadata_fills_grade_and_subject():
    normalizer = Normalizer()
    doc = _sample_document(subject=None, grade=None, title="Untitled", publication_year=None)
    text = "Grade 5 mathematics workbook for 2023 CAPS curriculum."
    updates = normalizer.infer_metadata(text, doc)
    assert updates.get("grade") == 5
    assert updates.get("subject") == "mathematics"
    assert updates.get("publication_year") == 2023
    assert updates.get("phase") == "Intermediate Phase"


@pytest.mark.unit
def test_chunker_generic_produces_paragraph_chunks():
    chunker = Chunker()
    text = "First paragraph.\n\nSecond paragraph with more words.\n\nThird paragraph."
    chunks = chunker.chunk(text, DocumentType.unknown.value, "doc-1")
    assert len(chunks) >= 1
    assert all(c.document_id == "doc-1" for c in chunks)
    assert all(c.token_count >= 1 for c in chunks)


@pytest.mark.unit
def test_chunker_assessment_splits_questions():
    chunker = Chunker()
    text = "Introduction\n\nQuestion 1\nWhat is 2+2?\n\nQuestion 2\nWhat is 3+3?"
    chunks = chunker.chunk(text, DocumentType.past_paper.value, "doc-2")
    assert any(c.chunk_type == ChunkType.assessment_question.value for c in chunks)


@pytest.mark.unit
def test_extractor_txt_reads_markdown_headings(tmp_path: Path):
    path = tmp_path / "lesson.md"
    path.write_text("# Fractions\n\n## Adding fractions\n\nContent here.", encoding="utf-8")
    result = Extractor().extract(str(path))
    assert result.extraction_ok is True
    assert "Fractions" in result.headings
    assert "Adding fractions" in result.raw_text


@pytest.mark.unit
def test_quality_validator_scores_well_formed_document():
    doc = _sample_document()
    extraction = ExtractionResult(
        raw_text="x" * 2000,
        pages=[{"page_num": 1, "text": "x", "headings": ["H"]}],
        tables=[],
        headings=["H"],
        page_count=2,
        mime_type="text/plain",
        ocr_confidence=None,
        extraction_ok=True,
    )
    chunker = Chunker()
    chunks = chunker.chunk(extraction.raw_text, doc.document_type, doc.document_id)
    result = QualityValidator().validate(doc, chunks, extraction)
    assert isinstance(result, QualityCheckResult)
    assert result.quality_score > 0.4
    assert result.status in {
        ProcessingStatus.validated.value,
        ProcessingStatus.needs_review.value,
        ProcessingStatus.rejected.value,
    }


@pytest.mark.unit
def test_quality_check_compute_composite():
    score = QualityCheckResult.compute_composite(1.0, 1.0, 1.0, 1.0, 1.0, 1.0)
    assert score == pytest.approx(1.0)


@pytest.mark.unit
def test_eduboost_etl_init_db_and_ingest_txt(tmp_path: Path):
    db_path = tmp_path / "etl.db"
    storage = tmp_path / "data"
    sample = tmp_path / "caps.txt"
    sample.write_text("Grade 4 mathematics fractions unit.", encoding="utf-8")

    etl = EduboostETL(db_url=f"sqlite:///{db_path}", storage_root=str(storage))
    etl.init_db()
    try:
        doc = etl.ingest(
            IngestRequest(
                file_path=str(sample),
                source_type=SourceType.manual_upload.value,
                uploaded_by="tester",
                document_type=DocumentType.textbook.value,
                grade=4,
                subject="mathematics",
            )
        )
        assert doc.document_id
        assert doc.checksum
        assert Path(doc.file_path_raw).exists()
    finally:
        etl.close()


@pytest.mark.unit
def test_eduboost_etlv3_audit_trail(tmp_path: Path):
    db_path = tmp_path / "etl_v3.db"
    storage = tmp_path / "data_v3"
    etl = EduboostETLv3(db_url=f"sqlite:///{db_path}", storage_root=str(storage))
    etl.init_db()
    try:
        entry = etl._record_audit(
            document_id="doc-audit",
            action="metadata_update",
            performed_by="reviewer@test.com",
            field_name="title",
            old_value="Old",
            new_value="New",
        )
        trail = etl.get_audit_trail("doc-audit")
        assert len(trail) == 1
        assert trail[0]["audit_id"] == entry.audit_id
        assert trail[0]["action"] == "metadata_update"
    finally:
        etl.close()
