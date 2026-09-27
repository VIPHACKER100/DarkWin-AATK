"use client";

import React, { useState, useEffect } from "react";
import {
  Wrench,
  CheckCircle2,
  XCircle,
  RefreshCw,
  Search,
  AlertTriangle,
  ChevronDown,
  ChevronRight,
  Copy,
  Check,
  Terminal,
  Layers,
} from "lucide-react";
import { getToolsDetailed } from "@/lib/api";
import { cn } from "@/lib/utils";

interface ToolInfo {
  binary: string;
  installed: boolean;
  path: string;
  category: string;
  description?: string;
  install_command?: string;
}

const CATEGORY_META: Record<string, { color: string; bg: string; border: string; icon: string }> = {
  Recon:         { color: "text-cyan-400",   bg: "bg-cyan-950/40",    border: "border-cyan-500/30",  icon: "🔭" },
  "Web Discovery": { color: "text-blue-400", bg: "bg-blue-950/40",   border: "border-blue-500/30",  icon: "🌐" },
  Vulnerability: { color: "text-red-400",    bg: "bg-red-950/40",    border: "border-red-500/30",   icon: "🛡️" },
  Fuzzing:       { color: "text-amber-400",  bg: "bg-amber-950/40",  border: "border-amber-500/30", icon: "🎯" },
  Network:       { color: "text-emerald-400",bg: "bg-emerald-950/40",border: "border-emerald-500/30",icon: "📡" },
  OSINT:         { color: "text-purple-400", bg: "bg-purple-950/40", border: "border-purple-500/30",icon: "👁️" },
  Cloud:         { color: "text-sky-400",    bg: "bg-sky-950/40",    border: "border-sky-500/30",   icon: "☁️" },
  Exploitation:  { color: "text-rose-400",   bg: "bg-rose-950/40",   border: "border-rose-500/30",  icon: "💣" },
  General:       { color: "text-slate-400",  bg: "bg-slate-800/40",  border: "border-slate-500/30", icon: "🔧" },
};

function CopyButton({ text }: { text: string }) {
  const [copied, setCopied] = useState(false);
  const handleCopy = () => {
    navigator.clipboard.writeText(text).catch(() => {});
    setCopied(true);
    setTimeout(() => setCopied(false), 1500);
  };
  return (
    <button
      onClick={handleCopy}
      className="p-1 rounded text-slate-500 hover:text-slate-200 transition-colors"
      title="Copy install command"
    >
      {copied ? <Check className="h-3 w-3 text-emerald-400" /> : <Copy className="h-3 w-3" />}
    </button>
  );
}

