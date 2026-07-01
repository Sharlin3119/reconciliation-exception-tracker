import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.health import router as health_router
from app.api.exceptions import router as exceptions_router
from app.api.matching import router as matching_router
from app.api.rules import router as rules_router
from app.api.reporting import router as reporting_router
from app.api.billing import router as billing_router
from app.api.files import router as files_router
from app.db import engine
from app.models import Base

app = FastAPI(
    title="Reconciliation Exception Tracker",
    description="Bank-to-GL reconciliation tool for SME accounting teams.",
    version="0.1.0",
)

_cors_origins = os.getenv("CORS_ORIGINS", "http://localhost:5173").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=_cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

Base.metadata.create_all(bind=engine)

app.include_router(health_router)
app.include_router(exceptions_router)
app.include_router(matching_router)
app.include_router(rules_router)
app.include_router(reporting_router)
app.include_router(billing_router)
app.include_router(files_router)
