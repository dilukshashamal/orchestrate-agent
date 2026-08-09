import json
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field

from app.workflows.supply_chain import create_supply_chain_workflow
from app.workflows.rules import (
    evaluate_disruption_rule,
    evaluate_alternative_supplier_rule,
    evaluate_purchase_approval_rule,
    evaluate_stockout_risk_rule
)
from app.models.enums import StockoutRisk, ImpactLevel, POStatus, RuleAction
from app.models.schemas import DisruptionRuleInput, PurchaseApprovalRuleInput, StockoutRiskRuleInput

router = APIRouter(prefix="/api/v1/workflows", tags=["Workflows & Exceptions"])

MOCK_DIR = Path(__file__).resolve().parent.parent / "data" / "mock"

def _load_json(filename: str):
    file_path = MOCK_DIR / filename
    if not file_path.exists():
        return []
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)

def _save_json(filename: str, data: list):
    file_path = MOCK_DIR / filename
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

class ApprovalDecisionRequest(BaseModel):
    decision: str = Field(..., description="APPROVED or REJECTED")
    reviewer_notes: Optional[str] = "Human decision logged via Command Center Control Room."

class WorkflowRunRequest(BaseModel):
    po_number: str = "PO-9001"
    force_rescan: bool = False

@router.get("/exceptions")
async def get_all_exceptions(severity: Optional[str] = None):
    """Retrieve all active supply chain exception cases with decision metrics."""
    pos = _load_json("purchase_orders.json")
    inventory = _load_json("inventory.json")
    suppliers = _load_json("suppliers.json")
    
    inventory_map = {item["sku"]: item for item in inventory}
    supplier_map = {sup["id"]: sup for sup in suppliers}
    
    exceptions = []
    for po in pos:
        sku = po.get("item_sku")
        inv = inventory_map.get(sku, {})
        sup = supplier_map.get(po.get("supplier_id"), {})
        
        daily_usage = inv.get("daily_usage_rate", 25)
        on_hand = inv.get("on_hand_qty", 100)
        countdown = on_hand // daily_usage if daily_usage > 0 else 999
        risk = evaluate_stockout_risk_rule(StockoutRiskRuleInput(stockout_countdown_days=countdown))
        delay_days = po.get("actual_delay_days", 0)
        
        # Check rule engines
        disruption_eval = evaluate_disruption_rule(DisruptionRuleInput(
            supplier_delay_days=delay_days,
            stockout_risk=risk
        ))
        
        approval_eval = evaluate_purchase_approval_rule(PurchaseApprovalRuleInput(
            purchase_value=po.get("total_value", 0.0),
            supplier_is_preapproved=sup.get("is_preapproved", False)
        ))

        is_critical = risk == StockoutRisk.HIGH or delay_days > 3
        
        # Build comprehensive exception record
        exception_item = {
            "id": f"EXC-{po['po_number']}",
            "po_number": po["po_number"],
            "item_sku": sku,
            "item_name": inv.get("name", "Component Asset"),
            "supplier_id": po["supplier_id"],
            "supplier_name": sup.get("name", "Unknown Supplier"),
            "delay_days": delay_days,
            "on_hand_qty": on_hand,
            "daily_usage_rate": daily_usage,
            "stockout_countdown_days": countdown,
            "stockout_risk": risk.value if hasattr(risk, 'value') else risk,
            "purchase_value": po["total_value"],
            "po_status": po["status"],
            "requires_human_approval": approval_eval.requires_human_approval,
            "disruption_flagged": disruption_eval.action == RuleAction.CREATE_EXCEPTION_CASE or is_critical,
            "severity": "CRITICAL" if is_critical else "WARNING" if approval_eval.requires_human_approval else "INFO",
            "decision_reasons": [
                disruption_eval.reason,
                approval_eval.reason
            ],
            "rule_actions": {
                "disruption_rule": disruption_eval.action.value,
                "purchase_approval_rule": approval_eval.action.value
            },
            "last_updated": datetime.now().isoformat()
        }
        
        if severity:
            if exception_item["severity"].upper() == severity.upper():
                exceptions.append(exception_item)
        else:
            exceptions.append(exception_item)
            
    return exceptions