function ToolCard({ name, info }: { name: string; info: ToolInfo }) {
  const [open, setOpen] = useState(false);
  const cat = CATEGORY_META[info.category] || CATEGORY_META.General;

  return (
    <div
      className={cn(
        "rounded-xl border transition-all duration-200",
        info.installed
          ? "bg-slate-900/40 border-slate-800/80 hover:border-slate-700"
          : "bg-slate-900/20 border-slate-800/40 hover:border-amber-700/30"
      )}
    >
      {/* Card Header */}
      <div
        className="flex items-center gap-3 p-3.5 cursor-pointer select-none"
        onClick={() => setOpen(!open)}
      >
        {/* Status Indicator */}
        <div className="shrink-0">
          {info.installed ? (
            <CheckCircle2 className="h-4.5 w-4.5 text-emerald-400" style={{ width: 18, height: 18 }} />
          ) : (
            <XCircle className="h-4.5 w-4.5 text-rose-500" style={{ width: 18, height: 18 }} />
          )}
        </div>

        {/* Tool Info */}
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2 flex-wrap">
            <span className="text-sm font-bold text-slate-100 font-mono tracking-tight">{name}</span>
            <span className={cn("text-[10px] px-1.5 py-0.5 rounded font-mono font-semibold border", cat.bg, cat.color, cat.border)}>
              {cat.icon} {info.category}
            </span>
            {info.installed && (
              <span className="text-[10px] text-emerald-400 font-mono">READY</span>
            )}
          </div>
          {info.description && (
            <p className="text-[11px] text-slate-500 mt-0.5 truncate">{info.description}</p>
          )}
        </div>

        {/* Expand arrow */}
        <div className="shrink-0 text-slate-600">
          {open ? <ChevronDown className="h-3.5 w-3.5" /> : <ChevronRight className="h-3.5 w-3.5" />}
        </div>
      </div>

      {/* Expanded Details */}
      {open && (
        <div className="px-3.5 pb-3.5 border-t border-slate-800/60 pt-3 space-y-2.5">
          {info.description && (
            <p className="text-xs text-slate-400 leading-relaxed">{info.description}</p>
          )}

          {/* Binary path */}
          <div className="space-y-1">
            <div className="text-[10px] font-mono text-slate-500 uppercase tracking-wider">Binary</div>
            <div className="flex items-center gap-2 px-2.5 py-1.5 rounded-lg bg-slate-950 border border-slate-800 font-mono text-xs">
              <Terminal className="h-3 w-3 text-slate-500 shrink-0" />
              <span className={info.installed ? "text-slate-300" : "text-rose-400/70"}>
                {info.binary}
              </span>
              {info.installed && info.path && (
                <span className="text-slate-600 truncate text-[10px] ml-auto">{info.path}</span>
              )}
            </div>
          </div>

          {/* Install command (only for missing tools) */}
          {!info.installed && info.install_command && (
            <div className="space-y-1">
              <div className="text-[10px] font-mono text-slate-500 uppercase tracking-wider">Install Command</div>
              <div className="flex items-center gap-2 px-2.5 py-1.5 rounded-lg bg-amber-950/20 border border-amber-700/30">
                <code className="font-mono text-xs text-amber-300 flex-1 truncate">
                  {info.install_command}
                </code>
                <CopyButton text={info.install_command} />
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}

export function ToolsView() {
  const [tools, setTools] = useState<Record<string, ToolInfo>>({});
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState("");
  const [activeCategory, setActiveCategory] = useState<string>("All");

  const fetchTools = () => {
    setLoading(true);
    getToolsDetailed()
      .then((data) => setTools(data as Record<string, ToolInfo>))
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
  const readyPercent = total > 0 ? Math.round((installedCount / total) * 100) : 0;

  // Build category list
  const categories = ["All", ...Array.from(new Set(toolEntries.map(([, info]) => info.category))).sort()];

  const filtered = toolEntries.filter(([name, info]) => {
    const matchSearch =
      name.toLowerCase().includes(search.toLowerCase()) ||
      (info.description || "").toLowerCase().includes(search.toLowerCase()) ||
      (info.binary || "").toLowerCase().includes(search.toLowerCase());
    const matchCat = activeCategory === "All" || info.category === activeCategory;
    return matchSearch && matchCat;
  });

  // Group by category
  const grouped: Record<string, [string, ToolInfo][]> = {};
  for (const [name, info] of filtered) {
    const cat = info.category;
    if (!grouped[cat]) grouped[cat] = [];
    grouped[cat].push([name, info]);
  }

  return (
    <div className="space-y-5">
      {/* Stats Banner */}
      <div className="glass-panel p-5 rounded-2xl border border-slate-800">
        <div className="flex flex-wrap items-start justify-between gap-4">
          <div className="flex-1 min-w-0">
            <h2 className="text-sm font-bold text-white font-mono flex items-center gap-2">
              <Wrench className="h-4 w-4 text-blue-400 shrink-0" />
              Security Binary Arsenal &amp; Environment
            </h2>
            <p className="text-xs text-slate-400 mt-1">
              Status of {total} external CLI tools discovered across system $PATH
            </p>

            {/* Progress Bar */}
            <div className="mt-3 space-y-1.5">
              <div className="flex justify-between text-[10px] font-mono text-slate-500">
                <span>{installedCount}/{total} tools operational</span>
                <span
                  className={cn(
                    "font-semibold",
                    readyPercent === 100 ? "text-emerald-400" : readyPercent >= 60 ? "text-amber-400" : "text-rose-400"
                  )}
                >
                  {readyPercent}% ready
                </span>
              </div>
              <div className="h-2 bg-slate-800 rounded-full overflow-hidden">
                <div
                  className={cn(
                    "h-full rounded-full transition-all duration-700",
                    readyPercent === 100 ? "bg-emerald-500" : readyPercent >= 60 ? "bg-amber-500" : "bg-rose-500"
                  )}
                  style={{ width: `${readyPercent}%` }}
                />
              </div>
            </div>
          </div>

          <div className="flex items-center gap-3 flex-wrap">
            <div className="flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-emerald-950/60 border border-emerald-500/30 text-emerald-400 font-mono text-xs">
              <CheckCircle2 className="h-3.5 w-3.5" />
              <span>{installedCount} Operational</span>
            </div>
            {missingCount > 0 && (
              <div className="flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-amber-950/60 border border-amber-500/30 text-amber-400 font-mono text-xs">
                <AlertTriangle className="h-3.5 w-3.5" />
                <span>{missingCount} Missing</span>
              </div>
            )}
            <button
              onClick={fetchTools}
              disabled={loading}
              className="flex items-center gap-2 px-3 py-1.5 rounded-xl bg-slate-900 border border-slate-800 text-slate-300 hover:text-white font-mono text-xs transition-colors disabled:opacity-50"
            >
              <RefreshCw className={cn("h-3.5 w-3.5", loading && "animate-spin")} />
              <span>Re-Audit</span>
            </button>
          </div>
        </div>
      </div>

      {/* Search + Category Filters */}
      <div className="flex flex-wrap gap-3 items-center">
        <div className="relative flex-1 min-w-[180px] max-w-sm">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-3.5 w-3.5 text-slate-500" />
          <input
            type="text"
            placeholder="Search tools, categories..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="w-full pl-8 pr-3 py-2 text-xs rounded-xl bg-slate-900 border border-slate-800 text-slate-200 placeholder-slate-500 focus:outline-none focus:border-blue-500 font-mono"
          />
        </div>

        {/* Category tabs */}
        <div className="flex items-center gap-1.5 overflow-x-auto pb-0.5 flex-wrap">
          {categories.map((cat) => {
            const meta = CATEGORY_META[cat] || CATEGORY_META.General;
            const count = cat === "All" ? total : toolEntries.filter(([, i]) => i.category === cat).length;
            const isActive = activeCategory === cat;
            return (
              <button
                key={cat}
                onClick={() => setActiveCategory(cat)}
                className={cn(
                  "flex items-center gap-1.5 px-2.5 py-1 rounded-lg text-[11px] font-mono font-semibold transition-all border whitespace-nowrap shrink-0",
                  isActive
                    ? cat === "All"
                      ? "bg-blue-600/20 text-blue-400 border-blue-500/40"
                      : `${meta.bg} ${meta.color} ${meta.border}`
                    : "bg-slate-900/60 text-slate-500 border-slate-800 hover:text-slate-300 hover:border-slate-700"
                )}
              >
                {cat !== "All" && <Layers className="h-3 w-3" />}
                <span>{cat}</span>
                <span className="text-[9px] opacity-70">({count})</span>
              </button>
            );
          })}
        </div>
      </div>

      {/* Loading State */}
      {loading && (
        <div className="flex items-center justify-center py-16 text-slate-500">
          <RefreshCw className="h-5 w-5 animate-spin mr-3" />
          <span className="font-mono text-xs">Auditing environment...</span>
        </div>
      )}

      {/* Empty State */}
      {!loading && filtered.length === 0 && (
        <div className="text-center py-16 space-y-2 text-slate-500 font-mono text-xs">
          <Search className="h-8 w-8 mx-auto opacity-30" />
          <p>No tools found matching &ldquo;{search}&rdquo;.</p>
          <button onClick={() => { setSearch(""); setActiveCategory("All"); }} className="text-blue-400 hover:underline text-xs">
            Clear filters
          </button>
        </div>
      )}

      {/* Tool Groups */}
      {!loading && Object.entries(grouped).sort().map(([category, entries]) => {
        const meta = CATEGORY_META[category] || CATEGORY_META.General;
        const installedInCat = entries.filter(([, i]) => i.installed).length;
        return (
          <div key={category} className="space-y-2">
            {/* Category Header */}
            <div className="flex items-center gap-3">
              <div className={cn("flex items-center gap-2 px-3 py-1 rounded-lg border text-xs font-mono font-bold", meta.bg, meta.color, meta.border)}>
                <span>{meta.icon}</span>
                <span>{category}</span>
              </div>
              <span className="text-[10px] text-slate-600 font-mono">
                {installedInCat}/{entries.length} ready
              </span>
              <div className="flex-1 h-px bg-slate-800/60" />
            </div>

            {/* Tool Cards Grid */}
            <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-2.5">
              {entries.map(([name, info]) => (
                <ToolCard key={name} name={name} info={info} />
              ))}
            </div>
          </div>
        );
      })}
    </div>
  );
}
