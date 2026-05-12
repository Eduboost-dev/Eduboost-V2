from __future__ import annotations
import pytest
pytestmark = pytest.mark.integration


import pytest_asyncio


@pytest_asyncio.fixture
async def seed_consent():
    """Compatibility fixture placeholder for older integration tests."""
    yield
