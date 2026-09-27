"use client";

import React, { useState, useEffect } from "react";
import {
  Target,
  FileText,
  Copy,
  Check,
  Search,
  Trash2,
  ExternalLink,
  Layers,
  Globe,
  Radio,
  Server,
  Mail,
  FolderOpen,
  Eye,
  Download,
  AlertCircle,
  Clock,
} from "lucide-react";
import { TargetItem, TargetAssets, getTargetAssets, getReportUrl } from "@/lib/api";
import { cn } from "@/lib/utils";

interface TargetsViewProps {
  targets: TargetItem[];
  selectedTarget: string | null;
  onSelectTarget: (target: string) => void;
  onDeleteTarget: (target: string) => Promise<void>;
  onDeleteSession: (target: string, session: string) => Promise<void>;
}

export function TargetsView({
  targets,
  selectedTarget,
  onSelectTarget,
  onDeleteTarget,
  onDeleteSession,
}: TargetsViewProps) {
  const [targetSearch, setTargetSearch] = useState("");
  const [activeTab, setActiveTab] = useState<"subdomains" | "ports" | "urls" | "emails" | "artifacts" | "report">("subdomains");
  const [assets, setAssets] = useState<TargetAssets | null>(null);
  const [loadingAssets, setLoadingAssets] = useState(false);
  const [copied, setCopied] = useState(false);
  const [selectedSession, setSelectedSession] = useState<string | null>(null);

  const currentTargetObj = targets.find((t) => t.target === selectedTarget) || targets[0];

  useEffect(() => {
    if (currentTargetObj) {
      if (!selectedSession && currentTargetObj.sessions.length > 0) {
        setSelectedSession(currentTargetObj.sessions[0].name);
      }
      setLoadingAssets(true);
      getTargetAssets(currentTargetObj.target)
        .then(setAssets)
        .catch(() => setAssets(null))
        .finally(() => setLoadingAssets(false));
    }
  }, [currentTargetObj, selectedSession]);

  const filteredTargets = targets.filter((t) =>
    t.target.toLowerCase().includes(targetSearch.toLowerCase())
  );

  const handleCopySubdomains = () => {
    if (!assets?.subdomains) return;
    const text = assets.subdomains.map((s) => s.host).join("\n");
    navigator.clipboard.writeText(text);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 h-[calc(100vh-140px)]">
      {/* Left Column: Target Selector (4 cols) */}
      <div className="lg:col-span-4 glass-panel rounded-2xl border border-slate-800 p-4 flex flex-col h-full overflow-hidden">
        <div className="flex items-center justify-between mb-3">
          <h2 className="text-xs font-bold uppercase tracking-wider text-slate-300 font-mono-label flex items-center gap-2">
            <Target className="h-4 w-4 text-blue-400" />
            Target Directory ({targets.length})
          </h2>
        </div>

        {/* Search targets */}
        <div className="relative mb-3">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-3.5 w-3.5 text-slate-500" />
          <input
            type="text"
            placeholder="Filter targets..."
            value={targetSearch}
            onChange={(e) => setTargetSearch(e.target.value)}
            className="w-full pl-8 pr-3 py-1.5 text-xs rounded-xl bg-slate-900 border border-slate-800 text-slate-200 placeholder-slate-500 focus:outline-none focus:border-blue-500 font-mono"
          />
        </div>

        {/* Target List */}
        <div className="flex-1 overflow-y-auto space-y-1.5 pr-1">
          {filteredTargets.map((t) => {
            const isSelected = (selectedTarget || currentTargetObj?.target) === t.target;
            const hasReport = t.sessions.some((s) => s.hasReport);
            return (
              <div
                key={t.target}
                onClick={() => {
                  onSelectTarget(t.target);
                  if (t.sessions.length > 0) setSelectedSession(t.sessions[0].name);
                }}
                className={cn(
                  "p-3 rounded-xl border cursor-pointer transition-all flex items-center justify-between group",
                  isSelected
                    ? "bg-blue-950/40 border-blue-500/50 shadow-md ring-1 ring-blue-500/30"
                    : "bg-slate-900/30 border-slate-800/80 hover:bg-slate-900/70 hover:border-slate-700"
                )}
              >
                <div className="overflow-hidden">
                  <h3
                    className={cn(
                      "text-xs font-bold font-mono truncate",
                      isSelected ? "text-blue-300" : "text-slate-200"
                    )}
                  >
                    {t.target}
                  </h3>
                  <div className="flex items-center gap-2 text-[10px] text-slate-500 font-mono mt-0.5">
                    <span>{t.sessions.length} sessions</span>
                    {hasReport && (
                      <span className="text-emerald-400 bg-emerald-950/40 px-1 rounded border border-emerald-500/30">
                        Report Ready
                      </span>
                    )}
                  </div>
                </div>

                <button
                  onClick={(e) => {
                    e.stopPropagation();
                    if (confirm(`Delete target ${t.target} and all results?`)) {
                      onDeleteTarget(t.target);
                    }
                  }}
                  className="opacity-0 group-hover:opacity-100 p-1.5 text-slate-500 hover:text-red-400 transition-all rounded"
                  title="Delete target"
                >
                  <Trash2 className="h-3.5 w-3.5" />
                </button>
              </div>
            );
          })}
        </div>
      </div>

      {/* Right Column: Asset Details & Intelligence (8 cols) */}
      <div className="lg:col-span-8 glass-panel rounded-2xl border border-slate-800 p-6 flex flex-col h-full overflow-hidden">
        {currentTargetObj ? (
          <>
            {/* Top Target Context Header */}
            <div className="flex flex-wrap items-center justify-between gap-4 pb-4 border-b border-slate-800/80 shrink-0">
              <div>
                <div className="flex items-center gap-2">
                  <h2 className="text-lg font-bold text-white font-mono">{currentTargetObj.target}</h2>
                  <span className="text-[10px] uppercase font-mono px-2 py-0.5 rounded-full bg-blue-950 text-blue-400 border border-blue-500/30">
                    Scope Active
                  </span>
                </div>
                <p className="text-xs text-slate-400 mt-0.5">
                  Target assets discovered by automated scanning engines
                </p>
              </div>

              {/* Session Selector */}
              {currentTargetObj.sessions.length > 0 && (
                <div className="flex items-center gap-2">
                  <Clock className="h-3.5 w-3.5 text-slate-500" />
                  <select
                    value={selectedSession || ""}
                    onChange={(e) => setSelectedSession(e.target.value)}
                    className="px-2.5 py-1 text-xs rounded-lg bg-slate-900 border border-slate-800 text-slate-300 font-mono focus:outline-none focus:border-blue-500"
                  >
                    {currentTargetObj.sessions.map((s) => (
                      <option key={s.name} value={s.name}>
                        {s.name} {s.hasReport ? "★" : ""}
                      </option>
                    ))}
                  </select>
                </div>
              )}
            </div>

            {/* Asset Category Tabs */}
            <div className="flex items-center gap-2 py-3 border-b border-slate-800/60 overflow-x-auto shrink-0">
              {[
                { id: "subdomains", label: "Subdomains", count: assets?.subdomains?.length ?? 0, icon: Globe },
                { id: "ports", label: "Ports & Services", count: assets?.ports?.length ?? 0, icon: Server },
                { id: "urls", label: "Crawled URLs", count: assets?.urls?.length ?? 0, icon: Layers },
                { id: "emails", label: "OSINT & Emails", count: assets?.emails?.length ?? 0, icon: Mail },
                { id: "artifacts", label: "Artifacts", count: assets?.artifacts?.length ?? 0, icon: FolderOpen },
                { id: "report", label: "Executive Report", count: null, icon: FileText },
              ].map((tab) => {
                const Icon = tab.icon;
                const isActive = activeTab === tab.id;
                return (
                  <button
                    key={tab.id}
                    onClick={() => setActiveTab(tab.id as any)}
                    className={cn(
                      "flex items-center gap-2 px-3 py-1.5 rounded-lg text-xs font-mono font-medium transition-all shrink-0",
                      isActive
                        ? "bg-blue-600/20 text-blue-400 border border-blue-500/40"
                        : "text-slate-400 hover:text-slate-200 hover:bg-slate-900 border border-transparent"
                    )}
                  >
                    <Icon className="h-3.5 w-3.5" />
                    <span>{tab.label}</span>
                    {tab.count !== null && (
                      <span className="text-[10px] px-1.5 py-0.2 rounded bg-slate-800 text-slate-300">
                        {tab.count}
                      </span>
                    )}
                  </button>
                );
              })}
            </div>

            {/* Tab Contents Viewport */}
            <div className="flex-1 overflow-y-auto mt-4 pr-1">
              {loadingAssets ? (
                <div className="h-full flex items-center justify-center text-slate-500 font-mono text-xs">
                  Loading target telemetry...
                </div>
              ) : activeTab === "subdomains" ? (
                <div className="space-y-3">
                  <div className="flex items-center justify-between">
                    <span className="text-xs text-slate-400 font-mono">
                      Discovered {assets?.subdomains?.length ?? 0} unique domain assets
                    </span>
                    <button
                      onClick={handleCopySubdomains}
                      className="flex items-center gap-1.5 px-2.5 py-1 text-xs rounded-lg bg-slate-900 border border-slate-800 text-slate-300 hover:text-white transition-colors font-mono"
                    >
                      {copied ? <Check className="h-3 w-3 text-emerald-400" /> : <Copy className="h-3 w-3" />}
                      <span>{copied ? "Copied!" : "Copy All"}</span>
                    </button>
                  </div>
                  <div className="border border-slate-800 rounded-xl overflow-hidden bg-slate-900/30">
                    <table className="w-full text-left text-xs font-mono">
                      <thead className="bg-slate-900/80 text-slate-400 border-b border-slate-800 uppercase text-[10px]">
                        <tr>
                          <th className="px-4 py-2.5">Hostname</th>
                          <th className="px-4 py-2.5">Status</th>
                          <th className="px-4 py-2.5">Technologies</th>
                        </tr>
                      </thead>
                      <tbody className="divide-y divide-slate-800/60">
                        {assets?.subdomains?.map((s, idx) => (
                          <tr key={idx} className="hover:bg-slate-800/30 transition-colors">
                            <td className="px-4 py-2 text-blue-300 font-medium">{s.host}</td>
                            <td className="px-4 py-2">
                              <span
                                className={cn(
                                  "px-1.5 py-0.5 rounded text-[10px] font-bold",
                                  s.status === 200
                                    ? "bg-emerald-950/60 text-emerald-400 border border-emerald-500/30"
                                    : "bg-amber-950/60 text-amber-400 border border-amber-500/30"
                                )}
                              >
                                {s.status}
                              </span>
                            </td>
                            <td className="px-4 py-2 text-slate-400">
                              <div className="flex gap-1 flex-wrap">
                                {s.tech?.map((t, i) => (
                                  <span key={i} className="px-1.5 py-0.2 rounded bg-slate-800 text-[10px]">
                                    {t}
                                  </span>
                                ))}
                              </div>
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </div>
              ) : activeTab === "ports" ? (
                <div className="space-y-3">
                  <p className="text-xs text-slate-400 font-mono">Open ports & detected services</p>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                    {assets?.ports && assets.ports.length > 0 ? (
                      assets.ports.map((p, i) => (
                        <div key={i} className="p-3 rounded-xl bg-slate-900/40 border border-slate-800 font-mono text-xs flex justify-between">
                          <div>
                            <span className="font-bold text-white">{p.port}</span>
                            <span className="text-slate-500 uppercase ml-1">/{p.protocol}</span>
                            <p className="text-[11px] text-blue-400 mt-0.5">{p.service}</p>
                          </div>
                          {p.version && <span className="text-[10px] text-slate-400">{p.version}</span>}
                        </div>
                      ))
                    ) : (
                      <div className="col-span-2 p-6 text-center text-xs text-slate-500 font-mono">
                        No open ports recorded in target artifacts yet.
                      </div>
                    )}
                  </div>
                </div>
              ) : activeTab === "urls" ? (
                <div className="space-y-2">
                  <p className="text-xs text-slate-400 font-mono">Crawled & Historical Web Endpoints</p>
                  <div className="bg-slate-900/60 border border-slate-800 rounded-xl p-3 max-h-96 overflow-y-auto space-y-1 font-mono text-xs">
                    {assets?.urls && assets.urls.length > 0 ? (
                      assets.urls.map((url, i) => (
                        <div key={i} className="truncate text-slate-300 hover:text-blue-400 transition-colors">
                          <a href={url.startsWith("http") ? url : `https://${url}`} target="_blank" rel="noreferrer">
                            {url}
                          </a>
                        </div>
                      ))
                    ) : (
                      <span className="text-slate-500">No URLs crawled yet.</span>
                    )}
                  </div>
                </div>
              ) : activeTab === "emails" ? (
                <div className="space-y-2">
                  <p className="text-xs text-slate-400 font-mono">Discovered Corporate Emails & Usernames</p>
                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 font-mono text-xs">
                    {assets?.emails && assets.emails.length > 0 ? (
                      assets.emails.map((email, i) => (
                        <div key={i} className="p-2.5 rounded-lg bg-slate-900 border border-slate-800 text-slate-300 flex items-center gap-2">
                          <Mail className="h-3.5 w-3.5 text-blue-400" />
                          <span className="truncate">{email}</span>
                        </div>
                      ))
                    ) : (
                      <span className="text-slate-500 text-xs">No email addresses discovered.</span>
                    )}
                  </div>
                </div>
              ) : activeTab === "artifacts" ? (
                <div className="space-y-2">
                  <p className="text-xs text-slate-400 font-mono">Raw Scan Artifact Files</p>
                  <div className="border border-slate-800 rounded-xl overflow-hidden bg-slate-900/30">
                    <table className="w-full text-left text-xs font-mono">
                      <thead className="bg-slate-900/80 text-slate-400 border-b border-slate-800 uppercase text-[10px]">
                        <tr>
                          <th className="px-4 py-2.5">File Name</th>
                          <th className="px-4 py-2.5">Relative Path</th>
                          <th className="px-4 py-2.5">Size</th>
                        </tr>
                      </thead>
                      <tbody className="divide-y divide-slate-800/60">
                        {assets?.artifacts?.map((art, idx) => (
                          <tr key={idx} className="hover:bg-slate-800/30">
                            <td className="px-4 py-2 text-slate-200 font-semibold">{art.name}</td>
                            <td className="px-4 py-2 text-slate-400">{art.path}</td>
                            <td className="px-4 py-2 text-slate-500">{(art.size / 1024).toFixed(1)} KB</td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </div>
              ) : (
                /* Report View Tab */
                <div className="h-[550px] w-full border border-slate-800 rounded-xl overflow-hidden bg-white">
                  {selectedSession ? (
                    <iframe
                      src={getReportUrl(currentTargetObj.target, selectedSession)}
                      className="w-full h-full border-0"
                      title="Scan Report"
                    />
                  ) : (
                    <div className="flex items-center justify-center h-full text-slate-600 font-mono text-xs">
                      No report available for this session.
                    </div>
                  )}
                </div>
              )}
            </div>
          </>
        ) : (
          <div className="flex items-center justify-center h-full text-slate-500 font-mono text-xs">
            Select a target to inspect assets and scan results.
          </div>
        )}
      </div>
    </div>
  );
}
