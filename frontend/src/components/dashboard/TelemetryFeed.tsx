'use client';

import React from 'react';
import { Activity, ShieldAlert, Cpu, CheckCircle2, Zap, Radio, CornerDownRight } from 'lucide-react';
import { DashboardSummary } from '../../types';

interface TelemetryFeedProps {
  summary: DashboardSummary;
}

export function TelemetryFeed({ summary }: TelemetryFeedProps) {
  return (
    <div className="rounded-2xl bg-slate-900/80 border border-slate-800 p-5 backdrop-blur-md shadow-xl flex flex-col h-full">
      <div className="flex items-center justify-between pb-4 border-b border-slate-800/80">
        <div className="flex items-center gap-2">
          <Radio className="w-4 h-4 text-emerald-400 animate-pulse" />
          <h2 className="text-sm font-semibold text-white tracking-wide uppercase">
            Autonomous Agent Telemetry Feed
          </h2>
        </div>
        <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
          STREAM ACTIVE
        </span>
      </div>

      <div className="mt-4 space-y-3 font-mono text-xs overflow-y-auto max-h-[320px] pr-1">
        {summary.telemetry_stream.map((evt) => {
          let badgeColor = 'bg-blue-500/10 text-blue-400 border-blue-500/20';
          if (evt.severity === 'CRITICAL') badgeColor = 'bg-rose-500/10 text-rose-400 border-rose-500/20';
          if (evt.severity === 'WARNING') badgeColor = 'bg-amber-500/10 text-amber-400 border-amber-500/20';
          if (evt.severity === 'SUCCESS') badgeColor = 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20';

          return (
            <div
              key={evt.id}
              className="p-3 rounded-xl bg-slate-950/60 border border-slate-800/60 hover:border-slate-700/80 transition-all flex flex-col gap-1.5"
            >
              <div className="flex items-center justify-between text-[11px]">
                <div className="flex items-center gap-2">
                  <span className={`px-2 py-0.5 rounded border text-[10px] font-bold ${badgeColor}`}>
                    {evt.agent}
                  </span>
                  <span className="text-slate-500">{evt.id}</span>
                </div>
                <span className="text-slate-500 text-[10px]">{evt.timestamp}</span>
              </div>
              <p className="text-slate-300 font-sans text-xs flex items-start gap-1.5 mt-0.5">
                <CornerDownRight className="w-3.5 h-3.5 text-blue-400 shrink-0 mt-0.5" />
                {evt.message}
              </p>
            </div>
          );
        })}
      </div>
    </div>
  );
}
