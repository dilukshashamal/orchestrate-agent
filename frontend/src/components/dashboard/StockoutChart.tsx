'use client';

import React from 'react';
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Cell, ReferenceLine } from 'recharts';
import { Flame, Info } from 'lucide-react';
import { ExceptionCase } from '../../types';

interface StockoutChartProps {
  exceptions: ExceptionCase[];
}

export function StockoutChart({ exceptions }: StockoutChartProps) {
  const chartData = exceptions.map(exc => ({
    name: exc.po_number,
    sku: exc.item_sku,
    countdown: exc.stockout_countdown_days,
    daily_usage: exc.daily_usage_rate,
    on_hand: exc.on_hand_qty,
    risk: exc.stockout_risk
  }));

  return (
    <div className="rounded-2xl bg-slate-900/80 border border-slate-800 p-5 backdrop-blur-md shadow-xl flex flex-col h-full">
      <div className="flex items-center justify-between pb-4 border-b border-slate-800/80">
        <div className="flex items-center gap-2">
          <Flame className="w-4 h-4 text-rose-400" />
          <h2 className="text-sm font-semibold text-white tracking-wide uppercase">
            Stockout Risk Countdown (Days)
          </h2>
        </div>
        <div className="flex items-center gap-2 text-xs font-mono">
          <span className="flex items-center gap-1 text-rose-400">
            <span className="w-2.5 h-2.5 rounded-full bg-rose-500"></span>
            &lt; 7 Days (Critical)
          </span>
          <span className="flex items-center gap-1 text-emerald-400">
            <span className="w-2.5 h-2.5 rounded-full bg-emerald-500"></span>
            &ge; 7 Days (Safe)
          </span>
        </div>
      </div>

      <div className="mt-4 text-xs text-slate-400 flex items-center justify-between">
        <span>Inventory depletion timeline based on daily consumption rate</span>
        <span className="font-mono text-blue-400">Rule Threshold: 7.0 Days</span>
      </div>

      <div className="mt-4 h-[240px] w-full">
        <ResponsiveContainer width="100%" height="100%">
          <BarChart data={chartData} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
            <XAxis dataKey="name" stroke="#64748b" fontSize={11} tickLine={false} />
            <YAxis stroke="#64748b" fontSize={11} tickLine={false} unit="d" />
            <Tooltip
              contentStyle={{
                backgroundColor: '#0d1322',
                borderColor: '#1e2942',
                borderRadius: '0.75rem',
                color: '#f8fafc',
                fontSize: '12px',
                fontFamily: 'monospace'
              }}
              formatter={(val: any) => [`${val} days remaining`, 'Stockout Countdown']}
            />
            <ReferenceLine y={7} stroke="#ef4444" strokeDasharray="3 3" label={{ value: '7d Critical Limit', fill: '#ef4444', fontSize: 10 }} />
            <Bar dataKey="countdown" radius={[6, 6, 0, 0]}>
              {chartData.map((entry, index) => (
                <Cell
                  key={`cell-${index}`}
                  fill={entry.countdown < 7 ? '#ef4444' : '#10b981'}
                />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}
