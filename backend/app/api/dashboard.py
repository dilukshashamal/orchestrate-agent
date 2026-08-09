import json
from pathlib import Path
from datetime import datetime
from fastapi import APIRouter
from app.workflows.rules import evaluate_stockout_risk_rule, evaluate_purchase_approval_rule
from app.models.enums import StockoutRisk
from app.models.schemas import StockoutRiskRuleInput, PurchaseApprovalRuleInput

router = APIRouter(prefix="/api/v1/dashboard", tags=["Dashboard"])

MOCK_DIR = Path(__file__).resolve().parent.parent / "data" / "mock"

def _load_json(filename: str):
    file_path = MOCK_DIR / filename
    if not file_path.exists():
        return []
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)

@router.get("/summary")
async def get_dashboard_summary():
    """Retrieve telemetry summary stats for Command Center dashboard."""
    pos = _load_json("purchase_orders.json")
    inventory = _load_json("inventory.json")
    suppliers = _load_json("suppliers.json")
    
    inv_map = {item["sku"]: item for item in inventory}
    sup_map = {sup["id"]: sup for sup in suppliers}
    
    active_exceptions = 0
    pending_approvals = 0
    auto_executed = 0
    at_risk_capital = 0.0
    critical_stockout_count = 0
    
    for po in pos:
        sku = po.get("item_sku")
        inv = inv_map.get(sku, {})
        sup = sup_map.get(po.get("supplier_id"), {})
        
        daily_usage = inv.get("daily_usage_rate", 25)
        on_hand = inv.get("on_hand_qty", 100)
        countdown = on_hand // daily_usage if daily_usage > 0 else 999
        risk = evaluate_stockout_risk_rule(StockoutRiskRuleInput(stockout_countdown_days=countdown))
        
        delay_days = po.get("actual_delay_days", 0)
        val = po.get("total_value", 0.0)
        
        approval_eval = evaluate_purchase_approval_rule(PurchaseApprovalRuleInput(
            purchase_value=val,
            supplier_is_preapproved=sup.get("is_preapproved", False)
        ))
        
        if delay_days > 3 or risk == StockoutRisk.HIGH:
            active_exceptions += 1
            at_risk_capital += val
            
        if risk == StockoutRisk.HIGH:
            critical_stockout_count += 1
            
        if po.get("status") == "PENDING" or approval_eval.requires_human_approval:
            pending_approvals += 1
            
        if po.get("status") in ["EXPEDITED", "AUTO_EXECUTED"] or not approval_eval.requires_human_approval:
            auto_executed += 1

    # Activity stream / telemetry events
    telemetry_stream = [
        {
            "id": "EVT-101",
            "timestamp": "Just now",
            "agent": "MonitoringAgent",
            "message": "Flagged 5-day delay on PO-9001 from Titan Semiconductor Corp (MAT-101).",
            "severity": "CRITICAL"
        },
        {
            "id": "EVT-102",
            "timestamp": "2 mins ago",
            "agent": "ImpactAnalysisAgent",
            "message": "Stockout countdown calculated at 4.8 days (< 7d threshold). Stockout risk escalated to HIGH.",
            "severity": "CRITICAL"
        },
        {
            "id": "EVT-103",
            "timestamp": "5 mins ago",
            "agent": "SupplierIntelAgent",
            "message": "Evaluated alternative supplier Apex Global Microelectronics (Lead time: 5 days, Rating: 4.6).",
            "severity": "INFO"
        },
        {
            "id": "EVT-104",
            "timestamp": "8 mins ago",
            "agent": "ProcurementAgent",
            "message": "PO value $60,000 exceeds $50,000 rule engine threshold. Created human approval request.",
            "severity": "WARNING"
        },
        {
            "id": "EVT-105",
            "timestamp": "15 mins ago",
            "agent": "RulesEngine",
            "message": "Auto-executed PO-9002 ($6,750 < $10k preapproved limit).",
            "severity": "SUCCESS"
        }
    ]

    return {
        "active_exceptions": active_exceptions,
        "pending_approvals": pending_approvals,
        "auto_executed": auto_executed,
        "at_risk_capital": at_risk_capital,
        "critical_stockouts": critical_stockout_count,
        "telemetry_status": "ONLINE",
        "telemetry_stream": telemetry_stream,
        "last_telemetry_scan": datetime.now().isoformat()
    }
