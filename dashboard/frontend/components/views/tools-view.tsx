"use client";

import React, { useState, useEffect } from "react";
import {
  Wrench,
  CheckCircle2,
  XCircle,
  RefreshCw,
  Search,
  AlertTriangle,
} from "lucide-react";
import { getToolsDetailed } from "@/lib/api";
import { cn } from "@/lib/utils";

export function ToolsView() {
  const [tools, setTools] = useState<Record<string, { path: string; installed: boolean; category?: string }>>({});
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState("");

  const fetchTools = () => {
    setLoading(true);
    getToolsDetailed()
      .then(setTools)
      .catch(() => setTools({}))
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    fetchTools();
  }, []);

  const toolEntries = Object.entries(tools);
  const total = toolEntries.length;
  const installedCount = toolEntries.filter(([, info]) => info.installed).length;
  const missingCount = total - installedCount;

  const filtered = toolEntries.filter(([name, info]) =>
    name.toLowerCase().includes(search.toLowerCase()) ||
    (info.path || "").toLowerCase().includes(search.toLowerCase())
  );

  return (
    <div className="space-y-6">
      {/* Top Arsenal Status Banner */}
      <div className="glass-panel p-6 rounded-2xl border border-slate-800 flex flex-wrap items-center justify-between gap-4">
        <div>
          <h2 className="text-base font-bold text-white font-mono flex items-center gap-2">
            <Wrench className="h-5 w-5 text-blue-400" />
            Security Binary Arsenal & Diagnostics
          </h2>
          <p className="text-xs text-slate-400 mt-1">
            Status of external CLI tools discovered across system $PATH
          </p>
        </div>

        <div className="flex items-center gap-4">
          <div className="flex items-center gap-3">
            <div className="px-3 py-1.5 rounded-xl bg-emerald-950/60 border border-emerald-500/30 text-emerald-400 font-mono text-xs flex items-center gap-1.5">
              <CheckCircle2 className="h-3.5 w-3.5" />
              <span>{installedCount} Operational</span>
            </div>
            {missingCount > 0 && (
              <div className="px-3 py-1.5 rounded-xl bg-amber-950/60 border border-amber-500/30 text-amber-400 font-mono text-xs flex items-center gap-1.5">
                <AlertTriangle className="h-3.5 w-3.5" />
                <span>{missingCount} Missing</span>
              </div>
            )}
          </div>

          <button
            onClick={fetchTools}
            className="flex items-center gap-2 px-3 py-1.5 rounded-xl bg-slate-900 border border-slate-800 text-slate-300 hover:text-white font-mono text-xs transition-colors"
          >
            <RefreshCw className={cn("h-3.5 w-3.5", loading && "animate-spin")} />
            <span>Re-Audit</span>
          </button>
        </div>
      </div>

      {/* Search */}
      <div className="relative w-full max-w-md">
        <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-3.5 w-3.5 text-slate-500" />
        <input
          type="text"
          placeholder="Filter tools by binary name or path..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          className="w-full pl-8 pr-3 py-2 text-xs rounded-xl bg-slate-900 border border-slate-800 text-slate-200 placeholder-slate-500 focus:outline-none focus:border-blue-500 font-mono"
        />
      </div>

      {/* Tool Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
        {filtered.map(([name, info]) => (
          <div
            key={name}
            className="glass-panel p-4 rounded-xl border border-slate-800/80 hover:border-slate-700 transition-all flex items-center justify-between"
          >
            <div className="overflow-hidden">
              <div className="flex items-center gap-2">
                <span className="text-xs font-bold text-slate-200 font-mono">{name}</span>
                {info.category && (
                  <span className="text-[10px] px-1.5 py-0.2 rounded bg-slate-800 text-slate-400 font-mono">
                    {info.category}
                  </span>
                )}
              </div>
              <p className="text-[11px] text-slate-500 font-mono truncate mt-1">
                {info.path || "Not found on $PATH"}
              </p>
            </div>

            <div className="shrink-0 ml-3">
              {info.installed ? (
                <CheckCircle2 className="h-5 w-5 text-emerald-400" />
              ) : (
                <XCircle className="h-5 w-5 text-rose-500" />
              )}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
