from app.models.schemas import PurchaseApprovalRuleInput
from app.workflows.rules import evaluate_purchase_approval_rule

def run_procurement_agent(target_supplier: dict, purchase_value: float) -> dict:
    """
    Procurement Agent: Evaluates purchase preapproval and human approval policy rules.
    """
    is_preapproved = target_supplier.get("is_preapproved", False)
    
    rule_input = PurchaseApprovalRuleInput(
        purchase_value=purchase_value,
        supplier_is_preapproved=is_preapproved
    )
    rule_result = evaluate_purchase_approval_rule(rule_input)

    return {
        "target_supplier_id": target_supplier.get("id"),
        "target_supplier_name": target_supplier.get("name"),
        "purchase_value_usd": purchase_value,
        "is_preapproved_supplier": is_preapproved,
        "requires_human_approval": rule_result.requires_human_approval,
        "recommended_action": rule_result.action.value,
        "action_reason": rule_result.reason
    }
