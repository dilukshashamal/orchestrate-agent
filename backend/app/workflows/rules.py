from app.models.enums import StockoutRisk, ImpactLevel, RuleAction
from app.models.schemas import (
    DisruptionRuleInput,
    AlternativeSupplierRuleInput,
    PurchaseApprovalRuleInput,
    StockoutRiskRuleInput,
    RuleEvaluationResult
)

def evaluate_disruption_rule(input_data: DisruptionRuleInput) -> RuleEvaluationResult:
    """
    Baseline Rule 1:
    supplier_delay > 3 days AND stockout_risk == HIGH -> create_exception_case
    """
    if input_data.supplier_delay_days > 3 and input_data.stockout_risk == StockoutRisk.HIGH:
        return RuleEvaluationResult(
            action=RuleAction.CREATE_EXCEPTION_CASE,
            reason=f"Supplier delay of {input_data.supplier_delay_days} days exceeds 3-day threshold with HIGH stockout risk.",
            requires_human_approval=False
        )
    return RuleEvaluationResult(
        action=RuleAction.NO_ACTION,
        reason="Disruption criteria (delay > 3 days AND HIGH stockout risk) not met.",
        requires_human_approval=False
    )

def evaluate_alternative_supplier_rule(input_data: AlternativeSupplierRuleInput) -> RuleEvaluationResult:
    """
    Baseline Rule 2:
    alternative_supplier_available AND production_impact == HIGH -> evaluate_alternative_supplier
    """
    if input_data.alternative_supplier_available and input_data.production_impact == ImpactLevel.HIGH:
        return RuleEvaluationResult(
            action=RuleAction.EVALUATE_ALTERNATIVE_SUPPLIER,
            reason="Alternative supplier available for high production impact disruption.",
            requires_human_approval=False
        )
    return RuleEvaluationResult(
        action=RuleAction.NO_ACTION,
        reason="Alternative supplier evaluation criteria not met.",
        requires_human_approval=False
    )

def evaluate_purchase_approval_rule(input_data: PurchaseApprovalRuleInput) -> RuleEvaluationResult:
    """
    Baseline Rules 3 & 4:
    - purchase_value > $50,000 -> human_approval_required (Human Approval Threshold)
    - purchase_value < $10,000 AND supplier_is_preapproved -> auto_create_PO (Preapproval Threshold)
    - values in between or without preapproval default to human approval requirement.
    """
    if input_data.purchase_value > 50000.0:
        return RuleEvaluationResult(
            action=RuleAction.HUMAN_APPROVAL_REQUIRED,
            reason=f"Purchase value of ${input_data.purchase_value:,.2f} exceeds human approval threshold of $50,000.",
            requires_human_approval=True
        )
    
    if input_data.purchase_value < 10000.0 and input_data.supplier_is_preapproved:
        return RuleEvaluationResult(
            action=RuleAction.AUTO_CREATE_PO,
            reason=f"Purchase value of ${input_data.purchase_value:,.2f} is under $10,000 threshold with a preapproved supplier.",
            requires_human_approval=False
        )

    return RuleEvaluationResult(
        action=RuleAction.HUMAN_APPROVAL_REQUIRED,
        reason=f"Purchase value of ${input_data.purchase_value:,.2f} requires human review (not preapproved or above $10,000).",
        requires_human_approval=True
    )

def evaluate_stockout_risk_rule(input_data: StockoutRiskRuleInput) -> StockoutRisk:
    """
    Baseline Rule 5:
    stockout_countdown < 7 days -> HIGH severity stockout risk
    """
    if input_data.stockout_countdown_days < 7:
        return StockoutRisk.HIGH
    return StockoutRisk.LOW
