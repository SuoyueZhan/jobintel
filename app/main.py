from fastapi import FastAPI
from app.schemas import AnalyzeRequest, AnalyzeResponse
from app.rules import analyze_jd

app = FastAPI(title="JobIntel", version="0.1")


@app.get("/health")
def health():
    return {"ok": True}


@app.post("/analyze", response_model=AnalyzeResponse)
def analyze(req: AnalyzeRequest):
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
    """
    return analyze_jd(req.text)
