"""
Integration Tests: FastAPI Endpoints
------------------------------------
Tests API routes for eCourts Scraper and Legal Draft Generator.
"""

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_health_endpoint():
    res = client.get("/health")
    assert res.status_code == 200
    assert res.json()["status"] == "ok"


def test_index_dashboard():
    res = client.get("/")
    assert res.status_code == 200
    assert "VakeelAI" in res.text
    assert "eCourts Scraper" in res.text


def test_drafting_templates_endpoint():
    res = client.get("/api/drafting/templates")
    assert res.status_code == 200
    templates = res.json()
    assert len(templates) >= 5


def test_drafting_generation_and_export():
    payload = {
        "template_id": "commercial_suit",
        "court_name": "IN THE COURT OF DISTRICT JUDGE (COMMERCIAL COURT) AT SAKET, NEW DELHI",
        "case_type_number_year": "CS (COMM) NO. 233 OF 2024",
        "cnr_number": "DLST010047302024",
        "plaintiffs": [{"name": "Punjab National Bank", "address": "Saket, New Delhi"}],
        "defendants": [{"name": "Sunil Kumar", "address": "Saket, New Delhi"}],
        "total_claim_amount": 2450000.0,
        "facts": [{"date": "10-05-2024", "narrative": "Credit defaulted"}],
    }
    # Test JSON generation
    res_gen = client.post("/api/drafting/generate", json=payload)
    assert res_gen.status_code == 200
    data = res_gen.json()
    assert "PUNJAB NATIONAL BANK" in data["plain_text"]

    # Test DOCX export
    res_docx = client.post("/api/drafting/export/docx", json=payload)
    assert res_docx.status_code == 200
    assert len(res_docx.content) > 10000


def test_cnr_search_api():
    res = client.post(
        "/api/ecourts/search/cnr",
        json={"cnr_number": "DLST010047302024", "use_resilience_fallback": True},
    )
    assert res.status_code == 200
    data = res.json()
    assert data["cnr_number"] == "DLST010047302024"
    assert "CS (COMM)" in data["case_details"]["case_type"]


def test_case_number_search_api():
    payload = {
        "state_code": "26",
        "dist_code": "10",
        "court_complex_code": "1260011@1,2,3,4@Y",
        "est_code": "1",
        "case_type": "77^1",
        "case_no": "233",
        "year": "2024",
        "use_resilience_fallback": True,
    }
    res = client.post("/api/ecourts/search/case-number", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data.get("case") is not None
    assert data["case"]["cnr_number"] == "DLST010047302024"

