import json
from pathlib import Path

from fastapi import APIRouter
from pydantic import BaseModel, Field

from app.api.workflows import WORKFLOW_THREADS
from app.evaluation.metrics import EvaluationMetrics, compute_evaluation_metrics

router = APIRouter(prefix="/api/v1/dashboard", tags=["Dashboard"])

MOCK_DIR = Path(__file__).resolve().parent.parent / "data" / "mock"

def _load_json(filename: str):
    file_path = MOCK_DIR / filename
    if not file_path.exists():
        return []
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)

class DashboardSummaryResponse(BaseModel):
    stockout_risk_count: int = Field(..., description="Number of materials with HIGH stockout risk")
    delayed_orders_count: int = Field(..., description="Number of purchase orders currently DELAYED")
    pending_approvals_count: int = Field(..., description="Number of workflows pending human approval")
    auto_executed_pos_count: int = Field(..., description="Number of auto-approved POs")
    agent_accuracy: EvaluationMetrics = Field(..., description="Evaluation benchmark metrics")

@router.get("", response_model=DashboardSummaryResponse)
async def get_dashboard_kpis():
    inventory_raw = _load_json("inventory.json")
    pos_raw = _load_json("purchase_orders.json")

    # Count high stockout risk
    stockout_risk_count = 0
    for item in inventory_raw:
        daily_usage = item.get("daily_usage_rate", 1)
        on_hand = item.get("on_hand_qty", 0)
        countdown = on_hand // daily_usage if daily_usage > 0 else 999
        if countdown < 7:
            stockout_risk_count += 1

    # Count delayed orders
    delayed_orders_count = sum(1 for po in pos_raw if po.get("status") == "DELAYED")

    # Count pending approvals & auto executed POs from active threads or mock data
    pending_approvals = sum(
        1 for t in WORKFLOW_THREADS.values() if t.get("approval_status") == "PENDING"
    )
    if pending_approvals == 0:
        # Default mock count
        pending_approvals = 1

    auto_executed = sum(
        1 for t in WORKFLOW_THREADS.values() if t.get("approval_status") in ["AUTO_EXECUTED", "EXECUTED"]
    )
    if auto_executed == 0:
        auto_executed = 2

    # Compute evaluation metrics
    metrics = await compute_evaluation_metrics()

    return DashboardSummaryResponse(
        stockout_risk_count=stockout_risk_count,
        delayed_orders_count=delayed_orders_count,
        pending_approvals_count=pending_approvals,
        auto_executed_pos_count=auto_executed,
        agent_accuracy=metrics
    )
