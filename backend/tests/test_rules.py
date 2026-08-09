import pytest

from app.models.enums import ImpactLevel, RuleAction, StockoutRisk
from app.models.schemas import (
    AlternativeSupplierRuleInput,
    DisruptionRuleInput,
    PurchaseApprovalRuleInput,
    StockoutRiskRuleInput,
)
from app.workflows.rules import (
    evaluate_alternative_supplier_rule,
    evaluate_disruption_rule,
    evaluate_purchase_approval_rule,
    evaluate_stockout_risk_rule,
)


@pytest.mark.parametrize(
    "delay_days, stockout_risk, expected_action",
    [
        (4, StockoutRisk.HIGH, RuleAction.CREATE_EXCEPTION_CASE),
        (3, StockoutRisk.HIGH, RuleAction.NO_ACTION),  # Boundary test: exactly 3 days
        (5, StockoutRisk.LOW, RuleAction.NO_ACTION),
        (2, StockoutRisk.LOW, RuleAction.NO_ACTION),
        (10, StockoutRisk.MEDIUM, RuleAction.NO_ACTION),
    ]
)
def test_evaluate_disruption_rule(delay_days, stockout_risk, expected_action):
    input_data = DisruptionRuleInput(supplier_delay_days=delay_days, stockout_risk=stockout_risk)
    result = evaluate_disruption_rule(input_data)
    assert result.action == expected_action


@pytest.mark.parametrize(
    "alt_available, impact_level, expected_action",
    [
        (True, ImpactLevel.HIGH, RuleAction.EVALUATE_ALTERNATIVE_SUPPLIER),
        (False, ImpactLevel.HIGH, RuleAction.NO_ACTION),
        (True, ImpactLevel.LOW, RuleAction.NO_ACTION),
        (True, ImpactLevel.MEDIUM, RuleAction.NO_ACTION),
        (False, ImpactLevel.LOW, RuleAction.NO_ACTION),
    ]
)
def test_evaluate_alternative_supplier_rule(alt_available, impact_level, expected_action):
    input_data = AlternativeSupplierRuleInput(
        alternative_supplier_available=alt_available,
        production_impact=impact_level
    )
    result = evaluate_alternative_supplier_rule(input_data)
    assert result.action == expected_action


@pytest.mark.parametrize(
    "purchase_value, is_preapproved, expected_action, expected_human_approval",
    [
        # Preapproval boundary tests (< $10,000)
        (9999.99, True, RuleAction.AUTO_CREATE_PO, False),
        (10000.00, True, RuleAction.HUMAN_APPROVAL_REQUIRED, True),  # Boundary test: exact $10,000
        (5000.00, False, RuleAction.HUMAN_APPROVAL_REQUIRED, True),
        
        # Mid-tier values ($10,000 - $50,000)
        (25000.00, True, RuleAction.HUMAN_APPROVAL_REQUIRED, True),
        (50000.00, True, RuleAction.HUMAN_APPROVAL_REQUIRED, True),  # Boundary test: exact $50,000
        
        # Human approval boundary tests (> $50,000)
        (50000.01, True, RuleAction.HUMAN_APPROVAL_REQUIRED, True),
        (75000.00, False, RuleAction.HUMAN_APPROVAL_REQUIRED, True),
    ]
)
def test_evaluate_purchase_approval_rule(purchase_value, is_preapproved, expected_action, expected_human_approval):
    input_data = PurchaseApprovalRuleInput(
        purchase_value=purchase_value,
        supplier_is_preapproved=is_preapproved
    )
    result = evaluate_purchase_approval_rule(input_data)
    assert result.action == expected_action
    assert result.requires_human_approval == expected_human_approval


@pytest.mark.parametrize(
    "countdown_days, expected_risk",
    [
        (0, StockoutRisk.HIGH),
        (6, StockoutRisk.HIGH),
        (7, StockoutRisk.LOW),   # Boundary test: exactly 7 days
        (10, StockoutRisk.LOW),
    ]
)
def test_evaluate_stockout_risk_rule(countdown_days, expected_risk):
    input_data = StockoutRiskRuleInput(stockout_countdown_days=countdown_days)
    risk = evaluate_stockout_risk_rule(input_data)
    assert risk == expected_risk
