import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app

@pytest.mark.asyncio
async def test_health_endpoint():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.get("/health")
        assert response.status_code == 200
        assert response.json() == {"status": "ok"}

@pytest.mark.asyncio
async def test_erp_inventory_endpoints():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        # Get all inventory
        res = await ac.get("/api/v1/erp/inventory")
        assert res.status_code == 200
        items = res.json()
        assert len(items) > 0
        assert "sku" in items[0]
        assert "stockout_risk" in items[0]

        # Get single item by SKU
        sku = items[0]["sku"]
        res_sku = await ac.get(f"/api/v1/erp/inventory/{sku}")
        assert res_sku.status_code == 200
        assert res_sku.json()["sku"] == sku

        # Invalid SKU
        res_inv = await ac.get("/api/v1/erp/inventory/INVALID-SKU-999")
        assert res_inv.status_code == 404

@pytest.mark.asyncio
async def test_erp_suppliers_endpoints():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        # Get all suppliers
        res = await ac.get("/api/v1/erp/suppliers")
        assert res.status_code == 200
        suppliers = res.json()
        assert len(suppliers) > 0
        assert "is_preapproved" in suppliers[0]

        # Get single supplier by ID
        sup_id = suppliers[0]["id"]
        res_id = await ac.get(f"/api/v1/erp/suppliers/{sup_id}")
        assert res_id.status_code == 200
        assert res_id.json()["id"] == sup_id

        # Invalid supplier ID
        res_inv = await ac.get("/api/v1/erp/suppliers/SUP-INVALID")
        assert res_inv.status_code == 404

@pytest.mark.asyncio
async def test_procurement_endpoints():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        # Get all POs
        res = await ac.get("/api/v1/procurement/orders")
        assert res.status_code == 200
        pos = res.json()
        assert len(pos) > 0

        # Get single PO
        po_num = pos[0]["po_number"]
        res_po = await ac.get(f"/api/v1/procurement/orders/{po_num}")
        assert res_po.status_code == 200
        assert res_po.json()["po_number"] == po_num

        # Create PO
        create_payload = {
            "supplier_id": "SUP-002",
            "item_sku": "MAT-101",
            "quantity": 20,
            "unit_price": 135.0
        }
        res_create = await ac.post("/api/v1/procurement/orders", json=create_payload)
        assert res_create.status_code == 201
        created_po = res_create.json()
        assert created_po["total_value"] == 2700.0
        assert created_po["supplier_id"] == "SUP-002"

        # Patch PO status
        patch_payload = {"status": "EXPEDITED", "actual_delay_days": 2}
        res_patch = await ac.patch(f"/api/v1/procurement/orders/{created_po['po_number']}", json=patch_payload)
        assert res_patch.status_code == 200
        assert res_patch.json()["status"] == "EXPEDITED"
        assert res_patch.json()["actual_delay_days"] == 2

@pytest.mark.asyncio
async def test_logistics_endpoints():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        # Get routes
        res = await ac.get("/api/v1/logistics/routes")
        assert res.status_code == 200
        routes = res.json()
        assert len(routes) == 3

        # Calculate route
        calc_payload = {
            "origin": "Hsinchu, Taiwan",
            "destination": "Austin, TX",
            "cargo_weight_kg": 500.0,
            "is_expedited": True
        }
        res_calc = await ac.post("/api/v1/logistics/calculate-route", json=calc_payload)
        assert res_calc.status_code == 200
        options = res_calc.json()
        assert len(options) == 3
        assert any(opt["mode"] == "AIR" for opt in options)

@pytest.mark.asyncio
async def test_dashboard_and_workflows_endpoints():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        # Dashboard Summary
        res_dash = await ac.get("/api/v1/dashboard/summary")
        assert res_dash.status_code == 200
        dash = res_dash.json()
        assert "active_exceptions" in dash
        assert "pending_approvals" in dash
        assert "telemetry_stream" in dash

        # Workflows Exceptions List
        res_exc = await ac.get("/api/v1/workflows/exceptions")
        assert res_exc.status_code == 200
        excs = res_exc.json()
        assert len(excs) > 0
        assert "decision_reasons" in excs[0]

        # Single Exception Detail with LangGraph workflow trace and decision factors
        exc_id = excs[0]["id"]
        res_detail = await ac.get(f"/api/v1/workflows/exceptions/{exc_id}")
        assert res_detail.status_code == 200
        detail = res_detail.json()
        assert "decision_factors" in detail
        assert "langgraph_workflow" in detail
        assert "alternative_suppliers" in detail

        # Post Approval Decision
        decision_payload = {"decision": "APPROVED", "reviewer_notes": "Approved in test."}
        res_dec = await ac.post(f"/api/v1/workflows/approvals/{exc_id}/decision", json=decision_payload)
        assert res_dec.status_code == 200
        assert res_dec.json()["decision"] == "APPROVED"

        # Bulk Preapprove
        res_bulk = await ac.post("/api/v1/workflows/approvals/bulk-preapprove")
        assert res_bulk.status_code == 200
        assert "auto_executed_count" in res_bulk.json()

        # Run Workflow Endpoint
        run_payload = {"po_number": "PO-9001"}
        res_run = await ac.post("/api/v1/workflows/run", json=run_payload)
        assert res_run.status_code == 200
        assert res_run.json()["status"] == "COMPLETED"

