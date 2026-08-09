from typing import Any

HIGH_RISK_HIGH_VALUE_SCENARIO: dict[str, Any] = {
    "scenario_id": "SCENARIO-001-HIGH-RISK-HIGH-VALUE",
    "name": "Delayed Microprocessor Shipment with High Stockout Risk ($60,000)",
    "description": "5-day shipment delay for Microprocessor X100 causing critical 4-day stockout countdown with $60,000 purchase value requiring human approval.",
    "po_data": {
        "po_number": "PO-9001",
        "supplier_id": "SUP-001",
        "item_sku": "MAT-101",
        "quantity": 500,
        "unit_price": 120.0,
        "total_value": 60000.0,
        "status": "DELAYED",
        "actual_delay_days": 5
    },
    "inventory_data": {
        "sku": "MAT-101",
        "name": "Microprocessor X100",
        "on_hand_qty": 120,
        "safety_stock": 200,
        "reorder_point": 300,
        "daily_usage_rate": 25,
        "stockout_risk": "HIGH"
    },
    "all_suppliers": [
        {
            "id": "SUP-001",
            "name": "Titan Semiconductor Corp",
            "rating": 4.8,
            "lead_time_days": 14,
            "unit_price": 120.0,
            "capacity_units_per_week": 5000,
            "is_preapproved": True,
            "location": "Hsinchu, Taiwan"
        },
        {
            "id": "SUP-002",
            "name": "Apex Global Microelectronics",
            "rating": 4.6,
            "lead_time_days": 5,
            "unit_price": 135.0,
            "capacity_units_per_week": 2000,
            "is_preapproved": True,
            "location": "Austin, TX, USA"
        }
    ],
    "expected_outcome": {
        "disruption_flagged": True,
        "requires_human_approval": True,
        "expected_action": "HUMAN_APPROVAL_REQUIRED"
    }
}

LOW_RISK_LOW_VALUE_SCENARIO: dict[str, Any] = {
    "scenario_id": "SCENARIO-002-LOW-RISK-LOW-VALUE",
    "name": "Minor Delay Preapproved Order ($6,750)",
    "description": "4-day delay for small batch preapproved order ($6,750 < $10k threshold) with preapproved supplier SUP-002.",
    "po_data": {
        "po_number": "PO-9002",
        "supplier_id": "SUP-002",
        "item_sku": "MAT-101",
        "quantity": 50,
        "unit_price": 135.0,
        "total_value": 6750.0,
        "status": "DELAYED",
        "actual_delay_days": 4
    },
    "inventory_data": {
        "sku": "MAT-101",
        "name": "Microprocessor X100",
        "on_hand_qty": 120,
        "safety_stock": 200,
        "reorder_point": 300,
        "daily_usage_rate": 25,
        "stockout_risk": "HIGH"
    },
    "all_suppliers": [
        {
            "id": "SUP-002",
            "name": "Apex Global Microelectronics",
            "rating": 4.6,
            "lead_time_days": 5,
            "unit_price": 135.0,
            "capacity_units_per_week": 2000,
            "is_preapproved": True,
            "location": "Austin, TX, USA"
        }
    ],
    "expected_outcome": {
        "disruption_flagged": True,
        "requires_human_approval": False,
        "expected_action": "AUTO_CREATE_PO"
    }
}

EVALUATION_SCENARIOS: list[dict[str, Any]] = [
    HIGH_RISK_HIGH_VALUE_SCENARIO,
    LOW_RISK_LOW_VALUE_SCENARIO
]
