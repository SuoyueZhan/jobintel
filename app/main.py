import hashlib
from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session

from app.schemas import AnalyzeRequest, AnalyzeResponse
from app.rules import analyze_jd
from app.db import get_db
from app.models import AnalysisRecord

app = FastAPI(title="JobIntel", version="0.1")


@app.get("/health")
def health():
    return {"ok": True}


def _normalize_text(text: str) -> str:
    # Simple normalization so hashing is stable across minor whitespace differences
    return " ".join((text or "").split())


def _sha256_hex(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


@app.post("/analyze", response_model=AnalyzeResponse)
def analyze(req: AnalyzeRequest, db: Session = Depends(get_db)):
    """
    Input JSON:
      { "text": "..." }

    Output JSON (stable schema):
      {
        "requires_clearance": bool,
        "requires_citizenship": bool,
        "hits": [...],
        "evidence": [...]
      }

    Side effect (Week 3):
      Save an analysis record into Postgres.
    """
    result = analyze_jd(req.text)

    normalized = _normalize_text(req.text)
    text_hash = _sha256_hex(normalized)
    text_preview = normalized[:200] if normalized else ""

    rec = AnalysisRecord(
        text_hash=text_hash,
        requires_clearance=bool(result["requires_clearance"]),
        requires_citizenship=bool(result["requires_citizenship"]),
        hits=list(result.get("hits", [])),
        evidence=list(result.get("evidence", [])),
        text_preview=text_preview,
        raw_text=None,  # keep privacy-friendly for now
    )
    try:
        db.add(rec)
        db.commit()
    except Exception:
        # DB might not be running (e.g., CI). Keep API behavior stable.
        db.rollback()

    return result
