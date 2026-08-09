'use client';

import React from 'react';
import { Layers, Clock, CheckCircle2, XCircle, Zap, ShieldAlert, ArrowRight, Eye } from 'lucide-react';
import { ExceptionCase } from '../../types';

interface ApprovalKanbanProps {
  exceptions: ExceptionCase[];
  onSelectException: (id: string) => void;
  onApprovePO: (id: string) => void;
  onBulkPreapprove: () => void;
}

export function ApprovalKanban({ exceptions, onSelectException, onApprovePO, onBulkPreapprove }: ApprovalKanbanProps) {
  const pending = exceptions.filter(e => e.requires_human_approval && e.po_status !== 'EXPEDITED' && e.po_status !== 'CANCELLED');
  const autoExecuted = exceptions.filter(e => e.po_status === 'AUTO_EXECUTED' || (!e.requires_human_approval && e.po_status !== 'DELAYED'));
  const approved = exceptions.filter(e => e.po_status === 'EXPEDITED' || e.po_status === 'APPROVED');
  const rejected = exceptions.filter(e => e.po_status === 'CANCELLED');

  return (
    <div className="space-y-6">
      
      {/* Top Banner with Bulk Preapprove button */}
      <div className="rounded-2xl bg-gradient-to-r from-slate-900 via-indigo-950/40 to-slate-900 border border-slate-800 p-6 backdrop-blur-md shadow-xl flex flex-col md:flex-row items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2">
            <Layers className="w-5 h-5 text-indigo-400" />
            <h2 className="text-lg font-bold text-white tracking-tight">
              Human Approval Queue & Governance Kanban
            </h2>
          </div>
          <p className="text-xs text-slate-400 mt-1">
            Mandatory human review for POs &gt; $50,000 threshold. Preapproved POs &lt; $10,000 auto-execute.
          </p>
        </div>

        <button
          onClick={onBulkPreapprove}
          className="px-5 py-2.5 rounded-xl font-semibold text-xs bg-emerald-600 hover:bg-emerald-500 text-white shadow-lg shadow-emerald-600/20 border border-emerald-400/30 transition-all flex items-center gap-2 shrink-0"
        >
          <Zap className="w-4 h-4" />
          Bulk Pre-Approve Low-Risk POs (&lt;$10k)
        </button>
      </div>

      {/* Kanban Board Columns */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-5">
        
        {/* Column 1: Pending Human Approval */}
        <div className="rounded-2xl bg-slate-900/60 border border-amber-900/40 p-4 flex flex-col space-y-3">
          <div className="flex items-center justify-between pb-2 border-b border-amber-900/40 font-mono">
            <span className="text-xs font-bold text-amber-300 flex items-center gap-1.5">
              <Clock className="w-4 h-4 text-amber-400" />
              Pending Review ({pending.length})
            </span>
            <span className="text-[10px] bg-amber-500/20 text-amber-300 px-2 py-0.5 rounded border border-amber-500/30">
              HIGH VALUE
            </span>
          </div>

          <div className="space-y-3 overflow-y-auto max-h-[500px] pr-1">
            {pending.map(item => (
              <div key={item.id} className="p-4 rounded-xl bg-slate-950 border border-amber-500/30 space-y-2 hover:border-amber-400 transition-all shadow-md">
                <div className="flex items-center justify-between text-xs font-mono">
                  <span className="font-bold text-white">{item.po_number}</span>
                  <span className="text-rose-400 font-bold">${item.purchase_value.toLocaleString()}</span>
                </div>
                <div className="text-xs text-slate-300">{item.supplier_name}</div>
                <p className="text-[11px] text-slate-400 leading-tight">
                  {item.decision_reasons[1] || 'Value > $50,000 requires authorization.'}
                </p>
                <div className="pt-2 flex items-center justify-between border-t border-slate-800/80">
                  <button
                    onClick={() => onSelectException(item.id)}
                    className="text-xs text-blue-400 hover:underline flex items-center gap-1 font-mono"
                  >
                    <Eye className="w-3.5 h-3.5" />
                    Inspect Factors
                  </button>
                  <button
                    onClick={() => onApprovePO(item.id)}
                    className="px-3 py-1 rounded-lg text-xs font-semibold bg-amber-500 hover:bg-amber-400 text-slate-950 transition-all"
                  >
                    Approve
                  </button>
                </div>
              </div>
            ))}
            {pending.length === 0 && (
              <div className="p-6 text-center text-xs text-slate-500 font-mono">No pending approval requests.</div>
            )}
          </div>
        </div>

        {/* Column 2: Auto-Executed */}
        <div className="rounded-2xl bg-slate-900/60 border border-emerald-900/40 p-4 flex flex-col space-y-3">
          <div className="flex items-center justify-between pb-2 border-b border-emerald-900/40 font-mono">
            <span className="text-xs font-bold text-emerald-300 flex items-center gap-1.5">
              <Zap className="w-4 h-4 text-emerald-400" />
              Auto-Executed ({autoExecuted.length})
            </span>
            <span className="text-[10px] bg-emerald-500/20 text-emerald-400 px-2 py-0.5 rounded border border-emerald-500/30">
              POLICY AUTOMATED
            </span>
          </div>

          <div className="space-y-3 overflow-y-auto max-h-[500px] pr-1">
            {autoExecuted.map(item => (
              <div key={item.id} className="p-4 rounded-xl bg-slate-950 border border-slate-800 space-y-2">
                <div className="flex items-center justify-between text-xs font-mono">
                  <span className="font-bold text-white">{item.po_number}</span>
                  <span className="text-emerald-400 font-bold">${item.purchase_value.toLocaleString()}</span>
                </div>
                <div className="text-xs text-slate-300">{item.supplier_name}</div>
                <p className="text-[11px] text-slate-400 leading-tight">
                  Auto-executed under $10,000 threshold with preapproved supplier.
                </p>
              </div>
            ))}
          </div>
        </div>

        {/* Column 3: Approved & Expedited */}
        <div className="rounded-2xl bg-slate-900/60 border border-blue-900/40 p-4 flex flex-col space-y-3">
          <div className="flex items-center justify-between pb-2 border-b border-blue-900/40 font-mono">
            <span className="text-xs font-bold text-blue-300 flex items-center gap-1.5">
              <CheckCircle2 className="w-4 h-4 text-blue-400" />
              Approved / Expedited ({approved.length})
            </span>
            <span className="text-[10px] bg-blue-500/20 text-blue-300 px-2 py-0.5 rounded border border-blue-500/30">
              EXECUTED
            </span>
          </div>

          <div className="space-y-3 overflow-y-auto max-h-[500px] pr-1">
            {approved.map(item => (
              <div key={item.id} className="p-4 rounded-xl bg-slate-950 border border-slate-800 space-y-2">
                <div className="flex items-center justify-between text-xs font-mono">
                  <span className="font-bold text-white">{item.po_number}</span>
                  <span className="text-blue-400 font-bold">${item.purchase_value.toLocaleString()}</span>
                </div>
                <div className="text-xs text-slate-300">{item.supplier_name}</div>
                <p className="text-[11px] text-slate-400">Rerouted via express air freight.</p>
              </div>
            ))}
          </div>
        </div>

        {/* Column 4: Rejected */}
        <div className="rounded-2xl bg-slate-900/60 border border-rose-900/40 p-4 flex flex-col space-y-3">
          <div className="flex items-center justify-between pb-2 border-b border-rose-900/40 font-mono">
            <span className="text-xs font-bold text-rose-300 flex items-center gap-1.5">
              <XCircle className="w-4 h-4 text-rose-400" />
              Rejected ({rejected.length})
            </span>
            <span className="text-[10px] bg-rose-500/20 text-rose-300 px-2 py-0.5 rounded border border-rose-500/30">
              CANCELLED
            </span>
          </div>

          <div className="space-y-3 overflow-y-auto max-h-[500px] pr-1">
            {rejected.map(item => (
              <div key={item.id} className="p-4 rounded-xl bg-slate-950 border border-slate-800 space-y-2">
                <div className="flex items-center justify-between text-xs font-mono">
                  <span className="font-bold text-white">{item.po_number}</span>
                  <span className="text-rose-400 font-bold">${item.purchase_value.toLocaleString()}</span>
                </div>
                <div className="text-xs text-slate-300">{item.supplier_name}</div>
                <p className="text-[11px] text-slate-400">Human override rejected action.</p>
              </div>
            ))}
            {rejected.length === 0 && (
              <div className="p-6 text-center text-xs text-slate-500 font-mono">No rejected orders.</div>
            )}
          </div>
        </div>

      </div>

    </div>
  );
}
