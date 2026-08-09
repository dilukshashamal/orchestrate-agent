from app.agents.monitoring import run_monitoring_agent
from app.agents.impact import run_impact_analysis_agent
from app.agents.supplier_intel import run_supplier_intel_agent
from app.agents.logistics import run_logistics_agent
from app.agents.procurement import run_procurement_agent

def monitoring_node(state: dict) -> dict:
    po_data = state.get("po_data", {})
    inventory_data = state.get("inventory_data", {})
    
    result = run_monitoring_agent(po_data, inventory_data)
    history = list(state.get("history", []))
    history.append("monitoring_node: completed disruption detection")
    
    return {
        **state,
        "monitoring_result": result,
        "current_step": "monitoring_node",
        "history": history
    }

def impact_analysis_node(state: dict) -> dict:
    po_data = state.get("po_data", {})
    inventory_data = state.get("inventory_data", {})
    
    result = run_impact_analysis_agent(po_data, inventory_data)
    history = list(state.get("history", []))
    history.append("impact_analysis_node: completed stockout impact calculation")
    
    return {
        **state,
        "impact_analysis": result,
        "current_step": "impact_analysis_node",
        "history": history
    }

def supplier_intelligence_node(state: dict) -> dict:
    all_suppliers = state.get("all_suppliers", [])
    po_data = state.get("po_data", {})
    impact_analysis = state.get("impact_analysis", {})
    
    current_sup_id = po_data.get("supplier_id", "")
    prod_impact = impact_analysis.get("production_impact", "LOW")
    
    result = run_supplier_intel_agent(all_suppliers, current_sup_id, prod_impact)
    history = list(state.get("history", []))
    history.append("supplier_intelligence_node: evaluated alternative suppliers")
    
    return {
        **state,
        "supplier_intelligence": result,
        "current_step": "supplier_intelligence_node",
        "history": history
    }

def logistics_node(state: dict) -> dict:
    supplier_intel = state.get("supplier_intelligence", {})
    best_alt = supplier_intel.get("best_alternative") or {}
    location = best_alt.get("location", "Taiwan")
    
    impact_analysis = state.get("impact_analysis", {})
    is_expedited = impact_analysis.get("production_impact") == "HIGH"
    
    result = run_logistics_agent(location, is_expedited)
    history = list(state.get("history", []))
    history.append("logistics_node: evaluated freight options")
    
    return {
        **state,
        "logistics_recommendations": result,
        "current_step": "logistics_node",
        "history": history
    }

def procurement_node(state: dict) -> dict:
    po_data = state.get("po_data", {})
    supplier_intel = state.get("supplier_intelligence", {})
    
    target_supplier = supplier_intel.get("best_alternative") or {
        "id": po_data.get("supplier_id"),
        "name": "Current Supplier",
        "is_preapproved": True
    }
    
    purchase_value = po_data.get("total_value", 0.0)
    result = run_procurement_agent(target_supplier, purchase_value)
    
    history = list(state.get("history", []))
    history.append("procurement_node: evaluated policy compliance & approval requirements")
    
    approval_status = "PENDING" if result["requires_human_approval"] else "AUTO_EXECUTED"
    
    return {
        **state,
        "procurement_plan": result,
        "requires_human_approval": result["requires_human_approval"],
        "approval_status": approval_status,
        "current_step": "procurement_node",
        "history": history
    }

def execution_node(state: dict) -> dict:
    history = list(state.get("history", []))
    approval_status = state.get("approval_status", "PENDING")
    
    if approval_status == "APPROVED" or approval_status == "AUTO_EXECUTED":
        final_status = "EXECUTED"
        history.append(f"execution_node: PO action successfully executed ({approval_status})")
    else:
        final_status = "REJECTED"
        history.append(f"execution_node: PO action rejected")

    return {
        **state,
        "approval_status": final_status,
        "current_step": "execution_node",
        "history": history
    }
