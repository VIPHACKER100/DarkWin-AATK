"use client";

import React, { useState } from "react";
import {
  X,
  Play,
  Zap,
  Shield,
  Search,
  Crosshair,
  Sliders,
  AlertCircle,
  CheckCircle2,
} from "lucide-react";
import { cn } from "@/lib/utils";

interface ScanWizardModalProps {
  isOpen: boolean;
  onClose: () => void;
  onStartScan: (target: string, mode: string) => Promise<void>;
  initialTarget?: string;
}

export function ScanWizardModal({
  isOpen,
  onClose,
  onStartScan,
  initialTarget = "",
}: ScanWizardModalProps) {
  const [target, setTarget] = useState(initialTarget);
  const [mode, setMode] = useState<"recon" | "full" | "bugbounty">("recon");
  const [threads, setThreads] = useState(25);
  const [showAdvanced, setShowAdvanced] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  if (!isOpen) return null;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!target.trim()) {
      setError("Please specify a target domain or IP address.");
      return;
    }
    setError(null);
    setLoading(true);
    try {
      await onStartScan(target.trim(), mode);
      onClose();
    } catch (err: any) {
      setError(err?.response?.data?.error || err.message || "Failed to start scan");
    } finally {
      setLoading(false);
    }
  };

  const pipelines = [
    {
      id: "recon",
      name: "Reconnaissance",
      tag: "Fast · 5-10m",
      desc: "Subdomain enumeration, DNS brute-forcing, WHOIS, ASN lookups, and port discovery.",
      icon: Search,
      color: "from-blue-600 to-cyan-500",
      border: "border-blue-500/40",
    },
    {
      id: "full",
      name: "Full Attack Scan",
      tag: "Comprehensive · 20-40m",
      desc: "Deep recon, web crawling, XSS/SQLi injection, Nuclei templates, and executive HTML report.",
      icon: Shield,
      color: "from-purple-600 to-indigo-500",
      border: "border-purple-500/40",
    },
    {
      id: "bugbounty",
      name: "Bug Bounty Sweep",
      tag: "High-Signal · 15-25m",
      desc: "Passive asset mining, historical Wayback/Katana URLs, parameter fuzzing, and S3 bucket checks.",
      icon: Crosshair,
      color: "from-emerald-600 to-teal-500",
      border: "border-emerald-500/40",
    },
  ] as const;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/80 backdrop-blur-sm p-4 animate-in fade-in duration-200">
      <div className="relative w-full max-w-2xl rounded-2xl border border-slate-800 bg-[#0A0E17] shadow-2xl overflow-hidden">
        {/* Top Header */}
        <div className="flex items-center justify-between px-6 py-5 border-b border-slate-800/80 bg-slate-900/40">
          <div className="flex items-center gap-3">
            <div className="flex h-9 w-9 items-center justify-center rounded-xl bg-blue-600/20 border border-blue-500/30 text-blue-400">
              <Zap className="h-5 w-5" />
            </div>
            <div>
              <h2 className="text-base font-bold text-white font-mono-label">Launch Attack Pipeline</h2>
              <p className="text-xs text-slate-400">Configure target scope and select automated scan workflow</p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-2 text-slate-400 hover:text-white rounded-lg hover:bg-slate-800 transition-colors"
          >
            <X className="h-4 w-4" />
          </button>
        </div>

        {/* Modal Form */}
        <form onSubmit={handleSubmit} className="p-6 space-y-6">
          {/* Target Input */}
          <div className="space-y-2">
            <label className="text-xs font-semibold uppercase tracking-wider text-slate-300 font-mono-label">
              Target Hostname / IP / Domain
            </label>
            <input
              type="text"
              required
              value={target}
              onChange={(e) => setTarget(e.target.value)}
              placeholder="e.g. example.com or 192.168.1.1"
              className="w-full px-4 py-3 rounded-xl bg-slate-900/90 border border-slate-800 text-sm text-slate-100 placeholder-slate-500 focus:outline-none focus:border-blue-500 focus:ring-1 focus:ring-blue-500 font-mono"
            />
            <p className="text-[11px] text-slate-500">
              Schemes (http://) and paths will be automatically normalized.
            </p>
          </div>

          {/* Pipeline Selector */}
          <div className="space-y-3">
            <label className="text-xs font-semibold uppercase tracking-wider text-slate-300 font-mono-label">
              Select Automated Pipeline
            </label>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
              {pipelines.map((p) => {
                const Icon = p.icon;
                const isSelected = mode === p.id;
                return (
                  <div
                    key={p.id}
                    onClick={() => setMode(p.id)}
                    className={cn(
                      "cursor-pointer p-4 rounded-xl border transition-all text-left flex flex-col justify-between",
                      isSelected
                        ? `bg-slate-900/90 ${p.border} shadow-lg ring-1 ring-blue-500`
                        : "bg-slate-900/40 border-slate-800 hover:border-slate-700 hover:bg-slate-900/60"
                    )}
                  >
                    <div>
                      <div className="flex items-center justify-between mb-2">
                        <div
                          className={cn(
                            "p-2 rounded-lg bg-gradient-to-br text-white",
                            p.color
                          )}
                        >
                          <Icon className="h-4 w-4" />
                        </div>
                        {isSelected && <CheckCircle2 className="h-4 w-4 text-blue-400" />}
                      </div>
                      <h3 className="text-xs font-bold text-white font-mono-label">{p.name}</h3>
                      <span className="text-[10px] text-blue-400 font-mono">{p.tag}</span>
                      <p className="text-[11px] text-slate-400 mt-2 leading-relaxed">{p.desc}</p>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>

          {/* Advanced Tuning Accordion */}
          <div className="border border-slate-800/80 rounded-xl overflow-hidden bg-slate-900/30">
            <button
              type="button"
              onClick={() => setShowAdvanced(!showAdvanced)}
              className="w-full flex items-center justify-between px-4 py-3 text-xs font-mono text-slate-400 hover:text-slate-200 transition-colors"
            >
              <span className="flex items-center gap-2">
                <Sliders className="h-3.5 w-3.5" />
                Advanced Concurrency & Stealth Tuning
              </span>
              <span>{showAdvanced ? "Hide ▲" : "Show ▼"}</span>
            </button>
            {showAdvanced && (
              <div className="p-4 border-t border-slate-800 space-y-4 text-xs">
                <div>
                  <div className="flex justify-between text-slate-400 mb-1 font-mono">
                    <span>Concurrency Threads</span>
                    <span className="text-blue-400 font-bold">{threads} Threads</span>
                  </div>
                  <input
                    type="range"
                    min="5"
                    max="50"
                    step="5"
                    value={threads}
                    onChange={(e) => setThreads(Number(e.target.value))}
                    className="w-full accent-blue-500 cursor-pointer"
                  />
                </div>
              </div>
            )}
          </div>

          {/* Error Banner */}
          {error && (
            <div className="p-3 rounded-xl bg-red-950/40 border border-red-500/40 flex items-center gap-2.5 text-xs text-red-300">
              <AlertCircle className="h-4 w-4 shrink-0 text-red-400" />
              <span>{error}</span>
            </div>
          )}

          {/* Bottom Actions */}
          <div className="flex items-center justify-end gap-3 pt-2">
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-2.5 rounded-xl text-xs font-medium text-slate-400 hover:text-white hover:bg-slate-800 transition-colors"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={loading}
              className="flex items-center gap-2 px-6 py-2.5 rounded-xl text-xs font-semibold text-white bg-gradient-to-r from-blue-600 via-blue-500 to-cyan-500 hover:opacity-95 shadow-lg shadow-blue-600/30 border border-blue-400/30 transition-all disabled:opacity-50"
            >
              {loading ? (
                <>
                  <div className="h-3.5 w-3.5 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                  <span>Initiating...</span>
                </>
              ) : (
                <>
                  <Play className="h-3.5 w-3.5 fill-current" />
                  <span>Start Scan Pipeline</span>
                </>
              )}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
