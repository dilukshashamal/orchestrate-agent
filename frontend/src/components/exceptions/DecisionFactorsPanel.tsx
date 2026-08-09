'use client';

import React from 'react';
import { Scale, CheckCircle2, AlertTriangle, ShieldAlert, FileText, ArrowRight } from 'lucide-react';
import { DecisionFactor } from '../../types';

interface DecisionFactorsPanelProps {
  factors: DecisionFactor[];
  ruleActions: {
    disruption_rule: string;
    purchase_approval_rule: string;
  };
  reasons: string[];
}

export function DecisionFactorsPanel({ factors, ruleActions, reasons }: DecisionFactorsPanelProps) {
  return (
    <div className="rounded-2xl bg-slate-900/90 border border-slate-800 p-6 shadow-xl space-y-6">
      
      {/* Header */}
      <div className="flex items-center justify-between border-b border-slate-800 pb-4">
        <div className="flex items-center gap-2.5">
          <div className="p-2 rounded-xl bg-blue-500/10 text-blue-400 border border-blue-500/20">
            <Scale className="w-5 h-5" />
          </div>
          <div>
            <h3 className="text-base font-bold text-white tracking-tight flex items-center gap-2">
              Decision Factors & Policy Engine Triggers
            </h3>
            <p className="text-xs text-slate-400">
              Deterministic evaluation rules executed by core policy engine (<code className="text-blue-400 font-mono">rules.py</code>)
            </p>
          </div>
        </div>

        <span className="px-3 py-1 rounded-full text-xs font-mono font-bold bg-blue-500/10 text-blue-400 border border-blue-500/20">
          LLM-FREE POLICY ENGINE
        </span>
      </div>

      {/* Decision Factors Matrix Table */}
      <div className="overflow-hidden rounded-xl border border-slate-800 bg-slate-950/60">
        <table className="w-full text-left border-collapse">
          <thead>
            <tr className="border-b border-slate-800 bg-slate-900/60 font-mono text-[11px] uppercase tracking-wider text-slate-400">
              <th className="p-3.5">Decision Factor</th>
              <th className="p-3.5">Observed Value</th>
              <th className="p-3.5">Policy Rule Threshold</th>
              <th className="p-3.5">Status</th>
              <th className="p-3.5">System Impact</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-800/80 text-xs">
            {factors.map((item, idx) => {
              let statusBadge = 'bg-slate-800 text-slate-300 border-slate-700';
              if (item.status === 'PASSED' || item.status === 'CRITICAL') {
                statusBadge = 'bg-rose-500/20 text-rose-300 border-rose-500/30';
              } else if (item.status === 'APPROVAL_REQUIRED') {
                statusBadge = 'bg-amber-500/20 text-amber-300 border-amber-500/30';
              } else if (item.status === 'HEALTHY' || item.status === 'VERIFIED' || item.status === 'AUTO_APPROVED') {
                statusBadge = 'bg-emerald-500/20 text-emerald-300 border-emerald-500/30';
              }

              return (
                <tr key={idx} className="hover:bg-slate-900/40 transition-colors">
                  <td className="p-3.5 font-semibold text-white flex items-center gap-2">
                    <span className="w-1.5 h-1.5 rounded-full bg-blue-400"></span>
                    {item.factor_name}
                  </td>
                  <td className="p-3.5 font-mono text-slate-200">{item.observed_value}</td>
                  <td className="p-3.5 font-mono text-blue-400">{item.rule_threshold}</td>
                  <td className="p-3.5">
                    <span className={`px-2.5 py-1 rounded-md text-[10px] font-mono font-bold border ${statusBadge}`}>
                      {item.status}
                    </span>
                  </td>
                  <td className="p-3.5 text-slate-300">{item.impact}</td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>

      {/* Decision Rationale Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        
        <div className="p-4 rounded-xl bg-slate-950/80 border border-slate-800 flex flex-col gap-2">
          <div className="flex items-center justify-between text-xs font-mono">
            <span className="text-slate-400 flex items-center gap-1.5">
              <ShieldAlert className="w-3.5 h-3.5 text-rose-400" />
              Disruption Detection Rule
            </span>
            <span className="text-rose-400 font-bold bg-rose-500/10 px-2 py-0.5 rounded border border-rose-500/20">
              {ruleActions.disruption_rule}
            </span>
          </div>
          <p className="text-xs text-slate-300 mt-1 leading-relaxed">
            {reasons[0] || 'Supplier delay > 3 days and HIGH stockout risk triggered exception creation.'}
          </p>
        </div>

        <div className="p-4 rounded-xl bg-slate-950/80 border border-slate-800 flex flex-col gap-2">
          <div className="flex items-center justify-between text-xs font-mono">
            <span className="text-slate-400 flex items-center gap-1.5">
              <FileText className="w-3.5 h-3.5 text-amber-400" />
              Procurement & Approval Rule
            </span>
            <span className="text-amber-400 font-bold bg-amber-500/10 px-2 py-0.5 rounded border border-amber-500/20">
              {ruleActions.purchase_approval_rule}
            </span>
          </div>
          <p className="text-xs text-slate-300 mt-1 leading-relaxed">
            {reasons[1] || 'PO value > $50,000 threshold requires mandatory human authorization.'}
          </p>
        </div>

      </div>

    </div>
  );
}
