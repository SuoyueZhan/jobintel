# JobIntel (Day 5)

A small FastAPI service that analyzes a job description (JD) text and returns whether it contains
clearance/citizenship language, plus matched evidence sentences.

## Requirements
- Python 3.10+ (3.11+ recommended)
- Linux/WSL is recommended

## Setup (first time)
From the project root:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
Run the API server
source .venv/bin/activate
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
Test in the browser (FastAPI UI)
Open:

http://127.0.0.1:8000/docs

Use POST /analyze and click Try it out.

Test from terminal (curl)
Health check:

curl http://127.0.0.1:8000/health
Analyze:

curl -X POST http://127.0.0.1:8000/analyze \
  -H "Content-Type: application/json" \
  -d '{"text":"Ability to obtain a security clearance is required. US citizenship is required."}'
Expected response shape:

{
  "requires_clearance": true,
  "requires_citizenship": true,
  "hits": ["clearance", "citizenship"],
  "evidence": ["...", "..."]
}
Project structure
app/main.py - FastAPI routes (/health, /analyze)

app/schemas.py - request/response models

app/rules.py - keyword rules + evidence extraction
