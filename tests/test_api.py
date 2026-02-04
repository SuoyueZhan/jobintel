from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health_endpoint():
    """
    Why:
    - Proves the app boots and routing is alive.
    - Good early indicator of environment/config errors in CI.
    """
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json() == {"ok": True}


def test_analyze_endpoint_negation_regression_case():
    """
    Why:
    - Locks in the exact regression you fixed:
      "No U.S. citizenship required." must NOT become a positive hit because of sentence splitting.
    - This is a high-value, real-world edge case.
    """
    payload = {"text": "No clearance required. No U.S. citizenship required."}
    resp = client.post("/analyze", json=payload)

    assert resp.status_code == 200
    data = resp.json()

    # Schema keys exist and types are stable
    assert set(data.keys()) == {
        "requires_clearance",
        "requires_citizenship",
        "hits",
        "evidence",
    }
    assert isinstance(data["requires_clearance"], bool)
    assert isinstance(data["requires_citizenship"], bool)
    assert isinstance(data["hits"], list)
    assert isinstance(data["evidence"], list)

    # Behavior for this known case
    assert data["requires_clearance"] is False
    assert data["requires_citizenship"] is False


def test_analyze_endpoint_positive_case_contract():
    """
    Why:
    - Confirms successful analysis returns both flags True when text explicitly requires them.
    - Ensures 'hits' and 'evidence' are populated when flags are True.
    """
    payload = {"text": "Security clearance is required. US citizenship is required."}
    resp = client.post("/analyze", json=payload)

    assert resp.status_code == 200
    data = resp.json()

    assert data["requires_clearance"] is True
    assert data["requires_citizenship"] is True
    assert "clearance" in data["hits"]
    assert "citizenship" in data["hits"]
    assert len(data["evidence"]) >= 1


def test_analyze_validation_missing_text_field():
    """
    Why:
    - AnalyzeRequest requires 'text' (Field(...)).
    - FastAPI/Pydantic should reject missing required fields with 422.
    """
    resp = client.post("/analyze", json={})
    assert resp.status_code == 422


def test_analyze_validation_empty_text_rejected():
    """
    Why:
    - Your schema says min_length=1.
    - Empty string should fail validation with 422.
    """
    resp = client.post("/analyze", json={"text": ""})
    assert resp.status_code == 422


def test_analyze_validation_whitespace_text_rejected_or_handled():
    """
    Why:
    - Your rules layer strips text; but schema only enforces min_length, not 'non-whitespace'.
    - This test makes behavior explicit. Right now, " " passes schema (length=1),
      then analyze_jd strips -> empty -> should return false/empty output.

    If you later decide whitespace should be invalid at schema level,
    you'll update this test accordingly.
    """
    resp = client.post("/analyze", json={"text": " "})
    assert resp.status_code == 200
    data = resp.json()
    assert data["requires_clearance"] is False
    assert data["requires_citizenship"] is False
    assert data["hits"] == []
    assert data["evidence"] == []
