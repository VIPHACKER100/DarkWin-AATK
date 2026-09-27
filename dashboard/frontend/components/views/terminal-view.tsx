"use client";

import React, { useState, useRef, useEffect } from "react";
import {
  Terminal as TerminalIcon,
  Search,
  Download,
  Trash2,
  Copy,
  Check,
  Maximize2,
  Minimize2,
  Radio,
  ArrowDown,
} from "lucide-react";
import { CurrentScan } from "@/lib/api";
import { cn } from "@/lib/utils";

interface TerminalViewProps {
  logs: string[];
  currentScan: CurrentScan;
  onClearLogs: () => void;
}

export function TerminalView({ logs, currentScan, onClearLogs }: TerminalViewProps) {
  const [filterLevel, setFilterLevel] = useState<string>("ALL");
  const [search, setSearch] = useState("");
  const [autoScroll, setAutoScroll] = useState(true);
  const [copied, setCopied] = useState(false);
  const logEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (autoScroll) {
      logEndRef.current?.scrollIntoView({ behavior: "smooth" });
    }
  }, [logs, autoScroll]);

  const handleCopyLogs = () => {
    navigator.clipboard.writeText(logs.join("\n"));
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const handleDownloadLogs = () => {
    const blob = new Blob([logs.join("\n")], { type: "text/plain;charset=utf-8" });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = `darkwin_${currentScan.scan_id || "session"}.log`;
    link.click();
    URL.revokeObjectURL(url);
  };

  const filteredLogs = logs.filter((line) => {
    const matchesSearch = !search || line.toLowerCase().includes(search.toLowerCase());
    if (!matchesSearch) return false;
    if (filterLevel === "SUCCESS") return line.includes("[+]") || line.includes("SUCCESS");
    if (filterLevel === "WARN") return line.includes("[!]") || line.includes("WARN");
    if (filterLevel === "ERROR") return line.includes("[-]") || line.includes("ERROR");
    if (filterLevel === "INFO") return line.includes("[*]") || line.includes("INFO");
    return true;
  });

  const colorizeLine = (line: string) => {
    if (line.includes("[+]") || line.includes("SUCCESS")) {
      return <span className="text-emerald-400">{line}</span>;
    }
    if (line.includes("[-]") || line.includes("ERROR")) {
      return <span className="text-rose-400">{line}</span>;
    }
    if (line.includes("[!]") || line.includes("WARN")) {
      return <span className="text-amber-400">{line}</span>;
    }
    if (line.includes("[*]") || line.includes("INFO")) {
      return <span className="text-cyan-400">{line}</span>;
    }
    return <span className="text-slate-300">{line}</span>;
  };

  return (
    <div className="glass-panel rounded-2xl border border-slate-800 flex flex-col h-[calc(100vh-140px)] overflow-hidden shadow-2xl">
      {/* Terminal Title Bar */}
      <div className="flex flex-wrap items-center justify-between gap-4 px-6 py-4 border-b border-slate-800/80 bg-slate-900/60 shrink-0">
        <div className="flex items-center gap-3">
          <div className="flex items-center gap-1.5">
            <span className="h-3 w-3 rounded-full bg-rose-500/80" />
            <span className="h-3 w-3 rounded-full bg-amber-500/80" />
            <span className="h-3 w-3 rounded-full bg-emerald-500/80" />
          </div>
          <span className="text-xs font-mono font-bold text-slate-300 ml-2 flex items-center gap-2">
            <TerminalIcon className="h-4 w-4 text-blue-400" />
            TELEMETRY STREAM: {currentScan.scan_id || "IDLE"}
          </span>
          {currentScan.status === "running" && (
            <span className="px-2 py-0.5 rounded-full bg-cyan-950 text-cyan-400 border border-cyan-500/30 text-[10px] font-mono animate-pulse">
              LIVE
            </span>
          )}
        </div>

        {/* Controls */}
        <div className="flex items-center gap-2 flex-wrap">
          {/* Level Filter */}
          <select
            value={filterLevel}
            onChange={(e) => setFilterLevel(e.target.value)}
            className="px-2.5 py-1 text-xs rounded-lg bg-slate-900 border border-slate-800 text-slate-300 font-mono focus:outline-none"
          >
            <option value="ALL">All Levels</option>
            <option value="SUCCESS">Success [+]</option>
            <option value="WARN">Warnings [!]</option>
            <option value="ERROR">Errors [-]</option>
            <option value="INFO">Info [*]</option>
          </select>

          {/* Search */}
          <div className="relative w-44">
            <Search className="absolute left-2.5 top-1/2 -translate-y-1/2 h-3 w-3 text-slate-500" />
            <input
              type="text"
              placeholder="Search output..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="w-full pl-7 pr-2.5 py-1 text-xs rounded-lg bg-slate-900 border border-slate-800 text-slate-200 placeholder-slate-500 font-mono focus:outline-none"
            />
          </div>

          {/* Auto scroll toggle */}
          <button
            onClick={() => setAutoScroll(!autoScroll)}
            className={cn(
              "px-2.5 py-1 rounded-lg text-xs font-mono border transition-colors flex items-center gap-1",
              autoScroll
                ? "bg-blue-600/20 text-blue-400 border-blue-500/40"
                : "bg-slate-900 text-slate-400 border-slate-800"
            )}
            title="Auto-scroll"
          >
            <ArrowDown className="h-3 w-3" />
            <span>Scroll</span>
          </button>

          {/* Copy */}
          <button
            onClick={handleCopyLogs}
            className="p-1.5 rounded-lg bg-slate-900 border border-slate-800 text-slate-400 hover:text-white transition-colors"
            title="Copy Logs"
          >
            {copied ? <Check className="h-3.5 w-3.5 text-emerald-400" /> : <Copy className="h-3.5 w-3.5" />}
          </button>

          {/* Download */}
          <button
            onClick={handleDownloadLogs}
            className="p-1.5 rounded-lg bg-slate-900 border border-slate-800 text-slate-400 hover:text-white transition-colors"
            title="Download Log File"
          >
            <Download className="h-3.5 w-3.5" />
          </button>

          {/* Clear */}
          <button
            onClick={onClearLogs}
            className="p-1.5 rounded-lg bg-slate-900 border border-slate-800 text-slate-400 hover:text-red-400 transition-colors"
            title="Clear Terminal View"
          >
            <Trash2 className="h-3.5 w-3.5" />
          </button>
        </div>
      </div>

      {/* Terminal Viewport */}
      <div className="flex-1 bg-[#05070B] p-5 font-mono text-xs overflow-y-auto space-y-1 select-text">
        {filteredLogs.length === 0 ? (
          <div className="h-full flex items-center justify-center text-slate-600">
            Waiting for scan telemetry... Start a scan to inspect real-time tool output.
          </div>
        ) : (
          filteredLogs.map((line, idx) => (
            <div key={idx} className="leading-relaxed hover:bg-slate-900/40 px-1 rounded">
              <span className="text-slate-600 mr-3 select-none">{String(idx + 1).padStart(4, "0")}</span>
              {colorizeLine(line)}
            </div>
          ))
        )}
        <div ref={logEndRef} />
      </div>

      {/* Terminal Status Bar */}
      <div className="px-6 py-2 border-t border-slate-800/80 bg-slate-900/60 text-[11px] font-mono text-slate-400 flex items-center justify-between shrink-0">
        <span>Lines: {filteredLogs.length} / {logs.length}</span>
        <span>DarkWin Terminal v1.3</span>
      </div>
    </div>
  );
}
