from fastapi import FastAPI
from app.api.health import router as health_router
from app.db import engine
from app.models import Base

app = FastAPI(
    title="Reconciliation Exception Tracker",
    description="Bank-to-GL reconciliation tool for SME accounting teams.",
    version="0.1.0",
)

Base.metadata.create_all(bind=engine)

app.include_router(health_router)