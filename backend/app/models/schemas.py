from typing import Optional, List
from pydantic import BaseModel, Field
from app.models.enums import StockoutRisk, ImpactLevel, RuleAction, ExceptionSeverity, POStatus, FreightMode

class DisruptionRuleInput(BaseModel):
    supplier_delay_days: int = Field(..., description="Supplier delay in days")
    stockout_risk: StockoutRisk = Field(..., description="Current stockout risk assessment")

class AlternativeSupplierRuleInput(BaseModel):
    alternative_supplier_available: bool = Field(..., description="Whether an alternative supplier exists")
    production_impact: ImpactLevel = Field(..., description="Impact level on ongoing production")

class PurchaseApprovalRuleInput(BaseModel):
    purchase_value: float = Field(..., description="Purchase order / action financial value in USD")
    supplier_is_preapproved: bool = Field(..., description="Whether the target supplier is preapproved")

class StockoutRiskRuleInput(BaseModel):
    stockout_countdown_days: int = Field(..., description="Days remaining until stockout occurs")

class RuleEvaluationResult(BaseModel):
    action: RuleAction = Field(..., description="Determined rule engine action")
    reason: str = Field(..., description="Explanation of why rule condition triggered")
    requires_human_approval: bool = Field(default=False, description="Whether human approval interrupt is mandatory")

# --- ERP Schemas ---
class Supplier(BaseModel):
    id: str
    name: str
    rating: float
    lead_time_days: int
    unit_price: float
    capacity_units_per_week: int
    is_preapproved: bool
    location: str
    contact_email: str

class InventoryItem(BaseModel):
    sku: str
    name: str
    on_hand_qty: int
    safety_stock: int
    reorder_point: int
    daily_usage_rate: int
    unit_of_measure: str
    stockout_countdown_days: Optional[int] = None
    stockout_risk: Optional[StockoutRisk] = None

# --- Procurement Schemas ---
class PurchaseOrder(BaseModel):
    po_number: str
    supplier_id: str
    item_sku: str
    quantity: int
    unit_price: float
    total_value: float
    status: POStatus
    order_date: str
    expected_delivery_date: str
    actual_delay_days: int = 0

class CreatePORequest(BaseModel):
    supplier_id: str
    item_sku: str
    quantity: int
    unit_price: float

class UpdatePORequest(BaseModel):
    status: Optional[POStatus] = None
    actual_delay_days: Optional[int] = None
    supplier_id: Optional[str] = None

# --- Logistics Schemas ---
class FreightRouteRequest(BaseModel):
    origin: str
    destination: str
    cargo_weight_kg: float
    is_expedited: bool = False

class FreightRouteOption(BaseModel):
    route_id: str
    mode: FreightMode
    carrier_name: str
    transit_days: int
    cost_usd: float
    carbon_footprint_kg: float
    reliability_score: float

