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

## Live Demo
[Link coming soon — hosted on Render + Vercel]
