from app.services.content_factory import ContentValidationService, ETLProvenanceService


def test_source_bundle_requires_approved_etl_source() -> None:
    result = ETLProvenanceService().validate_source_bundle(
        caps_ref="4.M.1.1",
        sources=[
            {
                "source_document_id": "doc-1",
                "source_chunk_id": "chunk-1",
                "caps_ref": "4.M.1.1",
                "document_status": "needs_review",
                "license_status": "government_open",
                "chunk_quality_score": 0.9,
            }
        ],
    )

    assert not result.passed
    assert "approved, indexed, or training_ready" in result.errors[0]


def test_source_bundle_accepts_training_ready_source_and_hashes_snapshot() -> None:
    result = ETLProvenanceService().validate_source_bundle(
        caps_ref="4.M.1.1",
        sources=[
            {
                "source_document_id": "doc-1",
                "source_chunk_id": "chunk-1",
                "curriculum_mapping_id": "map-1",
                "caps_ref": "4.M.1.1",
                "document_status": "training_ready",
                "license_status": "government_open",
                "chunk_quality_score": 0.9,
            }
        ],
    )

    assert result.passed
    assert result.errors == []
    assert result.source_snapshot_hash.startswith("sha256:")


def test_validation_blocks_diagnostic_item_without_answer_key() -> None:
    result = ContentValidationService().validate_artifact_payload(
        artifact_json={"stem": "What is 2 + 2?", "safety_status": "passed"},
        caps_ref="4.M.1.1",
        artifact_type="diagnostic_item",
        sources=[
            {
                "source_document_id": "doc-1",
                "source_chunk_id": "chunk-1",
                "caps_ref": "4.M.1.1",
                "document_status": "approved",
                "license_status": "government_open",
                "chunk_quality_score": 0.8,
            }
        ],
    )

    assert not result["passed"]
    assert "answer_key" in result["errors"][0]


def test_content_factory_router_is_registered() -> None:
    from app.api_v2 import ROUTER_REGISTRY

    names = {name for name, _router in ROUTER_REGISTRY}

    assert "content_factory" in names
