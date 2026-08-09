# Supply Chain Exception Agent — System Architecture & Guidelines

## Architecture Overview
The Supply Chain Exception Agent handles real-time supply chain disruptions (shipping delays, stockout risks, supplier capacity bottlenecks) by combining a deterministic rules engine with LLM agent decision nodes in a LangGraph StateGraph.

## Non-Negotiable Architecture Rules
1. **Deterministic Core Policy (`backend/app/workflows/rules.py`)**:
   - MUST be a pure-Python, LLM-free policy engine.
   - All critical business logic, financial limits, threshold checks, and approval policy decisions MUST be executed by deterministic code in `rules.py`.
   - Agent nodes in LangGraph invoke `rules.py` functions to validate decisions. Agent nodes do NOT re-implement or override financial or policy thresholds inline.
2. **Key Financial & Operational Thresholds (Baseline Rules)**:
   - `supplier_delay > 3 days AND stockout_risk == HIGH` -> `create_exception_case`
   - `alternative_supplier_available AND production_impact == HIGH` -> `evaluate_alternative_supplier`
   - `purchase_value > $50,000` -> `human_approval_required` (Human Approval Threshold)
   - `purchase_value < $10,000 AND supplier_is_preapproved` -> `auto_create_PO` (Preapproval Threshold)
   - `stockout_countdown < 7 days` -> `HIGH` severity stockout risk
3. **API Conventions**:
   - All REST API endpoints must be mounted under `/api/v1/`.
   - Structured JSON inputs and responses typed with Pydantic models.
4. **LangGraph State & Interrupts**:
   - Workflow is managed via LangGraph `StateGraph`.
   - Uses `interrupt_before` for nodes flagged by `rules.py` as requiring human approval.
   - State persistence powered by `MemorySaver` checkpointer.
5. **LLM Provider Redundancy**:
   - Primary LLM: Groq (`langchain-groq`).
   - Fallback LLM: Cerebras on same model weights (`gpt-oss-120b`).
   - Rate limits handled via standard exponential backoff.

## 5 Agent Roles
1. **Monitoring Agent**: Scans ERP / Logistics stream for delays and potential disruptions.
2. **Impact Analysis Agent**: Assesses inventory depletion, financial impact, and stockout timelines.
3. **Supplier Intelligence Agent**: Queries mock supplier database for alternative sourcing, lead times, capacity, and ratings.
4. **Procurement Agent**: Generates expedited POs or re-routes existing POs following rule engine checks.
5. **Logistics Agent**: Calculates alternative freight routes (air vs ocean) and transit timelines.

## Tech Stack
- **Backend**: Python 3.11.5+, FastAPI, LangGraph + LangChain, Groq as primary LLM provider with Cerebras fallback (`gpt-oss-120b`), PostgreSQL via Docker, Kafka for event stream (optional in dev), Redis + Celery for background jobs, LangSmith for tracing, pytest + pytest-asyncio, Ruff + Mypy strict.
- **Frontend**: Next.js 16 (App Router), React 19, TypeScript 5.9+ strict, Tailwind CSS v4, shadcn/ui, Tremor + Recharts, TanStack Table v8, React Hook Form + Zod, Zustand, Lucide React, Framer Motion.

## Directory Structure
```
supply-chain-agent/
├── docker-compose.yml, Makefile, .env.example
├── backend/
│   ├── requirements.txt, Dockerfile
│   └── app/
│       ├── main.py, config.py
│       ├── api/            (erp, procurement, logistics, workflows, dashboard)
│       ├── core/           (llm.py, embeddings, security)
│       ├── models/         (schemas.py, enums.py)
│       ├── services/       (inventory_service, supplier_service, impact_calculator)
│       ├── workflows/      (supply_chain.py LangGraph, nodes.py, rules.py)
│       ├── agents/         (monitoring, impact, supplier_intel, procurement, logistics)
│       ├── rag/            (knowledge_base, retriever)
│       ├── evaluation/     (scenarios, metrics)
│       └── data/           (mock/*.json, policies/*.pdf)
├── backend/tests/
└── frontend/
    ├── Dockerfile
    └── src/
        ├── app/            (Command Center, exceptions/, approvals/, suppliers/, analytics/, settings/)
        ├── components/     (ui/, layout/, dashboard/, exceptions/, charts/)
        └── hooks/, lib/, types/, store/
```

## UI & Design System Guidelines
- **Theme**: Dark mode default (control-room usage).
- **Color Semantics**: Red (Critical / High Stockout Risk), Amber (Warning / Pending Approval), Green (Healthy / Auto-executed), Blue (Informational / In-flight).
- **Progressive Disclosure**: Summary cards -> Detail drawers -> Full workflow view.
- **Views**:
  - Command Center (`/`): KPI Cards, Exception Timeline, Supplier Health & Inventory charts.
  - Exception Detail (`/exceptions/[id]`): Detailed impact, visual LangGraph step graph, recommendation panel, approval action buttons.
  - Approval Queue (`/approvals`): Kanban Board (Pending / Reviewed / Approved / Rejected) with bulk pre-approval actions for low-value POs.

## Verification Bar For Every Task
1. Run relevant backend tests and show actual output.
2. Any rules-engine change requires a test in `backend/tests/test_rules.py` first.
3. Any frontend change with visible UI impact: use browser tool to load the page and capture screenshots.
4. Any LangGraph workflow change: verify graph compiles and runs end-to-end scenario.
