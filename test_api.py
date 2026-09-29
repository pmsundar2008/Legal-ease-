from unittest.mock import patch
from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)

def test_root():
    r = client.get("/")
    assert r.status_code == 200
    assert r.json()["status"] == "running"

def test_health():
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"

@patch("backend.routes.GeminiDocumentGenerator")
def test_generate(mock_generator):
    mock_generator.return_value.generate_document.return_value = (
        "NON-DISCLOSURE AGREEMENT\n\n1. Confidentiality\n"
        "The parties agree to keep information confidential."
    )
    r = client.post("/generate", json={
        "document_type": "Non-Disclosure Agreement",
        "parties": "Alice (Disclosing Party), Example Ltd (Receiving Party)",
        "terms": "Confidentiality; 2-year term",
        "effective_date": "2026-04-15",
    })
    assert r.status_code == 200
    assert "NON-DISCLOSURE AGREEMENT" in r.json()["content"]

def test_txt_export():
    r = client.post("/export/txt", json={"content": "Hello", "document_type": "Agreement"})
    assert r.status_code == 200
    assert r.content == b"Hello\n"

def test_docx_export():
    r = client.post("/export/docx", json={
        "content": "AGREEMENT\n\n1. Terms\nHello",
        "document_type": "Agreement",
        "terms": "Payment within 30 days; Confidentiality",
    })
    assert r.status_code == 200
    assert r.content[:2] == b"PK"

def test_pdf_export():
    r = client.post("/export/pdf", json={
        "content": "AGREEMENT\n\n1. Terms\nHello",
        "document_type": "Agreement",
    })
    assert r.status_code == 200
    assert r.content.startswith(b"%PDF")
