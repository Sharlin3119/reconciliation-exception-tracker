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
## Running the backend locally

Prerequisites:
- Python 3.11+
- Git
- Virtualenv or `python -m venv`

### 1. Clone and install

```bash
git clone https://github.com/Sharlin3119/reconciliation-exception-tracker.git
cd reconciliation-exception-tracker/backend

python -m venv .venv
source .venv/bin/activate

pip install -r backend/requirements.txt
```

### 2. Start the API server

From the `backend` directory:

```bash
source .venv/bin/activate
uvicorn app.main:app --reload
```

The API will be available at `http://127.0.0.1:8000`.

Useful URLs:
- Swagger UI: `http://127.0.0.1:8000/docs`
- Health check: `GET http://127.0.0.1:8000/health`

### 3. Run tests

From the `backend` directory:

```bash
source .venv/bin/activate
pytest backend/tests
```

This runs both the matching engine unit tests and the `/matching/exact` API tests.