@router.get("/exceptions/{exception_id}")
async def get_exception_detail(exception_id: str):
    """Fetch deep exception analysis, decision factors, and LangGraph workflow state."""
    po_num = exception_id.replace("EXC-", "").upper()
    pos = _load_json("purchase_orders.json")
    target_po = next((p for p in pos if p["po_number"].upper() == po_num), None)
    
    if not target_po:
        raise HTTPException(status_code=404, detail=f"Exception case {exception_id} not found.")
        
    inventory = _load_json("inventory.json")
    suppliers = _load_json("suppliers.json")
    
    sku = target_po["item_sku"]
    inv = next((i for i in inventory if i["sku"].lower() == sku.lower()), {})
    sup = next((s for s in suppliers if s["id"].lower() == target_po["supplier_id"].lower()), {})
    
    daily_usage = inv.get("daily_usage_rate", 25)
    on_hand = inv.get("on_hand_qty", 120)
    countdown = on_hand // daily_usage if daily_usage > 0 else 999
    risk = evaluate_stockout_risk_rule(StockoutRiskRuleInput(stockout_countdown_days=countdown))
    
    disruption_eval = evaluate_disruption_rule(DisruptionRuleInput(
        supplier_delay_days=target_po.get("actual_delay_days", 0),
        stockout_risk=risk
    ))
    
    approval_eval = evaluate_purchase_approval_rule(PurchaseApprovalRuleInput(
        purchase_value=target_po.get("total_value", 0.0),
        supplier_is_preapproved=sup.get("is_preapproved", False)
    ))
    
    # Run LangGraph workflow engine to build execution snapshot
    graph = create_supply_chain_workflow()
    thread_id = f"thread-exp-{po_num.lower()}"
    config = {"configurable": {"thread_id": thread_id}}
    
    state_input = {
        "po_data": target_po,
        "inventory_data": inv,
        "all_suppliers": suppliers,
        "history": []
    }
    
    snapshot = await graph.ainvoke(state_input, config=config)
    
    # Alternative suppliers evaluation table
    alt_suppliers_eval = []
    for s in suppliers:
        if s["id"] != sup.get("id"):
            is_viable = s.get("capacity_units_per_week", 0) >= target_po.get("quantity", 0)
            alt_suppliers_eval.append({
                **s,
                "is_viable": is_viable,
                "lead_time_delta_days": s.get("lead_time_days", 7) - sup.get("lead_time_days", 14),
                "price_delta": round(s.get("unit_price", 0) - target_po.get("unit_price", 0), 2)
            })
            
    # Decision Factors table explicitly listing baseline thresholds
    decision_factors = [
        {
            "factor_name": "Supplier Transit Delay",
            "observed_value": f"{target_po.get('actual_delay_days', 0)} days",
            "rule_threshold": "> 3 days",
            "status": "PASSED" if target_po.get("actual_delay_days", 0) > 3 else "NORMAL",
            "impact": "Triggered exception case creation" if target_po.get("actual_delay_days", 0) > 3 else "Within tolerance"
        },
        {
            "factor_name": "Stockout Countdown",
            "observed_value": f"{countdown} days ({on_hand} units on-hand / {daily_usage} daily rate)",
            "rule_threshold": "< 7 days (HIGH severity)",
            "status": "CRITICAL" if countdown < 7 else "HEALTHY",
            "impact": f"Stockout severity assessed as {risk.value.upper()}"
        },
        {
            "factor_name": "PO Financial Value",
            "observed_value": f"${target_po.get('total_value', 0.0):,.2f}",
            "rule_threshold": "> $50,000 (Human Approval Threshold)",
            "status": "APPROVAL_REQUIRED" if approval_eval.requires_human_approval else "AUTO_APPROVED",
            "impact": approval_eval.reason
        },
        {
            "factor_name": "Supplier Preapproval",
            "observed_value": "PREAPPROVED" if sup.get("is_preapproved") else "UNAPPROVED",
            "rule_threshold": "Preapproval required for auto PO creation under $10,000",
            "status": "VERIFIED" if sup.get("is_preapproved") else "UNVERIFIED",
            "impact": f"Supplier {sup.get('name')} preapproval verification status"
        }
    ]

    return {
        "id": exception_id,
        "po_data": target_po,
        "inventory_data": inv,
        "primary_supplier": sup,
        "stockout_countdown_days": countdown,
        "stockout_risk": risk.value if hasattr(risk, 'value') else risk,
        "disruption_evaluation": disruption_eval.model_dump(),
        "purchase_approval_evaluation": approval_eval.model_dump(),
        "decision_factors": decision_factors,
        "langgraph_workflow": {
            "current_step": snapshot.get("current_step"),
            "approval_status": snapshot.get("approval_status"),
            "requires_human_approval": snapshot.get("requires_human_approval"),
            "history": snapshot.get("history", []),
            "monitoring_result": snapshot.get("monitoring_result"),
            "impact_analysis": snapshot.get("impact_analysis"),
            "supplier_intelligence": snapshot.get("supplier_intelligence"),
            "logistics_recommendations": snapshot.get("logistics_recommendations"),
            "procurement_plan": snapshot.get("procurement_plan")
        },
        "alternative_suppliers": alt_suppliers_eval
    }

