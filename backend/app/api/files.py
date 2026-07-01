import csv
import io
import os
from datetime import date
from decimal import Decimal, InvalidOperation
from typing import List

from fastapi import APIRouter, Depends, File, Header, UploadFile
from sqlalchemy.orm import Session

from app.db import get_db
from app.models.recon_exception import ReconException
from app.services.matching_engine import TransactionRecord
from app.services.pipeline import run_pipeline

router = APIRouter(prefix="/files", tags=["files"])

ALLOWED_EXTENSIONS = {".pdf", ".xls", ".xlsx", ".doc", ".docx"}


@router.post("/upload")
async def upload_files(files: List[UploadFile] = File(...)):
    results = []
    for f in files:
        ext = os.path.splitext(f.filename or "")[1].lower()
        results.append({"filename": f.filename, "allowed": ext in ALLOWED_EXTENSIONS})
    return {"files": results}


def _parse_csv(text: str) -> tuple[list[TransactionRecord], list[TransactionRecord]]:
    """Parse a reconciliation CSV into (bank_records, gl_records).

    Expected header columns (case-insensitive): external_id, date, amount,
    description, source. `external_id` is the join key the matching engine uses,
    so a bank and a GL row only match when they share it. `source` routes each
    row: "bank" -> bank side, anything else -> GL side. `date` is ISO
    (YYYY-MM-DD). Rows missing a required field or with an unparseable
    amount/date are skipped (demo-grade parsing, not production validation).
    """
    bank: list[TransactionRecord] = []
    gl: list[TransactionRecord] = []
    reader = csv.DictReader(io.StringIO(text))
    for row in reader:
        norm = {(k or "").strip().lower(): (v or "").strip() for k, v in row.items()}
        ext, amount, day = norm.get("external_id"), norm.get("amount"), norm.get("date")
        if not ext or not amount or not day:
            continue
        try:
            rec = TransactionRecord(
                external_id=ext,
                amount=Decimal(amount),
                transaction_date=date.fromisoformat(day),
                source=norm.get("source") or None,
                description=norm.get("description") or None,
            )
        except (InvalidOperation, ValueError):
            continue
        (bank if (norm.get("source") or "").lower() == "bank" else gl).append(rec)
    return bank, gl


@router.post("/run_matching_from_upload")
async def run_matching_from_upload(
    files: List[UploadFile] = File(...),
    x_tenant_id: str = Header(default="dev"),
    db: Session = Depends(get_db),
):
    """Parse uploaded reconciliation CSV(s), run the matching pipeline, and
    persist an Open exception for every unmatched record. Created exceptions are
    tenant-scoped so they surface through the existing /exceptions and
    /reporting APIs. No run is persisted yet, so run_id is null."""
    bank: list[TransactionRecord] = []
    gl: list[TransactionRecord] = []
    for f in files:
        b, g = _parse_csv((await f.read()).decode("utf-8", errors="replace"))
        bank.extend(b)
        gl.extend(g)

    result = run_pipeline(bank, gl)
    matched = (
        len(result.confirmed_matches)
        + len(result.probable_matches)
        + len(result.possible_matches)
    )
    unmatched = list(result.unmatched_bank) + list(result.unmatched_gl)

    for rec in unmatched:
        db.add(ReconException(
            tenant_id=x_tenant_id,
            exception_type="Unmatched",
            amount_difference=rec.amount,
            status="Open",
        ))
    db.commit()

    return {
        "total_transactions": len(bank) + len(gl),
        "matched": matched,
        "exceptions_created": len(unmatched),
        "run_id": None,
    }
