from fastapi import FastAPI
from app.api.health import router as health_router

app = FastAPI(
    title="Reconciliation Exception Tracker",
    description="Bank-to-GL reconciliation tool for SME accounting teams.",
    version="0.1.0",
)

app.include_router(health_router)