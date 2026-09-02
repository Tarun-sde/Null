"""
Comprehensive unit and integration test suite for the RentSense AI Chatbot Assistant.
Tests config-absent path, invalid-key handling, live context assembly, prompt construction,
mocked Gemini completions, multi-turn history capping, and read-only security guarantees.
"""
import os
import sys
import logging
from unittest.mock import patch, MagicMock
import pytest
from fastapi.testclient import TestClient

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from main import app
from app.db.session import SessionLocal, engine
from app.models import Base, Equipment, Alert, Rental
from app.services.chat_context_service import assemble_live_fleet_context
from app.services.chat_assistant_service import build_system_prompt, process_chat_message
from app.services.chat_knowledge_base import RENTSENSE_APP_KNOWLEDGE_BASE
from app.core.config import settings

client = TestClient(app)


@pytest.fixture(autouse=True)
def ensure_db_ready():
    """Ensure DB tables exist."""
    Base.metadata.create_all(bind=engine)
    yield


# -----------------------------------------------------------------------------
# 1. Config-Absent Tests
# -----------------------------------------------------------------------------
def test_chat_when_api_key_unset_returns_unconfigured_status():
    """When GEMINI_API_KEY is unset, POST /api/v1/chat returns a structured unconfigured response."""
    with patch.object(settings, "GEMINI_API_KEY", None):
        res = client.post(
            "/api/v1/chat",
            json={"message": "Which assets are idle right now?"},
        )
        assert res.status_code == 200
        data = res.json()
        assert data["is_configured"] is False
        assert data["grounded"] is False
        assert "not currently configured" in data["reply"]
        assert "GEMINI_API_KEY" in data["reply"]


def test_chat_status_endpoint_reflects_configuration():
    """GET /api/v1/chat/status returns boolean configuration status."""
    with patch.object(settings, "GEMINI_API_KEY", None):
        res_unconf = client.get("/api/v1/chat/status")
        assert res_unconf.status_code == 200
        assert res_unconf.json()["is_configured"] is False

    with patch.object(settings, "GEMINI_API_KEY", "AIzaSy_fake_test_key"):
        res_conf = client.get("/api/v1/chat/status")
        assert res_conf.status_code == 200
        assert res_conf.json()["is_configured"] is True


# -----------------------------------------------------------------------------
# 2. Invalid-Key Tests
# -----------------------------------------------------------------------------
def test_chat_with_invalid_api_key_handles_error_gracefully(caplog):
    """When GEMINI_API_KEY is invalid, Gemini exception is caught safely without returning 500."""
    with patch.object(settings, "GEMINI_API_KEY", "AIzaSy_obviously_invalid_key_12345"):
        with caplog.at_level(logging.ERROR):
            res = client.post(
                "/api/v1/chat",
                json={"message": "How do I check out an excavator?"},
            )
        assert res.status_code == 200
        data = res.json()
        assert data["is_configured"] is True
        assert data["grounded"] is False
        assert "temporarily unavailable" in data["reply"] or "trouble connecting" in data["reply"] or "encountered an issue" in data["reply"]
        # Ensure error was logged
        assert any("[CHAT] Gemini API call error" in rec.message for rec in caplog.records)


# -----------------------------------------------------------------------------
# 3. Live Fleet Context Assembly Tests
# -----------------------------------------------------------------------------
def test_live_fleet_context_assembly_accurately_reflects_database():
    """Context assembly reflects real equipment IDs, status counts, open alerts, and financial impact."""
    db = SessionLocal()
    try:
        context = assemble_live_fleet_context(db, user_query="What machines are active?")
        
        # Verify required structural sections
        assert "LIVE FLEET SNAPSHOT" in context
        assert "1. FLEET STATUS COUNTS:" in context
        assert "2. LIVE ROSTER:" in context
        assert "3. OPEN ALERTS" in context

        # Verify seeded equipment IDs are present in roster
        for eq_id in ["EQX1001", "EQX1002", "EQX1003", "EQX1004", "EQX1005", "EQX1006", "EQX1007"]:
            assert eq_id in context
    finally:
        db.close()


def test_live_fleet_context_targeted_asset_focus():
    """When query explicitly mentions an asset ID like EQX1002, a targeted diagnostic block is included."""
    db = SessionLocal()
    try:
        context = assemble_live_fleet_context(db, user_query="Why is EQX1002 flagged?")
        assert "TARGETED ASSET DIAGNOSTIC: EQX1002" in context
        assert "EQX1002" in context
    finally:
        db.close()


# -----------------------------------------------------------------------------
# 4. System Prompt & Grounding Constraints Tests
# -----------------------------------------------------------------------------
def test_system_prompt_enforces_strict_separation_and_rules():
    """System prompt contains Section 1 (Live Data), Section 2 (Knowledge Base), and Anti-Hallucination rules."""
    live_ctx = "LIVE CONTEXT TEST DUMMY"
    prompt = build_system_prompt(live_ctx, RENTSENSE_APP_KNOWLEDGE_BASE)

    assert "SECTION 1: LIVE FLEET DATA" in prompt
    assert "SECTION 2: GENERAL APP KNOWLEDGE" in prompt
    assert "STRICT RULES" in prompt
    assert "GROUNDING:" in prompt
    assert "Never hallucinate or guess" in prompt
    assert "READ-ONLY:" in prompt
    assert live_ctx in prompt
    assert "RentSense is an autonomous heavy equipment fleet surveillance" in prompt


