from app.models.enums import ImpactLevel, StockoutRisk
from app.models.schemas import StockoutRiskRuleInput
from app.workflows.rules import evaluate_stockout_risk_rule


def run_impact_analysis_agent(po_data: dict, inventory_data: dict) -> dict:
    """
    Impact Analysis Agent: Calculates stockout countdown, financial exposure, and production impact.
    """
    on_hand = inventory_data.get("on_hand_qty", 0)
    daily_usage = inventory_data.get("daily_usage_rate", 1)
    countdown_days = on_hand // daily_usage if daily_usage > 0 else 999
    
    calculated_risk = evaluate_stockout_risk_rule(
        StockoutRiskRuleInput(stockout_countdown_days=countdown_days)
    )

    total_po_val = po_data.get("total_value", 0.0)
    
    # Determine production impact
    if calculated_risk == StockoutRisk.HIGH or total_po_val > 50000.0:
        prod_impact = ImpactLevel.HIGH
    elif calculated_risk == StockoutRisk.MEDIUM:
        prod_impact = ImpactLevel.MEDIUM
    else:
        prod_impact = ImpactLevel.LOW

    return {
        "stockout_countdown_days": countdown_days,
        "evaluated_stockout_risk": calculated_risk.value,
        "financial_exposure_usd": total_po_val,
        "production_impact": prod_impact.value,
        "impact_summary": f"Stockout projected in {countdown_days} days. Financial exposure: ${total_po_val:,.2f} USD."
    }
