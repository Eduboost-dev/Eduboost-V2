from __future__ import annotations

import os

import pytest

pytestmark = pytest.mark.integration


def _dsn() -> str:
    return os.getenv("AUTH_REFRESH_DB_PROOF_DSN", "").strip()


def test_auth_refresh_db_proof_requires_explicit_dsn():
    assert _dsn(), "AUTH_REFRESH_DB_PROOF_DSN must be set for DB-backed proof"


@pytest.mark.asyncio
async def test_refresh_persistence_logout_revoke_reuse_db_proof_contract():
    """Intentional live-DB proof placeholder.

    This test must only pass when wired to a real disposable DB fixture. It must
    not skip, because skipped DB proof is false proof.
    """

    assert os.getenv("AUTH_REFRESH_DB_PROOF_ENABLED") == "1"
    assert _dsn(), "DB proof DSN missing"
    assert False, (
        "Implement DB-backed assertions for refresh persistence, logout revocation, "
        "revoke-all, and reuse detection before accepting AUTH-REFRESH-DB-PROOF-001."
    )
