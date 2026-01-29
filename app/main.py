from fastapi import FastAPI

app = FastAPI(title="JobIntel")

@app.get("/health")
def health():
    return {"status": "ok"}
