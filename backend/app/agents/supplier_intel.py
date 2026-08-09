from app.models.enums import ImpactLevel
from app.models.schemas import AlternativeSupplierRuleInput
from app.workflows.rules import evaluate_alternative_supplier_rule

def run_supplier_intel_agent(all_suppliers: list, current_supplier_id: str, production_impact_str: str) -> dict:
    """
    Supplier Intelligence Agent: Identifies alternative suppliers and checks rule engine evaluation.
    """
    alt_suppliers = [
        s for s in all_suppliers if s["id"].lower() != current_supplier_id.lower()
    ]
    alt_available = len(alt_suppliers) > 0
    
    try:
        prod_impact = ImpactLevel(production_impact_str)
    except ValueError:
        prod_impact = ImpactLevel.LOW

    rule_result = evaluate_alternative_supplier_rule(
        AlternativeSupplierRuleInput(
            alternative_supplier_available=alt_available,
            production_impact=prod_impact
        )
    )

    # Sort alternatives by lead time & rating
    best_alt = None
    if alt_suppliers:
        sorted_alts = sorted(alt_suppliers, key=lambda s: (s.get("lead_time_days", 99), -s.get("rating", 0)))
        best_alt = sorted_alts[0]

    return {
        "alternative_supplier_available": alt_available,
        "total_alternatives_found": len(alt_suppliers),
        "best_alternative": best_alt,
        "rule_action": rule_result.action.value,
        "rule_reason": rule_result.reason
    }
