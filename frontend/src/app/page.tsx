'use client';

import React, { useState, useEffect } from 'react';
import { Header } from '../components/layout/Header';
import { KpiCards } from '../components/dashboard/KpiCards';
import { TelemetryFeed } from '../components/dashboard/TelemetryFeed';
import { StockoutChart } from '../components/dashboard/StockoutChart';
import { DisruptionMatrix } from '../components/dashboard/DisruptionMatrix';
import { ExceptionDetailDrawer } from '../components/exceptions/ExceptionDetailDrawer';
import { ApprovalKanban } from '../components/approvals/ApprovalKanban';
import {
  fetchDashboardSummary,
  fetchExceptions,
  fetchExceptionDetail,
  submitApprovalDecision,
  submitBulkPreapprove,
  triggerWorkflowRun
} from '../lib/api';
import { DashboardSummary, ExceptionCase, ExceptionDetail } from '../types';

export default function CommandCenterPage() {
  const [activeTab, setActiveTab] = useState<string>('dashboard');
  const [summary, setSummary] = useState<DashboardSummary | null>(null);
  const [exceptions, setExceptions] = useState<ExceptionCase[]>([]);
  const [selectedDetail, setSelectedDetail] = useState<ExceptionDetail | null>(null);
  const [isDrawerOpen, setIsDrawerOpen] = useState<boolean>(false);
  const [isScanning, setIsScanning] = useState<boolean>(false);

  const loadData = async () => {
    try {
      const [sumData, excData] = await Promise.all([
        fetchDashboardSummary(),
        fetchExceptions()
      ]);
      setSummary(sumData);
      setExceptions(excData);
    } catch (e) {
      console.error('Data load error:', e);
    }
  };

  useEffect(() => {
    loadData();
    const interval = setInterval(loadData, 5000);
    return () => clearInterval(interval);
  }, []);

  const handleSelectException = async (id: string) => {
    const detail = await fetchExceptionDetail(id);
    if (detail) {
      setSelectedDetail(detail);
      setIsDrawerOpen(true);
    }
  };

  const handleApprovePO = async (id: string) => {
    await submitApprovalDecision(id, 'APPROVED');
    await loadData();
    if (selectedDetail && selectedDetail.id === id) {
      const updated = await fetchExceptionDetail(id);
      setSelectedDetail(updated);
    }
  };

  const handleRejectPO = async (id: string) => {
    await submitApprovalDecision(id, 'REJECTED');
    await loadData();
    setIsDrawerOpen(false);
  };

  const handleBulkPreapprove = async () => {
    await submitBulkPreapprove();
    await loadData();
  };

  const handleTriggerRescan = async () => {
    setIsScanning(true);
    await triggerWorkflowRun('PO-9001');
    await loadData();
    setTimeout(() => setIsScanning(false), 1200);
  };

  if (!summary) {
    return (
      <div className="min-h-screen bg-[#070a12] flex items-center justify-center text-slate-400 font-mono text-xs">
        <div className="flex items-center gap-3">
          <div className="w-4 h-4 rounded-full bg-blue-500 animate-ping"></div>
          Initializing Agentic Command Center Control Room...
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-[#070a12] text-slate-100 flex flex-col font-sans">
      
      {/* Top Header */}
      <Header
        activeTab={activeTab}
        setActiveTab={setActiveTab}
        onTriggerScan={handleTriggerRescan}
        isScanning={isScanning}
      />

      {/* Main Workspace Body */}
      <main className="flex-1 max-w-7xl w-full mx-auto p-6 md:p-8 space-y-8">
        
        {/* Tab 1: Command Center Dashboard */}
        {activeTab === 'dashboard' && (
          <div className="space-y-8">
            
            {/* KPI Stat Widgets */}
            <KpiCards summary={summary} />

            {/* Middle Grid: Telemetry Stream + Stockout Countdown Chart */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <TelemetryFeed summary={summary} />
              <StockoutChart exceptions={exceptions} />
            </div>

            {/* Disruption Exception Cases Table */}
            <DisruptionMatrix
              exceptions={exceptions}
              onSelectException={handleSelectException}
              onApprovePO={handleApprovePO}
            />

          </div>
        )}

        {/* Tab 2: Disruption Matrix View */}
        {activeTab === 'exceptions' && (
          <div className="space-y-6">
            <DisruptionMatrix
              exceptions={exceptions}
              onSelectException={handleSelectException}
              onApprovePO={handleApprovePO}
            />
          </div>
        )}

        {/* Tab 3: Human Governance Approval Queue */}
        {activeTab === 'approvals' && (
          <div className="space-y-6">
            <ApprovalKanban
              exceptions={exceptions}
              onSelectException={handleSelectException}
              onApprovePO={handleApprovePO}
              onBulkPreapprove={handleBulkPreapprove}
            />
          </div>
        )}

      </main>

      {/* Exception Detail Slide-Over Drawer */}
      <ExceptionDetailDrawer
        detail={selectedDetail}
        isOpen={isDrawerOpen}
        onClose={() => setIsDrawerOpen(false)}
        onApprove={handleApprovePO}
        onReject={handleRejectPO}
      />

      {/* Footer */}
      <footer className="border-t border-slate-800/80 bg-[#070a12] px-6 py-4 mt-auto text-xs text-slate-500 font-mono flex flex-col md:flex-row items-center justify-between gap-2">
        <div className="flex items-center gap-2">
          <span className="w-2 h-2 rounded-full bg-emerald-500"></span>
          <span>Autonomous Supply Chain Exception Agent • LangGraph StateGraph Architecture</span>
        </div>
        <div>
          Policy Rules Engine: <span className="text-blue-400">backend/app/workflows/rules.py</span>
        </div>
      </footer>

    </div>
  );
}
