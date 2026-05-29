"""tests/unit/test_json_completion.py
Unit tests for JsonCompletionGateway and helpers (no network calls).
"""
from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.services.llm.json_completion import (
    JsonCompletionError,
    JsonCompletionGateway,
    parse_json_response,
)


@pytest.mark.unit
def test_parse_json_response_accepts_fenced_markdown():
    raw = """
    ```json
    {"a": 1, "b": 2}
    ```
    """.strip()
    parsed = parse_json_response(raw)
    assert parsed == {"a": 1, "b": 2}


@pytest.mark.unit
def test_parse_json_response_raises_on_invalid_json():
    with pytest.raises(JsonCompletionError, match="not valid JSON"):
        parse_json_response("{" )


@pytest.mark.unit
async def test_complete_uses_mock_provider_when_configured(monkeypatch):
    # Arrange settings
    from app.core import config
    monkeypatch.setattr(config.settings, "LLM_PROVIDER", "mock", raising=False)

    gw = JsonCompletionGateway()
    resp = await gw.complete(prompt="give me correct_answer")
    assert resp.provider == "mock"
    assert "correct_answer" in resp.content


@pytest.mark.unit
async def test_google_path_success(monkeypatch):
    from app.core import config
    # minimal viable settings
    monkeypatch.setattr(config.settings, "LLM_PROVIDER", "google", raising=False)
    monkeypatch.setattr(config.settings, "GOOGLE_API_KEY", "k", raising=False)
    monkeypatch.setattr(config.settings, "GOOGLE_MODEL", "models/gemini-pro", raising=False)
    monkeypatch.setattr(config.settings, "LLM_TIMEOUT_SECONDS", 5, raising=False)

    payload = {
        "usageMetadata": {"promptTokenCount": 12, "candidatesTokenCount": 34},
        "candidates": [
            {"content": {"parts": [{"text": "{\"ok\": true}"}]}}
        ],
    }

    with patch("httpx.AsyncClient") as mock_client, \
         patch("app.services.llm.json_completion.record_llm_tokens") as mock_record:
        mock_response = MagicMock()
        mock_response.json.return_value = payload
        mock_response.raise_for_status.return_value = None
        mock_client.return_value.__aenter__.return_value.post = AsyncMock(return_value=mock_response)

        gw = JsonCompletionGateway()
        resp = await gw.complete(prompt="hi", system="s")

        assert resp.provider == "google"
        assert resp.model == "gemini-pro"
        assert resp.content == "{\"ok\": true}"
        mock_record.assert_called_once()


@pytest.mark.unit
async def test_google_requires_api_key(monkeypatch):
    from app.core import config
    monkeypatch.setattr(config.settings, "LLM_PROVIDER", "google", raising=False)
    monkeypatch.setattr(config.settings, "GOOGLE_API_KEY", "", raising=False)

    gw = JsonCompletionGateway()
    with pytest.raises(JsonCompletionError, match="Google Gemini API key not configured"):
        await gw.complete(prompt="p")


@pytest.mark.unit
async def test_groq_requires_api_key(monkeypatch):
    from app.core import config
    monkeypatch.setattr(config.settings, "LLM_PROVIDER", "groq", raising=False)
    monkeypatch.setattr(config.settings, "GROQ_API_KEY", "", raising=False)

    gw = JsonCompletionGateway()
    with pytest.raises(JsonCompletionError, match="Groq API key not configured"):
        await gw.complete(prompt="p")


@pytest.mark.unit
async def test_anthropic_requires_api_key(monkeypatch):
    from app.core import config
    monkeypatch.setattr(config.settings, "LLM_PROVIDER", "anthropic", raising=False)
    monkeypatch.setattr(config.settings, "ANTHROPIC_API_KEY", "", raising=False)

    gw = JsonCompletionGateway()
    with pytest.raises(JsonCompletionError, match="Anthropic API key not configured"):
        await gw.complete(prompt="p")


@pytest.mark.unit
async def test_fallback_collects_errors_when_no_provider_configured(monkeypatch):
    from app.core import config
    # Ensure explicit provider is unset; emulate no keys so fallback will gather none
    monkeypatch.setattr(config.settings, "LLM_PROVIDER", "unknown", raising=False)
    monkeypatch.setattr(config.settings, "GOOGLE_API_KEY", "", raising=False)
    monkeypatch.setattr(config.settings, "GROQ_API_KEY", "", raising=False)
    monkeypatch.setattr(config.settings, "ANTHROPIC_API_KEY", "", raising=False)

    gw = JsonCompletionGateway()
    with pytest.raises(JsonCompletionError, match="No JSON LLM provider succeeded"):
        await gw.complete(prompt="p")
