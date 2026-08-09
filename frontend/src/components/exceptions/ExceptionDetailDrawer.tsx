'use client';

import React, { useState } from 'react';
import { X, CheckCircle, ShieldAlert, Cpu, Truck, ShoppingBag, Scale, ArrowRight, DollarSign, Clock, Building2, Flame } from 'lucide-react';
import { ExceptionDetail } from '../../types';
import { DecisionFactorsPanel } from './DecisionFactorsPanel';
import { LangGraphWorkflowVisualizer } from './LangGraphWorkflowVisualizer';

interface ExceptionDetailDrawerProps {
  detail: ExceptionDetail | null;
  isOpen: boolean;
  onClose: () => void;
  onApprove: (id: string) => void;
  onReject: (id: string) => void;
}

export function ExceptionDetailDrawer({ detail, isOpen, onClose, onApprove, onReject }: ExceptionDetailDrawerProps) {
  if (!isOpen || !detail) return null;

  const po = detail.po_data;
  const inv = detail.inventory_data;
  const sup = detail.primary_supplier;

  return (
    <div className="fixed inset-0 z-50 overflow-hidden bg-black/70 backdrop-blur-sm flex justify-end transition-opacity">
      <div className="w-full max-w-5xl bg-[#070a12] border-l border-slate-800 h-full overflow-y-auto p-6 md:p-8 space-y-8 text-slate-100 shadow-2xl">
        
        {/* Top Close Bar */}
        <div className="flex items-center justify-between border-b border-slate-800 pb-4">
          <div className="flex items-center gap-3">
            <div className="p-2.5 rounded-xl bg-rose-500/10 text-rose-400 border border-rose-500/20">
              <ShieldAlert className="w-6 h-6 animate-pulse" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h2 className="text-xl font-extrabold tracking-tight text-white font-mono">
                  {detail.id} ({po.po_number})
                </h2>
                <span className="px-2.5 py-0.5 rounded-md text-xs font-mono font-bold bg-rose-500/20 text-rose-300 border border-rose-500/30">
                  {detail.stockout_risk} RISK
                </span>
              </div>
              <p className="text-xs text-slate-400 mt-0.5">
                Detailed Agent Disruption Telemetry & Baseline Rule Engine Audit
              </p>
            </div>
          </div>

          <button
            onClick={onClose}
            className="p-2 rounded-xl bg-slate-900 border border-slate-800 hover:bg-slate-800 text-slate-400 hover:text-white transition-all"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Overview KPI Cards */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 font-mono text-xs">
          <div className="p-4 rounded-xl bg-slate-900/80 border border-slate-800">
            <span className="text-slate-500 flex items-center gap-1">
              <Building2 className="w-3.5 h-3.5 text-blue-400" />
              Primary Supplier
            </span>
            <div className="text-sm font-bold text-white mt-1 line-clamp-1">{sup.name}</div>
            <div className="text-[11px] text-slate-400 mt-0.5">{sup.location}</div>
          </div>

          <div className="p-4 rounded-xl bg-slate-900/80 border border-slate-800">
            <span className="text-slate-500 flex items-center gap-1">
              <Flame className="w-3.5 h-3.5 text-rose-400" />
              Stockout Countdown
            </span>
            <div className="text-sm font-bold text-rose-400 mt-1">
              {detail.stockout_countdown_days} Days Remaining
            </div>
            <div className="text-[11px] text-slate-400 mt-0.5">
              {inv.on_hand_qty} units on hand ({inv.daily_usage_rate}/day rate)
            </div>
          </div>

          <div className="p-4 rounded-xl bg-slate-900/80 border border-slate-800">
            <span className="text-slate-500 flex items-center gap-1">
              <DollarSign className="w-3.5 h-3.5 text-emerald-400" />
              PO Total Value
            </span>
            <div className="text-sm font-bold text-emerald-400 mt-1">
              ${po.total_value?.toLocaleString('en-US', { minimumFractionDigits: 2 })}
            </div>
            <div className="text-[11px] text-slate-400 mt-0.5">
              500 units @ ${po.unit_price}/unit
            </div>
          </div>

          <div className="p-4 rounded-xl bg-slate-900/80 border border-slate-800">
            <span className="text-slate-500 flex items-center gap-1">
              <Clock className="w-3.5 h-3.5 text-amber-400" />
              Human Approval Status
            </span>
            <div className="text-sm font-bold text-amber-300 mt-1">
              {detail.langgraph_workflow.approval_status}
            </div>
            <div className="text-[11px] text-slate-400 mt-0.5">
              Value &gt; $50,000 Threshold
            </div>
          </div>
        </div>

        {/* 1. Decision Factors & Policy Engine Triggers Panel */}
        <DecisionFactorsPanel
          factors={detail.decision_factors}
          ruleActions={{
            disruption_rule: detail.disruption_evaluation?.action || 'CREATE_EXCEPTION_CASE',
            purchase_approval_rule: detail.purchase_approval_evaluation?.action || 'HUMAN_APPROVAL_REQUIRED'
          }}
          reasons={[
            detail.disruption_evaluation?.reason || 'Supplier delay > 3 days exceeds threshold.',
            detail.purchase_approval_evaluation?.reason || 'PO value > $50,000 requires human review.'
          ]}
        />

        {/* 2. LangGraph Execution Workflow Diagram */}
        <LangGraphWorkflowVisualizer workflow={detail.langgraph_workflow} />

        {/* 3. Alternative Sourcing Options */}
        <div className="rounded-2xl bg-slate-900/90 border border-slate-800 p-6 shadow-xl space-y-4">
          <div className="flex items-center justify-between border-b border-slate-800 pb-3">
            <h3 className="text-base font-bold text-white flex items-center gap-2">
              <Building2 className="w-5 h-5 text-indigo-400" />
              Alternative Sourcing & Freight Comparison
            </h3>
            <span className="text-xs font-mono text-indigo-400 bg-indigo-500/10 px-2.5 py-1 rounded border border-indigo-500/20">
              Evaluated by SupplierIntelAgent
            </span>
          </div>

          <div className="overflow-x-auto rounded-xl border border-slate-800 bg-slate-950/60">
            <table className="w-full text-left text-xs border-collapse font-mono">
              <thead>
                <tr className="border-b border-slate-800 bg-slate-900/60 text-slate-400">
                  <th className="p-3">Supplier Name</th>
                  <th className="p-3">Location</th>
                  <th className="p-3 text-center">Rating</th>
                  <th className="p-3 text-center">Lead Time</th>
                  <th className="p-3 text-right">Unit Price</th>
                  <th className="p-3 text-center">Preapproved</th>
                  <th className="p-3 text-center">Viability</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/80">
                {detail.alternative_suppliers.map(alt => (
                  <tr key={alt.id} className="hover:bg-slate-900/40">
                    <td className="p-3 font-bold text-white">{alt.name}</td>
                    <td className="p-3 text-slate-400">{alt.location}</td>
                    <td className="p-3 text-center text-amber-400">★ {alt.rating}</td>
                    <td className="p-3 text-center text-emerald-400">{alt.lead_time_days} days ({alt.lead_time_delta_days}d)</td>
                    <td className="p-3 text-right text-white">${alt.unit_price}</td>
                    <td className="p-3 text-center">
                      {alt.is_preapproved ? (
                        <span className="px-2 py-0.5 rounded bg-emerald-500/20 text-emerald-400 text-[10px]">YES</span>
                      ) : (
                        <span className="px-2 py-0.5 rounded bg-slate-800 text-slate-400 text-[10px]">NO</span>
                      )}
                    </td>
                    <td className="p-3 text-center">
                      <span className="px-2 py-0.5 rounded bg-blue-500/20 text-blue-300 text-[10px]">OPTIMAL</span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        {/* Bottom Action Footer */}
        <div className="pt-4 border-t border-slate-800 flex items-center justify-end gap-3">
          <button
            onClick={() => onReject(detail.id)}
            className="px-5 py-2.5 rounded-xl font-semibold text-xs bg-rose-500/10 hover:bg-rose-500/20 text-rose-300 border border-rose-500/30 transition-all"
          >
            Reject & Escalate Case
          </button>

          <button
            onClick={() => onApprove(detail.id)}
            className="px-6 py-2.5 rounded-xl font-semibold text-xs bg-emerald-600 hover:bg-emerald-500 text-white shadow-lg shadow-emerald-600/20 border border-emerald-400/30 transition-all flex items-center gap-2"
          >
            <CheckCircle className="w-4 h-4" />
            Approve Expedited Reroute PO
          </button>
        </div>

      </div>
    </div>
  );
}