@router.post("/approvals/{exception_id}/decision")
async def post_approval_decision(exception_id: str, request: ApprovalDecisionRequest):
    """Log human approval/rejection decision for an exception case."""
    po_num = exception_id.replace("EXC-", "").upper()
    pos = _load_json("purchase_orders.json")
    
    found = False
    new_status = POStatus.EXPEDITED.value if request.decision.upper() == "APPROVED" else POStatus.CANCELLED.value
    
    for p in pos:
        if p["po_number"].upper() == po_num:
            p["status"] = new_status
            found = True
            break
            
    if not found:
        raise HTTPException(status_code=404, detail=f"PO number {po_num} not found.")
        
    _save_json("purchase_orders.json", pos)
    
    return {
        "exception_id": exception_id,
        "po_number": po_num,
        "decision": request.decision.upper(),
        "updated_po_status": new_status,
        "reviewer_notes": request.reviewer_notes,
        "timestamp": datetime.now().isoformat()
    }

@router.post("/approvals/bulk-preapprove")
async def post_bulk_preapprove():
    """Bulk auto-execute preapproved POs with values under $10,000 threshold."""
    pos = _load_json("purchase_orders.json")
    suppliers = _load_json("suppliers.json")
    sup_map = {s["id"]: s for s in suppliers}
    
    count = 0
    updated_pos = []
    for p in pos:
        s = sup_map.get(p["supplier_id"], {})
        is_preapproved = s.get("is_preapproved", False)
        val = p.get("total_value", 0.0)
        
        if val < 10000.0 and is_preapproved and p["status"] == "PENDING":
            p["status"] = "AUTO_EXECUTED"
            count += 1
        updated_pos.append(p)
        
    _save_json("purchase_orders.json", updated_pos)
    return {
        "auto_executed_count": count,
        "message": f"Successfully auto-executed {count} low-risk purchase orders under $10,000 preapproval threshold."
    }

@router.post("/run")
async def run_workflow(request: WorkflowRunRequest):
    """Trigger real-time agent workflow scenario for a PO."""
    pos = _load_json("purchase_orders.json")
    inventory = _load_json("inventory.json")
    suppliers = _load_json("suppliers.json")
    
    target_po = next((p for p in pos if p["po_number"].upper() == request.po_number.upper()), pos[0])
    sku = target_po["item_sku"]
    inv = next((i for i in inventory if i["sku"].lower() == sku.lower()), inventory[0])
    
    graph = create_supply_chain_workflow()
    thread_id = f"thread-run-{request.po_number.lower()}"
    config = {"configurable": {"thread_id": thread_id}}
    
    state_input = {
        "po_data": target_po,
        "inventory_data": inv,
        "all_suppliers": suppliers,
        "history": []
    }
    
    snapshot = await graph.ainvoke(state_input, config=config)
    return {
        "status": "COMPLETED",
        "thread_id": thread_id,
        "state_snapshot": snapshot
    }
