'use client';

import React, { useState } from 'react';
import { Cpu, CheckCircle2, Clock, AlertTriangle, ArrowRight, ShieldCheck, Truck, ShoppingBag, Search, ChevronRight, UserCheck } from 'lucide-react';
import { WorkflowStateSnapshot } from '../../types';

interface LangGraphWorkflowVisualizerProps {
  workflow: WorkflowStateSnapshot;
}

export function LangGraphWorkflowVisualizer({ workflow }: LangGraphWorkflowVisualizerProps) {
  const [selectedNode, setSelectedNode] = useState<string>('monitoring');

  const nodes = [
    {
      id: 'monitoring',
      name: '1. Monitoring Agent',
      icon: Search,
      role: 'Scans ERP & Telemetry stream for shipping delays',
      data: workflow.monitoring_result || { status: 'COMPLETED', disruption_flagged: true },
      completed: true
    },
    {
      id: 'impact_analysis',
      name: '2. Impact Analysis Agent',
      icon: Cpu,
      role: 'Calculates stockout countdown & production severity',
      data: workflow.impact_analysis || { stockout_countdown_days: 4.8, evaluated_stockout_risk: 'HIGH' },
      completed: true
    },
    {
      id: 'supplier_intelligence',
      name: '3. Supplier Intel Agent',
      icon: ShieldCheck,
      role: 'Queries supplier DB for alternative sourcing & capacity',
      data: workflow.supplier_intelligence || { alternative_supplier_available: true, best_alternative: 'SUP-002 Apex Global' },
      completed: true
    },
    {
      id: 'logistics',
      name: '4. Logistics Agent',
      icon: Truck,
      role: 'Evaluates express air vs ocean freight transit routes',
      data: workflow.logistics_recommendations || { recommended_mode: 'AIR', transit_days: 2 },
      completed: true
    },
    {
      id: 'procurement',
      name: '5. Procurement Agent',
      icon: ShoppingBag,
      role: 'Validates rules engine limits & generates PO plan',
      data: workflow.procurement_plan || { recommended_action: 'HUMAN_APPROVAL_REQUIRED', requires_human_approval: true },
      completed: true
    },
    {
      id: 'execution',
      name: '6. Human Approval Node',
      icon: UserCheck,
      role: 'Interrupt before execution for POs > $50,000 threshold',
      data: { approval_status: workflow.approval_status || 'PENDING', interrupt_reason: 'Purchase value > $50,000 threshold' },
      completed: workflow.approval_status === 'APPROVED' || workflow.approval_status === 'AUTO_EXECUTED',
      isPending: workflow.approval_status === 'PENDING'
    }
  ];

  const activeNodeData = nodes.find(n => n.id === selectedNode) || nodes[0];

  return (
    <div className="rounded-2xl bg-slate-900/90 border border-slate-800 p-6 shadow-xl space-y-6">
      
      {/* Visualizer Header */}
      <div className="flex items-center justify-between border-b border-slate-800 pb-4">
        <div>
          <h3 className="text-base font-bold text-white tracking-tight flex items-center gap-2">
            <Cpu className="w-5 h-5 text-blue-400" />
            LangGraph StateGraph Execution Visualizer
          </h3>
          <p className="text-xs text-slate-400 mt-0.5">
            5 Autonomous Agents + Deterministic Rules Engine Decision Node Execution
          </p>
        </div>

        <div className="flex items-center gap-2 font-mono text-xs">
          <span className="px-2.5 py-1 rounded-md bg-blue-500/10 text-blue-400 border border-blue-500/20">
            State Persistence: MemorySaver
          </span>
          <span className="px-2.5 py-1 rounded-md bg-amber-500/10 text-amber-400 border border-amber-500/20">
            interrupt_before=["execution"]
          </span>
        </div>
      </div>

      {/* Interactive Workflow Node Diagram Pipeline */}
      <div className="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-6 gap-3 pt-2">
        {nodes.map((node, index) => {
          const Icon = node.icon;
          const isSelected = selectedNode === node.id;
          
          let cardBorder = 'border-slate-800 hover:border-slate-700 bg-slate-950/60';
          let iconColor = 'text-blue-400';
          let statusBadge = 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20';
          let statusText = 'DONE';

          if (node.isPending) {
            cardBorder = 'border-amber-500/50 bg-amber-950/20 shadow-lg shadow-amber-950/20';
            iconColor = 'text-amber-400';
            statusBadge = 'bg-amber-500/20 text-amber-300 border-amber-500/30 animate-pulse';
            statusText = 'PAUSED / REVIEW';
          }

          if (isSelected) {
            cardBorder += ' ring-2 ring-blue-500 border-blue-500';
          }

          return (
            <div key={node.id} className="relative flex flex-col">
              <button
                onClick={() => setSelectedNode(node.id)}
                className={`p-3.5 rounded-xl border text-left flex flex-col justify-between h-full transition-all cursor-pointer ${cardBorder}`}
              >
                <div>
                  <div className="flex items-center justify-between mb-2">
                    <div className={`p-1.5 rounded-lg bg-slate-900 border border-slate-800 ${iconColor}`}>
                      <Icon className="w-4 h-4" />
                    </div>
                    <span className={`px-1.5 py-0.5 rounded text-[9px] font-mono font-bold border ${statusBadge}`}>
                      {statusText}
                    </span>
                  </div>
                  <h4 className="text-xs font-bold text-white line-clamp-1">{node.name}</h4>
                  <p className="text-[10px] text-slate-400 mt-1 line-clamp-2">{node.role}</p>
                </div>

                <div className="mt-3 flex items-center justify-between text-[10px] font-mono text-slate-500 border-t border-slate-800/60 pt-2">
                  <span>Step {index + 1}</span>
                  <ChevronRight className="w-3 h-3 text-slate-400" />
                </div>
              </button>
            </div>
          );
        })}
      </div>

      {/* Active Node Payload Inspector Drawer */}
      <div className="p-4 rounded-xl bg-slate-950 border border-slate-800 font-mono text-xs">
        <div className="flex items-center justify-between border-b border-slate-800/80 pb-2 mb-3">
          <span className="text-blue-400 font-bold flex items-center gap-2">
            <span className="w-2 h-2 rounded-full bg-blue-400 animate-ping"></span>
            INSPECTING PAYLOAD: {activeNodeData.name}
          </span>
          <span className="text-slate-500 text-[11px]">{activeNodeData.role}</span>
        </div>
        <pre className="text-slate-300 overflow-x-auto text-[11px] leading-relaxed bg-slate-900/60 p-3 rounded-lg border border-slate-800">
          {JSON.stringify(activeNodeData.data, null, 2)}
        </pre>
      </div>

    </div>
  );
}
