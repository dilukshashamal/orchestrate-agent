import json
from pathlib import Path
from typing import List
from fastapi import APIRouter, HTTPException
from app.models.schemas import InventoryItem, Supplier, StockoutRiskRuleInput
from app.workflows.rules import evaluate_stockout_risk_rule

router = APIRouter(prefix="/api/v1/erp", tags=["ERP"])

MOCK_DIR = Path(__file__).resolve().parent.parent / "data" / "mock"

def _load_json(filename: str):
    file_path = MOCK_DIR / filename
    if not file_path.exists():
        raise HTTPException(status_code=404, detail=f"Mock data file {filename} not found.")
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)

@router.get("/inventory", response_model=List[InventoryItem])
async def get_all_inventory():
    items_raw = _load_json("inventory.json")
    results = []
    for item in items_raw:
        daily_usage = item.get("daily_usage_rate", 1)
        on_hand = item.get("on_hand_qty", 0)
        countdown = on_hand // daily_usage if daily_usage > 0 else 999
        risk = evaluate_stockout_risk_rule(StockoutRiskRuleInput(stockout_countdown_days=countdown))
        
        item_obj = InventoryItem(
            **item,
            stockout_countdown_days=countdown,
            stockout_risk=risk
        )
        results.append(item_obj)
    return results

@router.get("/inventory/{sku}", response_model=InventoryItem)
async def get_inventory_by_sku(sku: str):
    items_raw = _load_json("inventory.json")
    for item in items_raw:
        if item["sku"].lower() == sku.lower():
            daily_usage = item.get("daily_usage_rate", 1)
            on_hand = item.get("on_hand_qty", 0)
            countdown = on_hand // daily_usage if daily_usage > 0 else 999
            risk = evaluate_stockout_risk_rule(StockoutRiskRuleInput(stockout_countdown_days=countdown))
            return InventoryItem(
                **item,
                stockout_countdown_days=countdown,
                stockout_risk=risk
            )
    raise HTTPException(status_code=404, detail=f"Inventory item SKU {sku} not found.")

@router.get("/suppliers", response_model=List[Supplier])
async def get_all_suppliers():
    suppliers_raw = _load_json("suppliers.json")
    return [Supplier(**s) for s in suppliers_raw]

@router.get("/suppliers/{supplier_id}", response_model=Supplier)
async def get_supplier_by_id(supplier_id: str):
    suppliers_raw = _load_json("suppliers.json")
    for supplier in suppliers_raw:
        if supplier["id"].lower() == supplier_id.lower():
            return Supplier(**supplier)
    raise HTTPException(status_code=404, detail=f"Supplier ID {supplier_id} not found.")
