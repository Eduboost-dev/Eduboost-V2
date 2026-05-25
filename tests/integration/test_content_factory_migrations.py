"""tests/integration/test_content_factory_migrations.py
─────────────────────────────────────────────────────────────────────────────
Verifies that after `alembic upgrade head` runs the Content Factory tables
and their key columns are present in the live database. Requires a real
database connection (uses the `db_session` fixture from the root conftest).
─────────────────────────────────────────────────────────────────────────────
"""
from __future__ import annotations

import pytest
import pytest_asyncio
from sqlalchemy import inspect, text

pytestmark = pytest.mark.integration


REQUIRED_TABLES = [
    "content_generation_artifacts",
    "content_artifact_sources",
    "content_generation_runs",
    "content_generation_tasks",
    "content_seed_runs",
    "content_promotion_events",
    "lesson_bank",
    "assessment_blueprints",
    "study_plan_templates",
]

# Spot-check columns in the two tables that received the most schema expansion
REQUIRED_SOURCE_COLUMNS = [
    "source_document_id",
    "source_chunk_id",
    "license_status",
    "source_quality_score",
]

REQUIRED_TASK_COLUMNS = [
    "idempotency_key",
    "depends_on_task_ids",
    "validation_failures",
    "token_usage",
]


@pytest.mark.asyncio
async def test_content_factory_tables_exist(db_session):
    """All Content Factory tables must be present after migration."""

    def _check(conn):
        inspector = inspect(conn)
        existing = set(inspector.get_table_names())
        missing = [t for t in REQUIRED_TABLES if t not in existing]
        return missing

    async with db_session.bind.connect() as conn:
        missing = await conn.run_sync(_check)

    assert not missing, f"Missing Content Factory tables: {missing}"


@pytest.mark.asyncio
async def test_content_artifact_sources_columns(db_session):
    """content_artifact_sources must have provenance columns."""

    def _check(conn):
        inspector = inspect(conn)
        cols = {c["name"] for c in inspector.get_columns("content_artifact_sources")}
        return [c for c in REQUIRED_SOURCE_COLUMNS if c not in cols]

    async with db_session.bind.connect() as conn:
        missing = await conn.run_sync(_check)

    assert not missing, (
        f"content_artifact_sources missing columns: {missing}"
    )


@pytest.mark.asyncio
async def test_content_generation_tasks_columns(db_session):
    """content_generation_tasks must have ledger columns."""

    def _check(conn):
        inspector = inspect(conn)
        cols = {c["name"] for c in inspector.get_columns("content_generation_tasks")}
        return [c for c in REQUIRED_TASK_COLUMNS if c not in cols]

    async with db_session.bind.connect() as conn:
        missing = await conn.run_sync(_check)

    assert not missing, (
        f"content_generation_tasks missing columns: {missing}"
    )


@pytest.mark.asyncio
async def test_content_generation_artifacts_unique_hash(db_session):
    """artifact_hash column must have a unique index."""

    def _check(conn):
        inspector = inspect(conn)
        unique_constraints = inspector.get_unique_constraints(
            "content_generation_artifacts"
        )
        indexes = inspector.get_indexes("content_generation_artifacts")

        has_unique = any(
            "artifact_hash" in c.get("column_names", [])
            for c in unique_constraints
        ) or any(
            "artifact_hash" in idx.get("column_names", []) and idx.get("unique")
            for idx in indexes
        )
        return has_unique

    async with db_session.bind.connect() as conn:
        has_unique = await conn.run_sync(_check)

    assert has_unique, "content_generation_artifacts.artifact_hash must have a unique constraint"
