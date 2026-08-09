import json
from datetime import datetime, timedelta
from pathlib import Path

from fastapi import APIRouter, HTTPException

from app.models.enums import POStatus
from app.models.schemas import CreatePORequest, PurchaseOrder, UpdatePORequest

router = APIRouter(prefix="/api/v1/procurement", tags=["Procurement"])

MOCK_DIR = Path(__file__).resolve().parent.parent / "data" / "mock"

from typing import Any


def _load_pos() -> list[dict[str, Any]]:
    file_path = MOCK_DIR / "purchase_orders.json"
    if not file_path.exists():
        return []
    with open(file_path, "r", encoding="utf-8") as f:
        data: list[dict[str, Any]] = json.load(f)
        return data

def _save_pos(pos: list[dict[str, Any]]) -> None:
    file_path = MOCK_DIR / "purchase_orders.json"
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(pos, f, indent=2)

@router.get("/orders", response_model=list[PurchaseOrder])
async def get_all_purchase_orders():
    pos = _load_pos()
    return [PurchaseOrder(**p) for p in pos]

@router.get("/orders/{po_number}", response_model=PurchaseOrder)
async def get_purchase_order(po_number: str):
    pos = _load_pos()
    for p in pos:
        if p["po_number"].lower() == po_number.lower():
            return PurchaseOrder(**p)
    raise HTTPException(status_code=404, detail=f"Purchase order {po_number} not found.")

@router.post("/orders", response_model=PurchaseOrder, status_code=210)
@router.post("/orders", response_model=PurchaseOrder, status_code=201)
async def create_purchase_order(request: CreatePORequest):
    pos = _load_pos()
    new_po_num = f"PO-{9000 + len(pos) + 1}"
    total_val = round(request.quantity * request.unit_price, 2)
    today_str = datetime.now().strftime("%Y-%m-%d")
    exp_delivery_str = (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d")
    
    new_po = {
        "po_number": new_po_num,
        "supplier_id": request.supplier_id,
        "item_sku": request.item_sku,
        "quantity": request.quantity,
        "unit_price": request.unit_price,
        "total_value": total_val,
        "status": POStatus.PENDING.value,
        "order_date": today_str,
        "expected_delivery_date": exp_delivery_str,
        "actual_delay_days": 0
    }
    pos.append(new_po)
    _save_pos(pos)
    return PurchaseOrder.model_validate(new_po)

@router.patch("/orders/{po_number}", response_model=PurchaseOrder)
async def update_purchase_order(po_number: str, request: UpdatePORequest):
    pos = _load_pos()
    for p in pos:
        if p["po_number"].lower() == po_number.lower():
            if request.status is not None:
                p["status"] = request.status.value
            if request.actual_delay_days is not None:
                p["actual_delay_days"] = request.actual_delay_days
            if request.supplier_id is not None:
                p["supplier_id"] = request.supplier_id
            _save_pos(pos)
            return PurchaseOrder(**p)
    raise HTTPException(status_code=404, detail=f"Purchase order {po_number} not found.")
