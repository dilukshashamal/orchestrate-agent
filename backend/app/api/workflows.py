import json
import uuid
from pathlib import Path
from typing import Any

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.evaluation.scenarios import EVALUATION_SCENARIOS
from app.workflows.supply_chain import create_supply_chain_workflow

router = APIRouter(prefix="/api/v1/workflows", tags=["Workflows"])

MOCK_DIR = Path(__file__).resolve().parent.parent / "data" / "mock"

def _load_json(filename: str) -> Any:
    file_path = MOCK_DIR / filename
    if not file_path.exists():
        return []
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)

# Global in-memory storage for workflow threads in dev mode
WORKFLOW_THREADS: dict[str, dict[str, Any]] = {}

class RunWorkflowRequest(BaseModel):
    po_number: str | None = Field(None, description="PO number to trigger workflow for")
    scenario_id: str | None = Field(None, description="Scenario ID from evaluation scenarios")

class ResumeWorkflowRequest(BaseModel):
    action: str = Field(..., description="Decision action: 'APPROVE' or 'REJECT'")
    comment: str | None = Field(None, description="Optional reviewer notes/comment")

class WorkflowResponse(BaseModel):
    thread_id: str
    po_number: str | None
    approval_status: str
    requires_human_approval: bool
    current_step: str
    state: dict[str, Any]

@router.post("/run", response_model=WorkflowResponse)
async def run_workflow(request: RunWorkflowRequest):
    po_data: dict[str, Any] = {}
    inventory_data: dict[str, Any] = {}
    all_suppliers: list[dict[str, Any]] = _load_json("suppliers.json")
    
    if request.scenario_id:
        for sc in EVALUATION_SCENARIOS:
            sc_dict: dict[str, Any] = sc
            if str(sc_dict.get("scenario_id")).lower() == request.scenario_id.lower():
                po_data = sc_dict.get("po_data", {})
                inventory_data = sc_dict.get("inventory_data", {})
                all_suppliers = sc_dict.get("all_suppliers", [])
                break
    
    if not po_data and request.po_number:
        pos: list[dict[str, Any]] = _load_json("purchase_orders.json")
        for p in pos:
            if str(p.get("po_number")).lower() == request.po_number.lower():
                po_data = p
                break
        
        if po_data:
            inv_items: list[dict[str, Any]] = _load_json("inventory.json")
            for item in inv_items:
                if str(item.get("sku")).lower() == str(po_data.get("item_sku")).lower():
                    inventory_data = item
                    break

    if not po_data:
        # Default fallback to PO-9001
        pos_fallback: list[dict[str, Any]] = _load_json("purchase_orders.json")
        po_data = pos_fallback[0] if pos_fallback else {
            "po_number": "PO-9001",
            "supplier_id": "SUP-001",
            "item_sku": "MAT-101",
            "quantity": 500,
            "unit_price": 120.0,
            "total_value": 60000.0,
            "status": "DELAYED",
            "actual_delay_days": 5
        }
        inv_items_fallback: list[dict[str, Any]] = _load_json("inventory.json")
        inventory_data = inv_items_fallback[0] if inv_items_fallback else {
            "sku": "MAT-101",
            "on_hand_qty": 120,
            "daily_usage_rate": 25,
            "stockout_risk": "HIGH"
        }

    if inventory_data and "stockout_risk" not in inventory_data:
        from app.models.schemas import StockoutRiskRuleInput
        from app.workflows.rules import evaluate_stockout_risk_rule
        daily_usage = inventory_data.get("daily_usage_rate", 1)
        on_hand = inventory_data.get("on_hand_qty", 0)
        countdown = on_hand // daily_usage if daily_usage > 0 else 999
        risk = evaluate_stockout_risk_rule(StockoutRiskRuleInput(stockout_countdown_days=countdown))
        inventory_data["stockout_risk"] = risk.value

    thread_id = f"thread-{po_data['po_number']}-{uuid.uuid4().hex[:8]}"
    config = {"configurable": {"thread_id": thread_id}}
    
    initial_state = {
        "po_data": po_data,
        "inventory_data": inventory_data,
        "all_suppliers": all_suppliers,
        "history": []
    }

    workflow = create_supply_chain_workflow()
    snapshot = await workflow.ainvoke(initial_state, config=config)

    requires_approval = snapshot.get("requires_human_approval", False)
    approval_status = snapshot.get("approval_status", "PENDING" if requires_approval else "AUTO_EXECUTED")
    current_step = snapshot.get("current_step", "unknown")

    result_data = {
        "thread_id": thread_id,
        "po_number": po_data.get("po_number"),
        "approval_status": approval_status,
        "requires_human_approval": requires_approval,
        "current_step": current_step,
        "state": snapshot
    }
    WORKFLOW_THREADS[thread_id] = result_data
    return WorkflowResponse(**result_data)

@router.get("/{thread_id}/state", response_model=WorkflowResponse)
async def get_workflow_state(thread_id: str):
    if thread_id in WORKFLOW_THREADS:
        return WorkflowResponse(**WORKFLOW_THREADS[thread_id])
    
    config = {"configurable": {"thread_id": thread_id}}
    workflow = create_supply_chain_workflow()
    state_snap = await workflow.aget_state(config)
    
    if not state_snap or not state_snap.values:
        raise HTTPException(status_code=404, detail=f"Workflow thread {thread_id} not found.")

    snapshot = state_snap.values
    requires_approval = snapshot.get("requires_human_approval", False)
    approval_status = snapshot.get("approval_status", "PENDING" if requires_approval else "AUTO_EXECUTED")
    po_data = snapshot.get("po_data", {})

    result_data = {
        "thread_id": thread_id,
        "po_number": po_data.get("po_number"),
        "approval_status": approval_status,
        "requires_human_approval": requires_approval,
        "current_step": snapshot.get("current_step", "unknown"),
        "state": snapshot
    }
    WORKFLOW_THREADS[thread_id] = result_data
    return WorkflowResponse(**result_data)

@router.post("/{thread_id}/resume", response_model=WorkflowResponse)
async def resume_workflow(thread_id: str, request: ResumeWorkflowRequest):
    config = {"configurable": {"thread_id": thread_id}}
    workflow = create_supply_chain_workflow()

    user_action = request.action.upper()
    if user_action not in ["APPROVE", "REJECT"]:
        raise HTTPException(status_code=400, detail="Action must be 'APPROVE' or 'REJECT'.")

    new_status = "APPROVED" if user_action == "APPROVE" else "REJECTED"
    
    # 1. Update state snapshot in checkpointer
    try:
        await workflow.aupdate_state(
            config,
            {
                "approval_status": new_status,
                "requires_human_approval": False
            }
        )
        # 2. Resume execution from interrupted node by passing None
        res_snapshot = await workflow.ainvoke(None, config=config)
        final_snapshot = dict(res_snapshot)
    except Exception:
        # Fallback for mock memory threads
        state_data = WORKFLOW_THREADS.get(thread_id, {})
        final_snapshot = dict(state_data.get("state", {}))
        final_snapshot["approval_status"] = "EXECUTED" if user_action == "APPROVE" else "REJECTED"
        final_snapshot["requires_human_approval"] = False

    po_data = final_snapshot.get("po_data", {})
    result_data = {
        "thread_id": thread_id,
        "po_number": po_data.get("po_number"),
        "approval_status": final_snapshot.get("approval_status", "EXECUTED"),
        "requires_human_approval": False,
        "current_step": final_snapshot.get("current_step", "execution_node"),
        "state": final_snapshot
    }
    WORKFLOW_THREADS[thread_id] = result_data
    return WorkflowResponse(**result_data)
