from __future__ import annotations

from fastapi.testclient import TestClient

from app.api_v2 import app


def _ms_from_header(value: str) -> float:
    # Expect format like '123.4ms'
    try:
        return float(value.rstrip("ms"))
    except Exception:
        return float("inf")


def test_root_latency():
    client = TestClient(app)
    r = client.get("/")
    assert r.status_code == 200
    header = r.headers.get("X-Response-Time")
    assert header is not None
    assert _ms_from_header(header) < 500.0


def test_health_latency():
    client = TestClient(app)
    r = client.get("/health")
    assert r.status_code == 200
    header = r.headers.get("X-Response-Time")
    assert header is not None
    assert _ms_from_header(header) < 500.0
