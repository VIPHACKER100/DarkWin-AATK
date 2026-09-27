"use client";

import React from "react";
import {
  Play,
  Square,
  Search,
  Activity,
  Layers,
  Sparkles,
  Loader2,
  RefreshCw,
} from "lucide-react";
import { CurrentScan } from "@/lib/api";

interface HeaderProps {
  title: string;
  subtitle?: string;
  currentScan: CurrentScan;
  onOpenScanModal: () => void;
  onStopScan: () => void;
  onRefresh: () => void;
  searchQuery: string;
  setSearchQuery: (query: string) => void;
}

export function Header({
  title,
  subtitle,
  currentScan,
  onOpenScanModal,
  onStopScan,
  onRefresh,
  searchQuery,
  setSearchQuery,
}: HeaderProps) {
  const isScanning = currentScan.status === "running";

  return (
    <header className="sticky top-0 z-20 flex h-20 w-full items-center justify-between border-b border-slate-800/80 bg-[#07090E]/90 px-6 backdrop-blur-md">
      {/* Title & Context */}
      <div>
        <h1 className="text-xl font-bold tracking-tight text-white flex items-center gap-2.5 font-mono-label">
          {title}
        </h1>
        {subtitle && <p className="text-xs text-slate-400 mt-0.5">{subtitle}</p>}
      </div>

      {/* Center: Active Scan Banner */}
      {isScanning && (
        <div className="flex items-center gap-4 px-4 py-2 rounded-xl bg-blue-950/40 border border-blue-500/40 shadow-lg shadow-blue-500/10">
          <div className="flex items-center gap-2">
            <Loader2 className="h-4 w-4 animate-spin text-cyan-400" />
            <div className="flex flex-col">
              <span className="text-xs font-mono font-semibold text-slate-200">
                Scanning <span className="text-cyan-400">{currentScan.target}</span> ({currentScan.mode})
              </span>
              <span className="text-[10px] text-slate-400 font-mono">
                {currentScan.phase || "Processing..."} · {currentScan.progress}%
              </span>
            </div>
          </div>
          {/* Progress Mini Bar */}
          <div className="w-28 h-2 rounded-full bg-slate-800 overflow-hidden">
            <div
              className="h-full bg-gradient-to-r from-blue-500 to-cyan-400 transition-all duration-300"
              style={{ width: `${Math.max(currentScan.progress, 5)}%` }}
            />
          </div>
          {/* Abort button */}
          <button
            onClick={onStopScan}
            className="flex items-center gap-1 px-2.5 py-1 rounded-lg text-xs font-medium text-red-400 bg-red-950/60 hover:bg-red-900/80 border border-red-500/40 transition-colors"
            title="Abort active scan"
          >
            <Square className="h-3 w-3 fill-current" />
            <span>Abort</span>
          </button>
        </div>
      )}

      {/* Right Controls */}
      <div className="flex items-center gap-3">
        {/* Global Search Filter */}
        <div className="relative w-64">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-slate-500" />
          <input
            type="text"
            placeholder="Quick search assets, targets..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full pl-9 pr-3 py-2 text-xs rounded-xl bg-slate-900/80 border border-slate-800 text-slate-200 placeholder-slate-500 focus:outline-none focus:border-blue-500/80 focus:ring-1 focus:ring-blue-500 transition-all"
          />
        </div>

        {/* Refresh Button */}
        <button
          onClick={onRefresh}
          className="p-2.5 rounded-xl border border-slate-800 bg-slate-900/80 text-slate-400 hover:text-white hover:border-slate-700 transition-all"
          title="Refresh Data"
        >
          <RefreshCw className="h-4 w-4" />
        </button>

        {/* Primary CTA: Launch Scan */}
        <button
          onClick={onOpenScanModal}
          className="flex items-center gap-2 px-4 py-2 rounded-xl text-xs font-semibold text-white bg-gradient-to-r from-blue-600 via-blue-500 to-cyan-500 hover:opacity-95 shadow-lg shadow-blue-600/30 border border-blue-400/30 transition-all transform active:scale-95"
        >
          <Play className="h-3.5 w-3.5 fill-current" />
          <span>Launch Scan</span>
        </button>
      </div>
    </header>
  );
}
