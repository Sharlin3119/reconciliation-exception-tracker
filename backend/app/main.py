from fastapi import FastAPI

app = FastAPI(
    title="Reconciliation Exception Tracker",
    description="Bank-to-GL reconciliation tool for SME accounting teams.",
    version="0.1.0",
)

@app.get("/health")
def health_check():
    return {"status": "ok"}