"use client";

import React from "react";
import {
  Activity,
  Target,
  ShieldAlert,
  Server,
  Wrench,
  Play,
  Clock,
  ArrowUpRight,
  CheckCircle2,
  AlertTriangle,
  Zap,
} from "lucide-react";
import { SystemStats, CurrentScan, TargetItem } from "@/lib/api";
import { cn } from "@/lib/utils";

interface OverviewViewProps {
  stats: SystemStats | null;
  targets: TargetItem[];
  currentScan: CurrentScan;
  onOpenScanModal: () => void;
  onSelectTarget: (target: string) => void;
  onNavigateToTab: (tab: any) => void;
}

export function OverviewView({
  stats,
  targets,
  currentScan,
  onOpenScanModal,
  onSelectTarget,
  onNavigateToTab,
}: OverviewViewProps) {
  const isScanning = currentScan.status === "running";

  const totalTargets = stats?.total_targets ?? targets.length;
  const toolsInstalled = stats?.tools_installed ?? 28;
  const toolsTotal = stats?.tools_total ?? 30;
  const criticalCount = stats?.severity_distribution?.critical ?? 0;
  const highCount = stats?.severity_distribution?.high ?? 0;

  const severityItems = [
    { label: "Critical", count: stats?.severity_distribution?.critical ?? 2, color: "bg-red-500", text: "text-red-400" },
    { label: "High", count: stats?.severity_distribution?.high ?? 4, color: "bg-orange-500", text: "text-orange-400" },
    { label: "Medium", count: stats?.severity_distribution?.medium ?? 7, color: "bg-amber-500", text: "text-amber-400" },
    { label: "Low", count: stats?.severity_distribution?.low ?? 12, color: "bg-cyan-500", text: "text-cyan-400" },
    { label: "Info", count: stats?.severity_distribution?.info ?? 25, color: "bg-slate-500", text: "text-slate-400" },
  ];

  const totalFindings = severityItems.reduce((acc, curr) => acc + curr.count, 0);

  return (
    <div className="space-y-6">
      {/* Top 4 KPI Metrics */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {/* Metric 1: Targets Scanned */}
        <div className="glass-panel glass-panel-hover p-5 rounded-2xl border border-slate-800 relative overflow-hidden group">
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold uppercase tracking-wider text-slate-400 font-mono-label">
              Total Targets
            </span>
            <div className="p-2.5 rounded-xl bg-blue-600/10 border border-blue-500/20 text-blue-400 group-hover:scale-110 transition-transform">
              <Target className="h-5 w-5" />
            </div>
          </div>
          <div className="mt-3 flex items-baseline gap-2">
            <span className="text-3xl font-bold font-mono text-white">{totalTargets}</span>
            <span className="text-xs text-emerald-400 font-mono flex items-center">
              +Active <ArrowUpRight className="h-3 w-3" />
            </span>
          </div>
          <p className="text-[11px] text-slate-500 mt-1">Managed perimeter scopes</p>
        </div>

        {/* Metric 2: Active Scans */}
        <div className="glass-panel glass-panel-hover p-5 rounded-2xl border border-slate-800 relative overflow-hidden group">
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold uppercase tracking-wider text-slate-400 font-mono-label">
              Active Scans
            </span>
            <div className="p-2.5 rounded-xl bg-cyan-600/10 border border-cyan-500/20 text-cyan-400 group-hover:scale-110 transition-transform">
              <Activity className={cn("h-5 w-5", isScanning && "animate-spin")} />
            </div>
          </div>
          <div className="mt-3 flex items-baseline gap-2">
            <span className="text-3xl font-bold font-mono text-white">
              {isScanning ? "1" : "0"}
            </span>
            <span
              className={cn(
                "text-xs font-mono font-medium px-2 py-0.5 rounded-full",
                isScanning ? "bg-cyan-500/20 text-cyan-300 animate-pulse" : "bg-slate-800 text-slate-400"
              )}
            >
              {isScanning ? currentScan.mode?.toUpperCase() : "IDLE"}
            </span>
          </div>
          <p className="text-[11px] text-slate-500 mt-1">Live attack pipelines</p>
        </div>

        {/* Metric 3: Critical & High Alerts */}
        <div className="glass-panel glass-panel-hover p-5 rounded-2xl border border-slate-800 relative overflow-hidden group">
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold uppercase tracking-wider text-slate-400 font-mono-label">
              Exploitable Vulns
            </span>
            <div className="p-2.5 rounded-xl bg-red-600/10 border border-red-500/20 text-red-400 group-hover:scale-110 transition-transform">
              <ShieldAlert className="h-5 w-5" />
            </div>
          </div>
          <div className="mt-3 flex items-baseline gap-2">
            <span className="text-3xl font-bold font-mono text-red-400">
              {criticalCount + highCount}
            </span>
            <span className="text-xs text-red-400/80 font-mono">Crit / High</span>
          </div>
          <p className="text-[11px] text-slate-500 mt-1">Requires immediate triage</p>
        </div>

        {/* Metric 4: Tool Health Readiness */}
        <div className="glass-panel glass-panel-hover p-5 rounded-2xl border border-slate-800 relative overflow-hidden group">
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold uppercase tracking-wider text-slate-400 font-mono-label">
              Tool Arsenal
            </span>
            <div className="p-2.5 rounded-xl bg-purple-600/10 border border-purple-500/20 text-purple-400 group-hover:scale-110 transition-transform">
              <Wrench className="h-5 w-5" />
            </div>
          </div>
          <div className="mt-3 flex items-baseline gap-2">
            <span className="text-3xl font-bold font-mono text-white">
              {toolsInstalled}/{toolsTotal}
            </span>
            <span className="text-xs text-emerald-400 font-mono">Operational</span>
          </div>
          <p className="text-[11px] text-slate-500 mt-1">External binaries on PATH</p>
        </div>
      </div>

      {/* Middle Grid: Vulnerability Spectrum & Active Scan Status */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Vulnerability Severity Distribution (2 cols) */}
        <div className="lg:col-span-2 glass-panel p-6 rounded-2xl border border-slate-800">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h2 className="text-sm font-bold text-white font-mono-label flex items-center gap-2">
                <ShieldAlert className="h-4 w-4 text-blue-400" />
                Vulnerability Severity Spectrum
              </h2>
              <p className="text-xs text-slate-400">Consolidated findings across all targets</p>
            </div>
            <button
              onClick={() => onNavigateToTab("vulns")}
              className="text-xs font-mono text-blue-400 hover:text-blue-300 flex items-center gap-1"
            >
              Open Findings Hub <ArrowUpRight className="h-3.5 w-3.5" />
            </button>
          </div>

          {/* Stacked Progress Bar */}
          <div className="h-4 w-full rounded-xl bg-slate-900 overflow-hidden flex p-0.5 border border-slate-800/80 mb-6">
            {severityItems.map((item) => {
              const widthPct = totalFindings > 0 ? (item.count / totalFindings) * 100 : 0;
              return (
                <div
                  key={item.label}
                  style={{ width: `${widthPct}%` }}
                  className={cn("h-full first:rounded-l-lg last:rounded-r-lg transition-all duration-500", item.color)}
                  title={`${item.label}: ${item.count}`}
                />
              );
            })}
          </div>

          {/* Severity Badges Grid */}
          <div className="grid grid-cols-2 sm:grid-cols-5 gap-3">
            {severityItems.map((item) => (
              <div
                key={item.label}
                className="p-3 rounded-xl bg-slate-900/60 border border-slate-800/80 flex flex-col"
              >
                <div className="flex items-center gap-1.5 mb-1">
                  <span className={cn("h-2 w-2 rounded-full", item.color)} />
                  <span className="text-[11px] font-mono text-slate-400 uppercase">{item.label}</span>
                </div>
                <span className={cn("text-xl font-bold font-mono", item.text)}>{item.count}</span>
              </div>
            ))}
          </div>
        </div>

        {/* Quick Launch & Status Card (1 col) */}
        <div className="glass-panel p-6 rounded-2xl border border-slate-800 flex flex-col justify-between">
          <div>
            <h2 className="text-sm font-bold text-white font-mono-label flex items-center gap-2 mb-1">
              <Zap className="h-4 w-4 text-cyan-400" />
              Quick Command Action
            </h2>
            <p className="text-xs text-slate-400 mb-4">Launch immediate scanning workflows</p>

            <div className="p-4 rounded-xl bg-slate-900/60 border border-slate-800 space-y-3 mb-4">
              <div className="flex items-center justify-between text-xs font-mono">
                <span className="text-slate-400">Scanner Engine</span>
                <span className="text-emerald-400 flex items-center gap-1">
                  <CheckCircle2 className="h-3 w-3" /> Ready
                </span>
              </div>
              <div className="flex items-center justify-between text-xs font-mono">
                <span className="text-slate-400">Default Wordlists</span>
                <span className="text-slate-300">SecLists (Loaded)</span>
              </div>
              <div className="flex items-center justify-between text-xs font-mono">
                <span className="text-slate-400">Engine Mode</span>
                <span className="text-blue-400">Pipeline v1.3</span>
              </div>
            </div>
          </div>

          <button
            onClick={onOpenScanModal}
            className="w-full flex items-center justify-center gap-2 py-3 rounded-xl text-xs font-bold text-white bg-gradient-to-r from-blue-600 via-blue-500 to-cyan-500 hover:opacity-95 shadow-lg shadow-blue-600/30 border border-blue-400/30 transition-all"
          >
            <Play className="h-4 w-4 fill-current" />
            <span>Launch Scan Wizard</span>
          </button>
        </div>
      </div>

      {/* Recent Targets & Scans Table */}
      <div className="glass-panel p-6 rounded-2xl border border-slate-800">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h2 className="text-sm font-bold text-white font-mono-label flex items-center gap-2">
              <Target className="h-4 w-4 text-emerald-400" />
              Recently Assessed Targets
            </h2>
            <p className="text-xs text-slate-400">Target directories available for analysis</p>
          </div>
          <button
            onClick={() => onNavigateToTab("targets")}
            className="text-xs font-mono text-blue-400 hover:text-blue-300 flex items-center gap-1"
          >
            View All Targets <ArrowUpRight className="h-3.5 w-3.5" />
          </button>
        </div>

        {targets.length === 0 ? (
          <div className="p-8 text-center border border-dashed border-slate-800 rounded-xl">
            <Target className="h-8 w-8 text-slate-600 mx-auto mb-2" />
            <p className="text-xs text-slate-400">No targets scanned yet.</p>
            <button
              onClick={onOpenScanModal}
              className="mt-3 text-xs text-blue-400 hover:underline font-mono"
            >
              Launch your first scan →
            </button>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
            {targets.slice(0, 6).map((t) => (
              <div
                key={t.target}
                onClick={() => {
                  onSelectTarget(t.target);
                  onNavigateToTab("targets");
                }}
                className="cursor-pointer p-4 rounded-xl bg-slate-900/40 border border-slate-800/80 hover:border-blue-500/50 hover:bg-slate-900/80 transition-all group flex items-center justify-between"
              >
                <div className="flex items-center gap-3 overflow-hidden">
                  <div className="p-2 rounded-lg bg-blue-600/10 text-blue-400 border border-blue-500/20 group-hover:scale-105 transition-transform">
                    <Target className="h-4 w-4" />
                  </div>
                  <div className="overflow-hidden">
                    <h3 className="text-xs font-bold text-slate-200 font-mono truncate group-hover:text-blue-400 transition-colors">
                      {t.target}
                    </h3>
                    <span className="text-[10px] text-slate-500 font-mono">
                      {t.sessions.length} Session{t.sessions.length === 1 ? "" : "s"}
                    </span>
                  </div>
                </div>
                <ArrowUpRight className="h-4 w-4 text-slate-600 group-hover:text-blue-400 transition-colors shrink-0" />
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
