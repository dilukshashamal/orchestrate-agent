'use client';

import React from 'react';
import { AlertTriangle, Clock, CheckCircle, DollarSign, Flame, ArrowUpRight, TrendingUp } from 'lucide-react';
import { DashboardSummary } from '../../types';

interface KpiCardsProps {
  summary: DashboardSummary;
}

export function KpiCards({ summary }: KpiCardsProps) {
  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-5">
      
      {/* Active Disruption Exceptions Card */}
      <div className="relative overflow-hidden rounded-2xl bg-gradient-to-b from-rose-950/40 to-slate-900/90 border border-rose-900/40 p-5 shadow-xl shadow-rose-950/20 backdrop-blur-md group hover:border-rose-700/60 transition-all">
        <div className="absolute top-0 right-0 w-32 h-32 bg-rose-500/10 rounded-full blur-2xl group-hover:bg-rose-500/20 transition-all"></div>
        <div className="flex items-center justify-between">
          <span className="text-xs font-semibold text-rose-300 uppercase tracking-wider flex items-center gap-1.5">
            <AlertTriangle className="w-4 h-4 text-rose-400 animate-pulse" />
            Active Exceptions
          </span>
          <span className="px-2 py-0.5 rounded-full text-[10px] font-mono font-bold bg-rose-500/20 text-rose-300 border border-rose-500/30">
            CRITICAL
          </span>
        </div>
        <div className="mt-4 flex items-baseline justify-between">
          <div className="text-4xl font-extrabold font-mono text-white tracking-tight">
            {summary.active_exceptions}
          </div>
          <span className="text-xs text-rose-400/80 font-medium flex items-center gap-1">
            <Flame className="w-3.5 h-3.5 text-rose-400" />
            High Stockout Risk
          </span>
        </div>
        <p className="text-xs text-slate-400 mt-2">
          Telemetries detecting supplier delay &gt; 3 days
        </p>
      </div>

      {/* Pending Approvals Card */}
      <div className="relative overflow-hidden rounded-2xl bg-gradient-to-b from-amber-950/40 to-slate-900/90 border border-amber-900/40 p-5 shadow-xl shadow-amber-950/20 backdrop-blur-md group hover:border-amber-700/60 transition-all">
        <div className="absolute top-0 right-0 w-32 h-32 bg-amber-500/10 rounded-full blur-2xl group-hover:bg-amber-500/20 transition-all"></div>
        <div className="flex items-center justify-between">
          <span className="text-xs font-semibold text-amber-300 uppercase tracking-wider flex items-center gap-1.5">
            <Clock className="w-4 h-4 text-amber-400" />
            Pending Approvals
          </span>
          <span className="px-2 py-0.5 rounded-full text-[10px] font-mono font-bold bg-amber-500/20 text-amber-300 border border-amber-500/30">
            HUMAN OVERSIGHT
          </span>
        </div>
        <div className="mt-4 flex items-baseline justify-between">
          <div className="text-4xl font-extrabold font-mono text-white tracking-tight">
            {summary.pending_approvals}
          </div>
          <span className="text-xs text-amber-400/80 font-medium">
            PO Value &gt; $50,000
          </span>
        </div>
        <p className="text-xs text-slate-400 mt-2">
          Rule engine threshold pauses execution for review
        </p>
      </div>

      {/* Auto-Executed POs Card */}
      <div className="relative overflow-hidden rounded-2xl bg-gradient-to-b from-emerald-950/40 to-slate-900/90 border border-emerald-900/40 p-5 shadow-xl shadow-emerald-950/20 backdrop-blur-md group hover:border-emerald-700/60 transition-all">
        <div className="absolute top-0 right-0 w-32 h-32 bg-emerald-500/10 rounded-full blur-2xl group-hover:bg-emerald-500/20 transition-all"></div>
        <div className="flex items-center justify-between">
          <span className="text-xs font-semibold text-emerald-300 uppercase tracking-wider flex items-center gap-1.5">
            <CheckCircle className="w-4 h-4 text-emerald-400" />
            Auto-Executed POs
          </span>
          <span className="px-2 py-0.5 rounded-full text-[10px] font-mono font-bold bg-emerald-500/20 text-emerald-400 border border-emerald-500/30">
            PREAPPROVED
          </span>
        </div>
        <div className="mt-4 flex items-baseline justify-between">
          <div className="text-4xl font-extrabold font-mono text-white tracking-tight">
            {summary.auto_executed}
          </div>
          <span className="text-xs text-emerald-400/80 font-medium flex items-center gap-1">
            <TrendingUp className="w-3.5 h-3.5" />
            100% Policy Compliant
          </span>
        </div>
        <p className="text-xs text-slate-400 mt-2">
          Low-risk rule engine decisions (&lt; $10,000 threshold)
        </p>
      </div>

      {/* At-Risk Capital Card */}
      <div className="relative overflow-hidden rounded-2xl bg-gradient-to-b from-blue-950/40 to-slate-900/90 border border-blue-900/40 p-5 shadow-xl shadow-blue-950/20 backdrop-blur-md group hover:border-blue-700/60 transition-all">
        <div className="absolute top-0 right-0 w-32 h-32 bg-blue-500/10 rounded-full blur-2xl group-hover:bg-blue-500/20 transition-all"></div>
        <div className="flex items-center justify-between">
          <span className="text-xs font-semibold text-blue-300 uppercase tracking-wider flex items-center gap-1.5">
            <DollarSign className="w-4 h-4 text-blue-400" />
            At-Risk Capital
          </span>
          <span className="px-2 py-0.5 rounded-full text-[10px] font-mono font-bold bg-blue-500/20 text-blue-300 border border-blue-500/30">
            EXPOSURE
          </span>
        </div>
        <div className="mt-4 flex items-baseline justify-between">
          <div className="text-3xl font-extrabold font-mono text-white tracking-tight">
            ${summary.at_risk_capital.toLocaleString('en-US', { minimumFractionDigits: 0 })}
          </div>
          <span className="text-xs text-blue-400/80 font-medium flex items-center gap-1">
            <ArrowUpRight className="w-3.5 h-3.5" />
            Active Orders
          </span>
        </div>
        <p className="text-xs text-slate-400 mt-2">
          Total value tied up in delayed component shipments
        </p>
      </div>

    </div>
  );
}
