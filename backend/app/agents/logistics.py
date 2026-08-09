def run_logistics_agent(supplier_location: str, is_expedited_needed: bool) -> dict:
    """
    Logistics Agent: Calculates fast freight options to mitigate shipping delay.
    """
    if is_expedited_needed:
        recommended_mode = "AIR"
        transit_days = 2
        cost_usd = 4500.0
        carrier = "Global Air Cargo Express"
    else:
        recommended_mode = "GROUND"
        transit_days = 5
        cost_usd = 2100.0
        carrier = "DHL Freight Network"

    return {
        "recommended_mode": recommended_mode,
        "carrier_name": carrier,
        "estimated_transit_days": transit_days,
        "estimated_freight_cost_usd": cost_usd,
        "origin_location": supplier_location or "Unknown Origin",
        "logistics_summary": f"Recommended {recommended_mode} freight via {carrier} ({transit_days} days transit)."
    }
