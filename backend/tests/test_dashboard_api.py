import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app


@pytest.mark.asyncio
async def test_dashboard_api_endpoint():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        res = await ac.get("/api/v1/dashboard")
        assert res.status_code == 200
        data = res.json()
        assert "stockout_risk_count" in data
        assert "delayed_orders_count" in data
        assert "pending_approvals_count" in data
        assert "agent_accuracy" in data
        metrics = data["agent_accuracy"]
        assert "decision_accuracy" in metrics
        assert "policy_compliance_rate" in metrics
