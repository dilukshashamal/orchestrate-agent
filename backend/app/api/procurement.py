import json
from pathlib import Path
from typing import List
from datetime import datetime, timedelta
from fastapi import APIRouter, HTTPException
from app.models.schemas import PurchaseOrder, CreatePORequest, UpdatePORequest
from app.models.enums import POStatus

router = APIRouter(prefix="/api/v1/procurement", tags=["Procurement"])

MOCK_DIR = Path(__file__).resolve().parent.parent / "data" / "mock"

def _load_pos():
    file_path = MOCK_DIR / "purchase_orders.json"
    if not file_path.exists():
        return []
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)

def _save_pos(pos: list):
    file_path = MOCK_DIR / "purchase_orders.json"
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(pos, f, indent=2)

@router.get("/orders", response_model=List[PurchaseOrder])
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
    return PurchaseOrder(**new_po)

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
