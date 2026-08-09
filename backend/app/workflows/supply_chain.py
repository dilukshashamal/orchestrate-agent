from typing import TypedDict, List, Dict, Any, Optional
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver

from app.workflows.nodes import (
    monitoring_node,
    impact_analysis_node,
    supplier_intelligence_node,
    logistics_node,
    procurement_node,
    execution_node
)

class SupplyChainState(TypedDict, total=False):
    po_data: Dict[str, Any]
    inventory_data: Dict[str, Any]
    all_suppliers: List[Dict[str, Any]]
    monitoring_result: Dict[str, Any]
    impact_analysis: Dict[str, Any]
    supplier_intelligence: Dict[str, Any]
    logistics_recommendations: Dict[str, Any]
    procurement_plan: Dict[str, Any]
    requires_human_approval: bool
    approval_status: str
    current_step: str
    history: List[str]

def check_disruption_edge(state: SupplyChainState) -> str:
    """Check if disruption is flagged to continue workflow or end."""
    monitoring = state.get("monitoring_result", {})
    if monitoring.get("disruption_flagged", False):
        return "impact_analysis"
    return END

def check_approval_edge(state: SupplyChainState) -> str:
    """Route to execution if auto-approved or paused if human approval required."""
    if state.get("requires_human_approval", False):
        # Human approval required: route to execution node which is flagged in interrupt_before
        return "execution"
    else:
        # Auto-create PO path: execute directly
        return "execution"

def create_supply_chain_workflow():
    workflow = StateGraph(SupplyChainState)
    
    workflow.add_node("monitoring", monitoring_node)
    workflow.add_node("impact_analysis", impact_analysis_node)
    workflow.add_node("supplier_intelligence", supplier_intelligence_node)
    workflow.add_node("logistics", logistics_node)
    workflow.add_node("procurement", procurement_node)
    workflow.add_node("execution", execution_node)
    
    workflow.set_entry_point("monitoring")
    
    workflow.add_conditional_edges(
        "monitoring",
        check_disruption_edge,
        {
            "impact_analysis": "impact_analysis",
            END: END
        }
    )
    
    workflow.add_edge("impact_analysis", "supplier_intelligence")
    workflow.add_edge("supplier_intelligence", "logistics")
    workflow.add_edge("logistics", "procurement")
    
    workflow.add_conditional_edges(
        "procurement",
        check_approval_edge,
        {
            "execution": "execution"
        }
    )
    
    workflow.add_edge("execution", END)
    
    checkpointer = MemorySaver()
    
    # Interrupt before execution when human approval is required
    app = workflow.compile(
        checkpointer=checkpointer,
        interrupt_before=["execution"]
    )
    return app

# Singleton compiled workflow instance
supply_chain_graph = create_supply_chain_workflow()