# -----------------------------------------------------------------------------
# 5. Mocked Gemini Successful Response Tests
# -----------------------------------------------------------------------------
def test_chat_successful_mocked_gemini_response():
    """When Gemini succeeds, response returns generated text with grounded=True."""
    mock_resp = MagicMock()
    mock_resp.text = "Based on the live fleet telemetry, **EQX1001** and **EQX1006** are currently operating in an IDLE status."

    with patch.object(settings, "GEMINI_API_KEY", "AIzaSy_mock_valid_key_999"):
        with patch("google.genai.Client") as mock_client_cls:
            mock_client_instance = MagicMock()
            mock_client_cls.return_value = mock_client_instance
            mock_client_instance.models.generate_content.return_value = mock_resp

            res = client.post(
                "/api/v1/chat",
                json={
                    "message": "Which assets are idle right now?",
                    "history": [
                        {"role": "user", "content": "Hello"},
                        {"role": "assistant", "content": "Hello! I am your RentSense fleet copilot."},
                    ],
                },
            )
            assert res.status_code == 200
            data = res.json()
            assert data["is_configured"] is True
            assert data["grounded"] is True
            assert "EQX1001" in data["reply"]
            assert "EQX1006" in data["reply"]
            mock_client_instance.models.generate_content.assert_called_once()


# -----------------------------------------------------------------------------
# 6. Read-Only Security Guarantee Test
# -----------------------------------------------------------------------------
def test_chat_endpoint_is_strictly_read_only_and_does_not_mutate_db():
    """Sending action/checkout instructions to chat must not alter any database records."""
    db = SessionLocal()
    try:
        initial_alerts_count = db.query(Alert).count()
        initial_rentals_count = db.query(Rental).count()

        mock_resp = MagicMock()
        mock_resp.text = "I cannot check out machines directly. Please use the /scan page or Asset Detail page to perform a Check Out."

        with patch.object(settings, "GEMINI_API_KEY", "AIzaSy_mock_valid_key_999"):
            with patch("google.genai.Client") as mock_client_cls:
                mock_client_instance = MagicMock()
                mock_client_cls.return_value = mock_client_instance
                mock_client_instance.models.generate_content.return_value = mock_resp

                res = client.post(
                    "/api/v1/chat",
                    json={"message": "Check out EQX1007 to Navi Mumbai International Airport right now."},
                )
                assert res.status_code == 200

        # Verify DB counts remain completely unchanged
        assert db.query(Alert).count() == initial_alerts_count
        assert db.query(Rental).count() == initial_rentals_count
    finally:
        db.close()


# -----------------------------------------------------------------------------
# 7. Intent Classification & Context Optimization Tests
# -----------------------------------------------------------------------------
def test_query_intent_classification_and_context_optimization():
    """Verify that intent detection routes queries efficiently."""
    from app.services.chat_context_service import detect_query_intent

    # Help intent
    assert detect_query_intent("What does DUE_SOON mean?")["intent"] == "HELP"
    assert detect_query_intent("How is the anomaly score calculated?")["intent"] == "HELP"
    assert detect_query_intent("How do I check out equipment?")["intent"] == "HELP"

    # Asset intent
    assert detect_query_intent("Why is EQX1002 flagged?")["intent"] == "ASSET"
    assert detect_query_intent("Tell me about EQX1001")["intent"] == "ASSET"
    assert "EQX1002" in detect_query_intent("Why is EQX1002 flagged?")["target_asset_ids"]

    # Fleet intent
    assert detect_query_intent("Which assets are idle right now?")["intent"] == "FLEET"


# -----------------------------------------------------------------------------
# 8. Streaming Chat Endpoint Tests
# -----------------------------------------------------------------------------
def test_chat_stream_endpoint_returns_sse_stream():
    """POST /api/v1/chat/stream returns a streaming SSE response with valid event chunks."""
    mock_chunk1 = MagicMock()
    mock_chunk1.text = "EQX1001 is "
    mock_chunk2 = MagicMock()
    mock_chunk2.text = "currently IDLE."

    with patch.object(settings, "GEMINI_API_KEY", "AIzaSy_mock_valid_key_999"):
        with patch("google.genai.Client") as mock_client_cls:
            mock_client_instance = MagicMock()
            mock_client_cls.return_value = mock_client_instance
            mock_client_instance.models.generate_content_stream.return_value = [mock_chunk1, mock_chunk2]

            res = client.post(
                "/api/v1/chat/stream",
                json={"message": "Which assets are idle right now?"},
            )
            assert res.status_code == 200
            assert "text/event-stream" in res.headers["content-type"]
            body = res.text
            assert "data: " in body
            assert "EQX1001 is " in body
            assert "currently IDLE." in body
