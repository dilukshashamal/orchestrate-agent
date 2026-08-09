import pytest
import json
from app.workflows.supply_chain import create_supply_chain_workflow
from app.evaluation.scenarios import HIGH_RISK_HIGH_VALUE_SCENARIO, LOW_RISK_LOW_VALUE_SCENARIO

def print_state_trace(scenario_name: str, state_snapshot: dict):
    print(f"\n==================== STATE TRACE: {scenario_name} ====================")
    history = state_snapshot.get("history", [])
    print("Execution Step History:")
    for idx, step in enumerate(history, 1):
        print(f"  [{idx}] {step}")
    
    monitoring = state_snapshot.get("monitoring_result", {})
    print(f"\n1. Monitoring Agent Result:")
    print(f"   - Disruption Flagged: {monitoring.get('disruption_flagged')}")
    print(f"   - Rule Action: {monitoring.get('rule_action')}")
    
    impact = state_snapshot.get("impact_analysis", {})
    print(f"\n2. Impact Analysis Agent Result:")
    print(f"   - Stockout Countdown: {impact.get('stockout_countdown_days')} days")
    print(f"   - Evaluated Stockout Risk: {impact.get('evaluated_stockout_risk')}")
    print(f"   - Production Impact: {impact.get('production_impact')}")

    intel = state_snapshot.get("supplier_intelligence", {})
    print(f"\n3. Supplier Intelligence Agent Result:")
    print(f"   - Alt Available: {intel.get('alternative_supplier_available')}")
    if intel.get('best_alternative'):
        print(f"   - Best Alternative: {intel['best_alternative']['name']} ({intel['best_alternative']['id']})")

    logistics = state_snapshot.get("logistics_recommendations", {})
    print(f"\n4. Logistics Agent Result:")
    print(f"   - Recommended Mode: {logistics.get('recommended_mode')}")
    print(f"   - Carrier: {logistics.get('carrier_name')} ({logistics.get('estimated_transit_days')} days)")

    procurement = state_snapshot.get("procurement_plan", {})
    print(f"\n5. Procurement Agent Result & Outcome:")
    print(f"   - Recommended Action: {procurement.get('recommended_action')}")
    print(f"   - Requires Human Approval: {state_snapshot.get('requires_human_approval')}")
    print(f"   - Final Approval Status: {state_snapshot.get('approval_status')}")
    print("======================================================================\n")

@pytest.mark.asyncio
async def test_high_risk_high_value_workflow_scenario():
    workflow = create_supply_chain_workflow()
    config = {"configurable": {"thread_id": "thread-high-risk-001"}}
    
    scenario = HIGH_RISK_HIGH_VALUE_SCENARIO
    initial_state = {
        "po_data": scenario["po_data"],
        "inventory_data": scenario["inventory_data"],
        "all_suppliers": scenario["all_suppliers"],
        "history": []
    }
    
    # Run graph until completion or interrupt
    snapshot = await workflow.ainvoke(initial_state, config=config)
    
    print_state_trace(scenario["name"], snapshot)
    
    # Assertions for High-Risk High-Value Scenario
    assert snapshot["requires_human_approval"] is True
    assert snapshot["procurement_plan"]["recommended_action"] == "HUMAN_APPROVAL_REQUIRED"
    assert snapshot["approval_status"] == "PENDING"

@pytest.mark.asyncio
async def test_low_risk_low_value_workflow_scenario():
    workflow = create_supply_chain_workflow()
    config = {"configurable": {"thread_id": "thread-low-risk-002"}}
    
    scenario = LOW_RISK_LOW_VALUE_SCENARIO
    initial_state = {
        "po_data": scenario["po_data"],
        "inventory_data": scenario["inventory_data"],
        "all_suppliers": scenario["all_suppliers"],
        "history": []
    }
    
    snapshot = await workflow.ainvoke(initial_state, config=config)
    
    print_state_trace(scenario["name"], snapshot)
    
    # Assertions for Low-Risk Low-Value Scenario (< $10k preapproved)
    assert snapshot["requires_human_approval"] is False
    assert snapshot["procurement_plan"]["recommended_action"] == "AUTO_CREATE_PO"
    assert snapshot["approval_status"] == "AUTO_EXECUTED"
