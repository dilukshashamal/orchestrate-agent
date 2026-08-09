'use client';

import React, { useState } from 'react';
import { ShieldAlert, AlertTriangle, CheckCircle, Clock, ChevronRight, Eye, ExternalLink, Filter, DollarSign } from 'lucide-react';
import { ExceptionCase } from '../../types';

interface DisruptionMatrixProps {
  exceptions: ExceptionCase[];
  onSelectException: (id: string) => void;
  onApprovePO: (id: string) => void;
}

export function DisruptionMatrix({ exceptions, onSelectException, onApprovePO }: DisruptionMatrixProps) {
  const [filterSeverity, setFilterSeverity] = useState<string>('ALL');

  const filtered = exceptions.filter(item => {
    if (filterSeverity === 'ALL') return true;
    return item.severity.toUpperCase() === filterSeverity.toUpperCase();
  });

  return (
    <div className="rounded-2xl bg-slate-900/80 border border-slate-800 p-5 backdrop-blur-md shadow-xl flex flex-col space-y-4">
      
      {/* Header & Filter Pills */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-4 border-b border-slate-800/80">
        <div className="flex items-center gap-2">
          <ShieldAlert className="w-5 h-5 text-rose-400" />
          <div>
            <h2 className="text-base font-bold text-white tracking-wide">
              Disruption Exceptions & Decision Matrix
            </h2>
            <p className="text-xs text-slate-400">
              Live cases flagged by 5-Agent LangGraph workflow and rules engine
            </p>
          </div>
        </div>

        {/* Filter Buttons */}
        <div className="flex items-center gap-1 bg-slate-950 p-1 rounded-xl border border-slate-800 text-xs font-medium">
          {['ALL', 'CRITICAL', 'WARNING', 'INFO'].map(sev => (
            <button
              key={sev}
              onClick={() => setFilterSeverity(sev)}
              className={`px-3 py-1 rounded-lg transition-all ${
                filterSeverity === sev
                  ? 'bg-blue-600 text-white font-bold shadow'
                  : 'text-slate-400 hover:text-slate-200'
              }`}
            >
              {sev}
            </button>
          ))}
        </div>
      </div>

      {/* Table */}
      <div className="overflow-x-auto rounded-xl border border-slate-800/80 bg-slate-950/60">
        <table className="w-full text-left border-collapse">
          <thead>
            <tr className="border-b border-slate-800 bg-slate-900/80 font-mono text-[11px] uppercase tracking-wider text-slate-400">
              <th className="p-3.5">Exception / PO</th>
              <th className="p-3.5">Component SKU</th>
              <th className="p-3.5">Primary Supplier</th>
              <th className="p-3.5 text-center">Delay</th>
              <th className="p-3.5 text-center">Stockout Countdown</th>
              <th className="p-3.5 text-right">PO Value</th>
              <th className="p-3.5 text-center">Severity / Risk</th>
              <th className="p-3.5 text-center">Approval Action</th>
              <th className="p-3.5 text-right">Inspect</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-800/60 text-xs">
            {filtered.map(item => {
              let sevBadge = 'bg-slate-800 text-slate-300 border-slate-700';
              if (item.severity === 'CRITICAL') sevBadge = 'bg-rose-500/20 text-rose-300 border-rose-500/30';
              if (item.severity === 'WARNING') sevBadge = 'bg-amber-500/20 text-amber-300 border-amber-500/30';
              if (item.severity === 'INFO') sevBadge = 'bg-blue-500/20 text-blue-300 border-blue-500/30';

              return (
                <tr key={item.id} className="hover:bg-slate-900/60 transition-colors">
                  
                  {/* PO # */}
                  <td className="p-3.5">
                    <div className="font-mono font-bold text-white flex items-center gap-1.5">
                      <span className="w-2 h-2 rounded-full bg-rose-500 animate-pulse"></span>
                      {item.po_number}
                    </div>
                    <span className="text-[10px] text-slate-500 font-mono">{item.id}</span>
                  </td>

                  {/* SKU */}
                  <td className="p-3.5">
                    <div className="font-mono text-blue-400 font-semibold">{item.item_sku}</div>
                    <div className="text-slate-400 text-[11px] line-clamp-1">{item.item_name}</div>
                  </td>

                  {/* Supplier */}
                  <td className="p-3.5 text-slate-300">
                    <div className="font-medium text-white">{item.supplier_name}</div>
                    <div className="text-[10px] text-slate-500 font-mono">{item.supplier_id}</div>
                  </td>

                  {/* Delay */}
                  <td className="p-3.5 text-center font-mono font-bold text-rose-400">
                    +{item.delay_days} days
                  </td>

                  {/* Countdown */}
                  <td className="p-3.5 text-center">
                    <span className={`inline-flex items-center px-2 py-0.5 rounded font-mono font-bold text-[11px] ${
                      item.stockout_countdown_days < 7
                        ? 'bg-rose-500/20 text-rose-300 border border-rose-500/30'
                        : 'bg-emerald-500/20 text-emerald-300 border border-emerald-500/30'
                    }`}>
                      {item.stockout_countdown_days} days
                    </span>
                  </td>

                  {/* PO Value */}
                  <td className="p-3.5 text-right font-mono font-bold text-white">
                    ${item.purchase_value.toLocaleString('en-US', { minimumFractionDigits: 2 })}
                  </td>

                  {/* Severity */}
                  <td className="p-3.5 text-center">
                    <span className={`px-2.5 py-1 rounded-md text-[10px] font-mono font-bold border ${sevBadge}`}>
                      {item.severity}
                    </span>
                  </td>

                  {/* Approval Action */}
                  <td className="p-3.5 text-center">
                    {item.requires_human_approval ? (
                      <span className="inline-flex items-center gap-1 text-amber-400 font-mono text-[10px] bg-amber-500/10 px-2 py-0.5 rounded border border-amber-500/20">
                        <Clock className="w-3 h-3" />
                        Human Approval Needed
                      </span>
                    ) : (
                      <span className="inline-flex items-center gap-1 text-emerald-400 font-mono text-[10px] bg-emerald-500/10 px-2 py-0.5 rounded border border-emerald-500/20">
                        <CheckCircle className="w-3 h-3" />
                        Auto-Executed
                      </span>
                    )}
                  </td>

                  {/* Inspect Button */}
                  <td className="p-3.5 text-right">
                    <button
                      onClick={() => onSelectException(item.id)}
                      className="px-3 py-1.5 rounded-lg bg-blue-600/20 hover:bg-blue-600/40 text-blue-300 border border-blue-500/30 font-semibold text-xs transition-all flex items-center gap-1 ml-auto"
                    >
                      <Eye className="w-3.5 h-3.5" />
                      Inspect Case
                    </button>
                  </td>

                </tr>
              );
            })}
          </tbody>
        </table>
      </div>

    </div>
  );
}
