from fastapi import FastAPI
from app.api.health import router as health_router
from app.api.exceptions import router as exceptions_router
from app.api.matching import router as matching_router
from app.db import engine
from app.models import Base

app = FastAPI(
    title="Reconciliation Exception Tracker",
    description="Bank-to-GL reconciliation tool for SME accounting teams.",
    version="0.1.0",
)

Base.metadata.create_all(bind=engine)

app.include_router(health_router)
app.include_router(exceptions_router)
app.include_router(matching_router)