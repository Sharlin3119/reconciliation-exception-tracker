# Reconciliation Exception Tracker (RET)

Bank-to-GL reconciliation tool for SME accounting teams. Replaces manual 
spreadsheet workflows with an automated matching engine and audit trail.

## Architecture
Data Sources (CSV / bank API)
  → Ingestion & Normalisation Layer
  → Matching Engine (exact → fuzzy → rule-based)
  → Exception Queue
  → Workflow Engine (assign / resolve / escalate)
  → Audit Log
  → Reporting Dashboard

## Tech Stack
- Backend: Python + FastAPI
- Database: PostgreSQL
- Matching: pandas + rapidfuzz
- Frontend: React + Tailwind
- Billing: Stripe

## Backend status (June 2026)

Implemented so far:

- FastAPI health check (`GET /health`)
- Exception listing (`GET /exceptions`)
- Exception workflow transition (`POST /exceptions/{id}/transition`)
- Audit logging of state changes
- Exact matching engine for bank vs GL transactions
- Matching API (`POST /matching/exact`)
- pytest test suite for matching service and matching API
