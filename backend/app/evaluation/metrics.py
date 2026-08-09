import math
import time
from typing import Any

from pydantic import BaseModel, Field

from app.evaluation.scenarios import EVALUATION_SCENARIOS
from app.workflows.supply_chain import create_supply_chain_workflow


class EvaluationMetrics(BaseModel):
    decision_accuracy: float = Field(..., description="Percentage of scenarios matching expected decision (0.0 to 100.0)")
    tool_selection_accuracy: float = Field(..., description="Percentage of rule engine tool evaluations executed accurately (0.0 to 100.0)")
    policy_compliance_rate: float = Field(..., description="Percentage of actions abiding by preapproval ($10k) and human approval ($50k) limits (0.0 to 100.0)")
    escalation_accuracy: float = Field(..., description="Percentage of high-risk scenarios correctly requiring human approval (0.0 to 100.0)")
    latency_p50_ms: float = Field(..., description="50th percentile workflow execution latency in milliseconds")
    latency_p95_ms: float = Field(..., description="95th percentile workflow execution latency in milliseconds")
    latency_p99_ms: float = Field(..., description="99th percentile workflow execution latency in milliseconds")
    scenarios_evaluated: int = Field(..., description="Total count of benchmark evaluation scenarios evaluated")

def _percentile(data: list[float], percentile: float) -> float:
    if not data:
        return 0.0
    sorted_data = sorted(data)
    k = (len(sorted_data) - 1) * (percentile / 100.0)
    f = math.floor(k)
    c = math.ceil(k)
    if f == c:
        return sorted_data[int(k)]
    d0 = sorted_data[int(f)] * (c - k)
    d1 = sorted_data[int(c)] * (k - f)
    return round(d0 + d1, 2)

async def compute_evaluation_metrics() -> EvaluationMetrics:
    workflow = create_supply_chain_workflow()
    
    total_scenarios = len(EVALUATION_SCENARIOS)
    correct_decisions = 0
    correct_tool_selections = 0
    compliant_policies = 0
    correct_escalations = 0
    latencies_ms: list[float] = []

    for idx, scenario in enumerate(EVALUATION_SCENARIOS):
        scenario_dict: dict[str, Any] = scenario
        po_data_dict: dict[str, Any] = scenario_dict.get("po_data", {})
        expected_dict: dict[str, Any] = scenario_dict.get("expected_outcome", {})
        
        config: dict[str, Any] = {"configurable": {"thread_id": f"eval-metrics-{idx}-{time.time()}"}}
        initial_state = {
            "po_data": po_data_dict,
            "inventory_data": scenario_dict.get("inventory_data", {}),
            "all_suppliers": scenario_dict.get("all_suppliers", []),
            "history": []
        }

        start_t = time.perf_counter()
        snapshot = await workflow.ainvoke(initial_state, config=config)
        elapsed_ms = (time.perf_counter() - start_t) * 1000.0
        latencies_ms.append(elapsed_ms)

        proc_plan = snapshot.get("procurement_plan", {})
        rec_action = proc_plan.get("recommended_action")
        req_approval = snapshot.get("requires_human_approval", False)

        # 1. Decision accuracy
        if rec_action == expected_dict.get("expected_action"):
            correct_decisions += 1
        
        # 2. Tool selection accuracy (monitoring + impact + procurement rules invoked)
        if snapshot.get("monitoring_result") and snapshot.get("impact_analysis") and proc_plan:
            correct_tool_selections += 1

        # 3. Policy compliance (Financial boundaries $10k and $50k)
        po_val = po_data_dict.get("total_value", 0.0)
        is_preapproved = po_data_dict.get("supplier_id") == "SUP-002"
        if po_val > 50000.0 and req_approval or po_val < 10000.0 and is_preapproved and not req_approval or po_val >= 10000.0 and po_val <= 50000.0 and req_approval:
            compliant_policies += 1

        # 4. Escalation accuracy
        if expected_dict.get("requires_human_approval") == req_approval:
            correct_escalations += 1

    dec_acc = round((correct_decisions / total_scenarios) * 100.0, 1) if total_scenarios > 0 else 100.0
    tool_acc = round((correct_tool_selections / total_scenarios) * 100.0, 1) if total_scenarios > 0 else 100.0
    pol_comp = round((compliant_policies / total_scenarios) * 100.0, 1) if total_scenarios > 0 else 100.0
    esc_acc = round((correct_escalations / total_scenarios) * 100.0, 1) if total_scenarios > 0 else 100.0

    p50 = _percentile(latencies_ms, 50.0)
    p95 = _percentile(latencies_ms, 95.0)
    p99 = _percentile(latencies_ms, 99.0)

    return EvaluationMetrics(
        decision_accuracy=dec_acc,
        tool_selection_accuracy=tool_acc,
        policy_compliance_rate=pol_comp,
        escalation_accuracy=esc_acc,
        latency_p50_ms=p50,
        latency_p95_ms=p95,
        latency_p99_ms=p99,
        scenarios_evaluated=total_scenarios
    )
