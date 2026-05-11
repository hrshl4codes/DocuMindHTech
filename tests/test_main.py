import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from fastapi.testclient import TestClient
from documind_main import create_app


@pytest.fixture(scope="module")
def client():
    return TestClient(create_app())


# ── /health ──────────────────────────────────────────────────

def test_health_ok(client):
    resp = client.get("/health")
    assert resp.status_code == 200
    body = resp.json()
    assert body["status"] == "healthy"
    assert body["system"] == "documind"


def test_api_health_ok(client):
    resp = client.get("/api/health")
    assert resp.status_code == 200
    assert resp.json()["status"] == "healthy"


# ── /api/upload ───────────────────────────────────────────────

_upload_ok = {"success": True, "document_id": "mock-doc-id", "chunks_created": 1}


def test_upload_text_success(client):
    with patch("services.routes.api_service") as mock_svc:
        mock_svc.upload_document = AsyncMock(return_value=_upload_ok)
        resp = client.post("/api/upload", data={"text": "Hello world document content."})
    assert resp.status_code == 200
    body = resp.json()
    assert body["success"] is True
    assert "document_id" in body


def test_upload_no_input_returns_400(client):
    resp = client.post("/api/upload", data={})
    assert resp.status_code == 400


def test_upload_file_txt(client):
    with patch("services.routes.api_service") as mock_svc:
        mock_svc.upload_document = AsyncMock(return_value=_upload_ok)
        resp = client.post(
            "/api/upload",
            files={"file": ("doc.txt", b"Plain text file content.", "text/plain")},
        )
    assert resp.status_code == 200
    assert resp.json()["success"] is True


def test_upload_file_too_large_returns_413(client):
    oversized = b"x" * (51 * 1024 * 1024)  # 51 MB
    resp = client.post(
        "/api/upload",
        files={"file": ("big.txt", oversized, "text/plain")},
    )
    assert resp.status_code == 413


# ── /api/query ────────────────────────────────────────────────

def test_query_missing_fields_returns_422(client):
    resp = client.post("/api/query", json={})
    assert resp.status_code == 422


def test_query_empty_question_returns_400(client):
    resp = client.post("/api/query", json={"document_id": "abc", "question": "  "})
    assert resp.status_code == 400


def test_query_success(client):
    _query_ok = {"success": True, "answer": "This document is about testing.", "citations": []}
    with patch("services.routes.api_service") as mock_svc:
        mock_svc.query_document = AsyncMock(return_value=_query_ok)
        resp = client.post(
            "/api/query",
            json={"document_id": "mock-doc-id", "question": "What is this document about?"},
        )
    assert resp.status_code == 200
    body = resp.json()
    assert body["success"] is True
    assert "answer" in body


def test_query_invalid_json_returns_422(client):
    resp = client.post(
        "/api/query",
        content=b"not-json",
        headers={"Content-Type": "application/json"},
    )
    assert resp.status_code == 422
