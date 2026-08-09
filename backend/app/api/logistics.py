from typing import List
from fastapi import APIRouter
from app.models.schemas import FreightRouteOption, FreightRouteRequest
from app.models.enums import FreightMode

router = APIRouter(prefix="/api/v1/logistics", tags=["Logistics"])

@router.get("/routes", response_model=List[FreightRouteOption])
async def get_available_routes():
    return [
        FreightRouteOption(
            route_id="RT-AIR-01",
            mode=FreightMode.AIR,
            carrier_name="Global Air Cargo Express",
            transit_days=2,
            cost_usd=4500.0,
            carbon_footprint_kg=1250.0,
            reliability_score=0.98
        ),
        FreightRouteOption(
            route_id="RT-OCEAN-01",
            mode=FreightMode.OCEAN,
            carrier_name="Maersk Ocean Line",
            transit_days=14,
            cost_usd=1200.0,
            carbon_footprint_kg=350.0,
            reliability_score=0.88
        ),
        FreightRouteOption(
            route_id="RT-GROUND-01",
            mode=FreightMode.GROUND,
            carrier_name="DHL Freight Network",
            transit_days=5,
            cost_usd=2100.0,
            carbon_footprint_kg=600.0,
            reliability_score=0.94
        )
    ]

@router.post("/calculate-route", response_model=List[FreightRouteOption])
async def calculate_freight_routes(request: FreightRouteRequest):
    weight_factor = request.cargo_weight_kg / 100.0
    
    air_cost = round(1500.0 + (weight_factor * 85.0), 2)
    ocean_cost = round(600.0 + (weight_factor * 20.0), 2)
    ground_cost = round(900.0 + (weight_factor * 45.0), 2)

    if request.is_expedited:
        air_cost = round(air_cost * 1.25, 2)
        ground_cost = round(ground_cost * 1.15, 2)

    return [
        FreightRouteOption(
            route_id="CALC-AIR-EXP",
            mode=FreightMode.AIR,
            carrier_name="Priority Air Charter",
            transit_days=1 if request.is_expedited else 2,
            cost_usd=air_cost,
            carbon_footprint_kg=round(weight_factor * 35.0, 1),
            reliability_score=0.99
        ),
        FreightRouteOption(
            route_id="CALC-GROUND-EXP",
            mode=FreightMode.GROUND,
            carrier_name="Express Fleet Direct",
            transit_days=3 if request.is_expedited else 5,
            cost_usd=ground_cost,
            carbon_footprint_kg=round(weight_factor * 18.0, 1),
            reliability_score=0.95
        ),
        FreightRouteOption(
            route_id="CALC-OCEAN-STD",
            mode=FreightMode.OCEAN,
            carrier_name="Transpacific Logistics",
            transit_days=12,
            cost_usd=ocean_cost,
            carbon_footprint_kg=round(weight_factor * 8.0, 1),
            reliability_score=0.87
        )
    ]
