from app.models.enums import StockoutRisk
from app.models.schemas import DisruptionRuleInput
from app.workflows.rules import evaluate_disruption_rule

def run_monitoring_agent(po_data: dict, inventory_data: dict) -> dict:
    """
    Monitoring Agent: Scans shipment delay and evaluates disruption exception criteria via rules engine.
    """
    delay_days = po_data.get("actual_delay_days", 0)
    stockout_risk_str = inventory_data.get("stockout_risk", "LOW")
    try:
        stockout_risk = StockoutRisk(stockout_risk_str)
    except ValueError:
        stockout_risk = StockoutRisk.LOW

    rule_input = DisruptionRuleInput(supplier_delay_days=delay_days, stockout_risk=stockout_risk)
    rule_result = evaluate_disruption_rule(rule_input)

    return {
        "po_number": po_data.get("po_number"),
        "supplier_id": po_data.get("supplier_id"),
        "item_sku": po_data.get("item_sku"),
        "actual_delay_days": delay_days,
        "stockout_risk": stockout_risk_str,
        "disruption_flagged": rule_result.action.value == "CREATE_EXCEPTION_CASE",
        "rule_action": rule_result.action.value,
        "rule_reason": rule_result.reason
    }
