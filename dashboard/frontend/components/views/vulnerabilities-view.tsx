"use client";

import React, { useState } from "react";
import { ShieldAlert, Search, Copy, Check, X } from "lucide-react";
import { VulnerabilityFinding } from "@/lib/api";
import { cn } from "@/lib/utils";

interface VulnerabilitiesViewProps {
  findings: VulnerabilityFinding[];
  loading?: boolean;
  selectedTarget?: string | null;
}

export function VulnerabilitiesView({
  findings,
  loading = false,
  selectedTarget,
}: VulnerabilitiesViewProps) {
  const [selectedSeverity, setSelectedSeverity] = useState<string>("ALL");
  const [search, setSearch] = useState("");
  const [activeFinding, setActiveFinding] = useState<VulnerabilityFinding | null>(null);
  const [copied, setCopied] = useState(false);

  const filtered = findings.filter((f) => {
    const matchesSev = selectedSeverity === "ALL" || f.severity === selectedSeverity;
    const matchesSearch =
      f.title.toLowerCase().includes(search.toLowerCase()) ||
      f.target.toLowerCase().includes(search.toLowerCase()) ||
      (f.category || "").toLowerCase().includes(search.toLowerCase());
    return matchesSev && matchesSearch;
  });

  const getSeverityBadge = (severity: string) => {
    switch (severity) {
      case "CRITICAL": return "bg-red-950/70 text-red-400 border-red-500/40";
      case "HIGH":     return "bg-orange-950/70 text-orange-400 border-orange-500/40";
      case "MEDIUM":   return "bg-amber-950/70 text-amber-400 border-amber-500/40";
      case "LOW":      return "bg-cyan-950/70 text-cyan-400 border-cyan-500/40";
      default:         return "bg-slate-900 text-slate-400 border-slate-700";
    }
  };

  const handleCopyPoC = () => {
    if (!activeFinding?.poc) return;
    navigator.clipboard.writeText(activeFinding.poc);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const counts = findings.reduce(
    (acc, f) => { const s = f.severity as keyof typeof acc; if (s in acc) acc[s]++; return acc; },
    { CRITICAL: 0, HIGH: 0, MEDIUM: 0, LOW: 0, INFO: 0 }
  );

  return (
    <div className="space-y-6">
      {/* Severity Stat Cards */}
      <div className="grid grid-cols-5 gap-3">
        {(["CRITICAL", "HIGH", "MEDIUM", "LOW", "INFO"] as const).map((sev) => (
          <div key={sev} className="glass-panel rounded-xl p-3 border border-slate-800 text-center">
            <div className={cn("text-lg font-bold font-mono",
              sev === "CRITICAL" ? "text-red-400" :
              sev === "HIGH" ? "text-orange-400" :
              sev === "MEDIUM" ? "text-amber-400" :
              sev === "LOW" ? "text-cyan-400" : "text-slate-400"
            )}>
              {counts[sev]}
            </div>
            <div className="text-[10px] text-slate-500 uppercase tracking-wider mt-0.5">{sev}</div>
          </div>
        ))}
      </div>

      {/* Loading State */}
      {loading && (
        <div className="flex items-center justify-center h-48 text-slate-500 text-xs font-mono">
          <div className="text-center space-y-3">
            <div className="h-8 w-8 rounded-full border-2 border-blue-500/30 border-t-blue-400 animate-spin mx-auto" />
            <p className="animate-pulse">
              Loading vulnerabilities for <span className="text-blue-400">{selectedTarget}</span>...
            </p>
          </div>
        </div>
      )}

      {!loading && (
        <div className="space-y-4">
          {/* Filter Bar */}
          <div className="glass-panel p-4 rounded-2xl border border-slate-800 flex flex-wrap items-center justify-between gap-4">
            <div className="flex items-center gap-1.5 flex-wrap">
              {["ALL", "CRITICAL", "HIGH", "MEDIUM", "LOW"].map((sev) => (
                <button
                  key={sev}
                  onClick={() => setSelectedSeverity(sev)}
                  className={cn(
                    "px-3 py-1.5 rounded-xl text-xs font-mono font-medium transition-all",
                    selectedSeverity === sev
                      ? "bg-blue-600 text-white shadow-md shadow-blue-600/30"
                      : "bg-slate-900/60 text-slate-400 hover:text-white hover:bg-slate-800/80 border border-slate-800"
                  )}
                >
                  {sev}
                </button>
              ))}
            </div>
            <div className="relative w-72">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-3.5 w-3.5 text-slate-500" />
              <input
                type="text"
                placeholder="Search vulnerabilities, CVE, PoC..."
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                className="w-full pl-8 pr-3 py-1.5 text-xs rounded-xl bg-slate-900 border border-slate-800 text-slate-200 placeholder-slate-500 focus:outline-none focus:border-blue-500 font-mono"
              />
            </div>
          </div>

          {/* Findings Table */}
          <div className="glass-panel rounded-2xl border border-slate-800 overflow-hidden">
            <table className="w-full text-left text-xs font-mono">
              <thead className="bg-slate-900/80 text-slate-400 border-b border-slate-800 uppercase text-[10px]">
                <tr>
                  <th className="px-5 py-3">Severity</th>
                  <th className="px-5 py-3">Vulnerability Title</th>
                  <th className="px-5 py-3">Target Scope</th>
                  <th className="px-5 py-3">Category</th>
                  <th className="px-5 py-3 text-right">Action</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/60">
                {filtered.length === 0 && (
                  <tr>
                    <td colSpan={5} className="px-5 py-16 text-center">
                      <div className="flex flex-col items-center gap-3 text-slate-500">
                        <ShieldAlert className="h-10 w-10 opacity-30" />
                        <p className="text-sm font-medium">
                          {findings.length === 0 && !selectedTarget
                            ? "Select a target to load vulnerability findings"
                            : findings.length === 0
                            ? `No vulnerabilities recorded for ${selectedTarget}`
                            : "No results match the current filter"}
                        </p>
                        {findings.length === 0 && (
                          <p className="text-xs opacity-70">
                            Run a Vulnerability or Full scan to populate this view
                          </p>
                        )}
                      </div>
                    </td>
                  </tr>
                )}
                {filtered.map((item, idx) => (
                  <tr
                    key={item.id ?? idx}
                    onClick={() => setActiveFinding(item)}
                    className="hover:bg-slate-800/30 cursor-pointer transition-colors group"
                  >
                    <td className="px-5 py-3">
                      <span className={cn("px-2 py-0.5 rounded text-[10px] font-bold border", getSeverityBadge(item.severity))}>
                        {item.severity}
                      </span>
                    </td>
                    <td className="px-5 py-3 font-semibold text-slate-200 group-hover:text-blue-400 transition-colors">
                      {item.title}
                    </td>
                    <td className="px-5 py-3 text-blue-300">{item.target}</td>
                    <td className="px-5 py-3 text-slate-400">
                      <span className="px-2 py-0.5 rounded bg-slate-800 border border-slate-700 text-[10px]">
                        {item.category || "General"}
                      </span>
                    </td>
                    <td className="px-5 py-3 text-right">
                      <button className="text-blue-400 hover:text-blue-300 font-medium text-xs">
                        Inspect PoC
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Finding Detail Drawer Modal */}
      {activeFinding && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/80 backdrop-blur-sm p-4">
          <div className="relative w-full max-w-2xl rounded-2xl border border-slate-800 bg-[#0A0E17] shadow-2xl overflow-hidden p-6 space-y-5">
            <div className="flex items-start justify-between pb-4 border-b border-slate-800">
              <div>
                <div className="flex items-center gap-2 mb-1.5">
                  <span className={cn("px-2 py-0.5 rounded text-[10px] font-bold border font-mono", getSeverityBadge(activeFinding.severity))}>
                    {activeFinding.severity}
                  </span>
                  <span className="text-xs text-blue-400 font-mono">{activeFinding.target}</span>
                </div>
                <h3 className="text-base font-bold text-white font-mono">{activeFinding.title}</h3>
              </div>
              <button onClick={() => setActiveFinding(null)} className="p-1.5 text-slate-400 hover:text-white rounded-lg hover:bg-slate-800">
                <X className="h-4 w-4" />
              </button>
            </div>

            {activeFinding.description && (
              <div className="space-y-1.5">
                <h4 className="text-xs font-semibold uppercase tracking-wider text-slate-400 font-mono">Technical Description</h4>
                <p className="text-xs text-slate-300 leading-relaxed font-mono">{activeFinding.description}</p>
              </div>
            )}

            {activeFinding.poc && (
              <div className="space-y-1.5">
                <div className="flex items-center justify-between">
                  <h4 className="text-xs font-semibold uppercase tracking-wider text-slate-400 font-mono">Reproduction PoC</h4>
                  <button onClick={handleCopyPoC} className="flex items-center gap-1 text-[11px] text-blue-400 hover:text-blue-300 font-mono">
                    {copied ? <Check className="h-3 w-3 text-emerald-400" /> : <Copy className="h-3 w-3" />}
                    <span>{copied ? "Copied" : "Copy"}</span>
                  </button>
                </div>
                <pre className="p-3 rounded-xl bg-slate-950 border border-slate-800 text-xs text-emerald-400 font-mono overflow-x-auto">
                  <code>{activeFinding.poc}</code>
                </pre>
              </div>
            )}

            {activeFinding.remediation && (
              <div className="space-y-1.5">
                <h4 className="text-xs font-semibold uppercase tracking-wider text-slate-400 font-mono">Remediation</h4>
                <div className="p-3 rounded-xl bg-emerald-950/30 border border-emerald-900/40 text-xs text-slate-300 font-mono leading-relaxed">
                  {activeFinding.remediation}
                </div>
              </div>
            )}

            <div className="flex justify-end pt-2">
              <button onClick={() => setActiveFinding(null)} className="px-4 py-2 rounded-xl text-xs font-mono font-medium text-slate-300 bg-slate-800 hover:bg-slate-700 transition-colors">
                Close
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
