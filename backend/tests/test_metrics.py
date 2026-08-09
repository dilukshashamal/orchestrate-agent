import pytest

from app.evaluation.metrics import EvaluationMetrics, compute_evaluation_metrics


@pytest.mark.asyncio
async def test_compute_evaluation_metrics():
    metrics = await compute_evaluation_metrics()
    assert isinstance(metrics, EvaluationMetrics)
    assert metrics.decision_accuracy >= 0.0
    assert metrics.tool_selection_accuracy >= 0.0
    assert metrics.policy_compliance_rate >= 0.0
    assert metrics.escalation_accuracy >= 0.0
    assert metrics.scenarios_evaluated > 0
    assert metrics.latency_p50_ms >= 0.0
