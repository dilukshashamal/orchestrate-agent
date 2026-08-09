import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app


@pytest.mark.asyncio
async def test_workflows_api_full_flow():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        # 1. Run workflow for high risk PO-9001
        run_res = await ac.post("/api/v1/workflows/run", json={"po_number": "PO-9001"})
        assert run_res.status_code == 200
        data = run_res.json()
        thread_id = data["thread_id"]
        assert data["requires_human_approval"] is True
        assert data["approval_status"] == "PENDING"

        # 2. Get state snapshot
        state_res = await ac.get(f"/api/v1/workflows/{thread_id}/state")
        assert state_res.status_code == 200
        assert state_res.json()["thread_id"] == thread_id

        # 3. Resume workflow with APPROVE decision
        resume_res = await ac.post(
            f"/api/v1/workflows/{thread_id}/resume",
            json={"action": "APPROVE", "comment": "Approved by Supply Chain Manager"}
        )
        assert resume_res.status_code == 200
        resumed_data = resume_res.json()
        assert resumed_data["approval_status"] in ["APPROVED", "EXECUTED"]
        assert resumed_data["requires_human_approval"] is False

@pytest.mark.asyncio
async def test_workflows_api_invalid_thread():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        res = await ac.get("/api/v1/workflows/non-existent-thread-xyz/state")
        assert res.status_code == 404
