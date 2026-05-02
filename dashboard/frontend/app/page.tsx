"use client";

import { useState, useEffect, useRef } from "react";
import { 
  Activity, 
  Terminal, 
  Target, 
  FileText, 
  Zap, 
  Shield, 
  Clock, 
  ChevronRight,
  Maximize2,
  RefreshCcw,
  Search
} from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";
import { getTargets, getReportUrl } from "@/lib/api";
import { socket } from "@/lib/socket";

interface TargetData {
  target: string;
  sessions: string[];
}

export default function Dashboard() {
  const [targets, setTargets] = useState<TargetData[]>([]);
  const [selectedTarget, setSelectedTarget] = useState<string | null>(null);
  const [selectedSession, setSelectedSession] = useState<string | null>(null);
  const [logs, setLogs] = useState<string[]>([]);
  const [loading, setLoading] = useState(true);
  const logEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    fetchData();
    socket.connect();

    socket.on("scan_update", (data: { scan_id: string; line: string }) => {
      setLogs((prev) => [...prev.slice(-499), data.line]);
    });

    return () => {
      socket.disconnect();
    };
  }, []);

  useEffect(() => {
    logEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [logs]);

  const fetchData = async () => {
    try {
      const data = await getTargets();
      setTargets(data);
      if (data.length > 0 && !selectedTarget) {
        setSelectedTarget(data[0].target);
        if (data[0].sessions.length > 0) {
          setSelectedSession(data[0].sessions[0]);
        }
      }
    } catch (error) {
      console.error("Failed to fetch targets", error);
    } finally {
      setLoading(false);
    }
  };

  const handleSubscribe = (session: string) => {
    setLogs([]);
    socket.emit("subscribe", { scan_id: `${selectedTarget}/${session}` });
  };

  const currentTarget = targets.find((t) => t.target === selectedTarget);

  return (
    <div className="flex h-screen w-full bg-[#050505] text-white font-sans selection:bg-cyan-500/30">
      {/* ── Sidebar ──────────────────────────────────────────────────────── */}
      <aside className="w-80 border-r border-white/5 flex flex-col bg-[#0a0a0a]">
        <div className="p-6 border-b border-white/5 flex items-center gap-3">
          <div className="w-10 h-10 bg-cyan-500/10 rounded-lg flex items-center justify-center border border-cyan-500/20">
            <Shield className="w-6 h-6 text-cyan-400" />
          </div>
          <div>
            <h1 className="font-bold tracking-tight text-lg leading-tight">DARKWIN</h1>
            <p className="text-[10px] text-zinc-500 uppercase tracking-[0.2em]">Control Center v1.1.0</p>
          </div>
        </div>

        <div className="flex-1 overflow-y-auto p-4 space-y-2">
          <div className="flex items-center justify-between px-2 mb-4">
            <span className="text-[11px] font-bold text-zinc-500 uppercase tracking-wider">Targets</span>
            <button onClick={fetchData} className="p-1 hover:bg-white/5 rounded transition-colors">
              <RefreshCcw className="w-3 h-3 text-zinc-500" />
            </button>
          </div>

          {targets.map((t) => (
            <button
              key={t.target}
              onClick={() => {
                setSelectedTarget(t.target);
                setSelectedSession(t.sessions[0] || null);
              }}
              className={`w-full text-left p-3 rounded-lg flex items-center justify-between group transition-all ${
                selectedTarget === t.target ? "bg-cyan-500/10 border border-cyan-500/20" : "hover:bg-white/5"
              }`}
            >
              <div className="flex items-center gap-3">
                <Target className={`w-4 h-4 ${selectedTarget === t.target ? "text-cyan-400" : "text-zinc-500"}`} />
                <span className={`text-sm font-medium ${selectedTarget === t.target ? "text-white" : "text-zinc-400"}`}>
                  {t.target}
                </span>
              </div>
              <ChevronRight className={`w-4 h-4 transition-transform ${selectedTarget === t.target ? "translate-x-0 text-cyan-400" : "translate-x-4 opacity-0 group-hover:translate-x-0 group-hover:opacity-100 text-zinc-600"}`} />
            </button>
          ))}
        </div>

        <div className="p-4 border-t border-white/5 bg-black/20">
          <div className="flex items-center gap-3 p-3 bg-white/5 rounded-lg">
            <div className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse" />
            <span className="text-xs text-zinc-400 font-mono">System Online</span>
          </div>
        </div>
      </aside>

      {/* ── Main Content ──────────────────────────────────────────────────── */}
      <main className="flex-1 flex flex-col relative overflow-hidden">
        {/* Header */}
        <header className="h-20 border-b border-white/5 flex items-center justify-between px-8 bg-black/40 backdrop-blur-md z-10">
          <div className="flex items-center gap-6">
            <div>
              <h2 className="text-sm font-bold text-zinc-500 uppercase tracking-widest mb-1">Active Session</h2>
              <div className="flex items-center gap-2">
                <p className="text-lg font-bold tracking-tight">{selectedTarget || "No Target"}</p>
                {selectedSession && (
                  <>
                    <ChevronRight className="w-4 h-4 text-zinc-700" />
                    <span className="text-zinc-400 font-mono text-sm">{selectedSession}</span>
                  </>
                )}
              </div>
            </div>
          </div>

          <div className="flex items-center gap-4">
            <select 
              value={selectedSession || ""} 
              onChange={(e) => setSelectedSession(e.target.value)}
              className="bg-white/5 border border-white/10 rounded-md px-3 py-1.5 text-xs font-mono outline-none focus:border-cyan-500/50 transition-colors"
            >
              {currentTarget?.sessions.map(s => (
                <option key={s} value={s}>{s}</option>
              ))}
            </select>
            <button 
              onClick={() => selectedSession && handleSubscribe(selectedSession)}
              className="flex items-center gap-2 bg-cyan-500 hover:bg-cyan-400 text-black font-bold px-4 py-2 rounded-md text-xs transition-all shadow-lg shadow-cyan-500/20 active:scale-95"
            >
              <Zap className="w-3 h-3 fill-black" />
              Listen Live
            </button>
          </div>
        </header>

        {/* Viewport */}
        <div className="flex-1 overflow-hidden p-6 flex flex-col gap-6">
          {selectedTarget && selectedSession ? (
            <>
              {/* Report Viewer */}
              <div className="flex-1 bg-black rounded-xl border border-white/5 overflow-hidden relative group">
                <div className="absolute top-4 right-4 z-10 flex gap-2 opacity-0 group-hover:opacity-100 transition-opacity">
                  <a 
                    href={getReportUrl(selectedTarget, selectedSession)} 
                    target="_blank" 
                    className="p-2 bg-black/80 border border-white/10 rounded-md hover:bg-white/10"
                  >
                    <Maximize2 className="w-4 h-4" />
                  </a>
                </div>
                <iframe 
                  src={getReportUrl(selectedTarget, selectedSession)} 
                  className="w-full h-full border-none"
                  title="Scan Report"
                />
              </div>

              {/* Console */}
              <div className="h-64 bg-[#0a0a0a] rounded-xl border border-white/5 flex flex-col overflow-hidden">
                <div className="px-4 py-3 border-b border-white/5 flex items-center justify-between bg-black/40">
                  <div className="flex items-center gap-2">
                    <Terminal className="w-4 h-4 text-cyan-400" />
                    <span className="text-xs font-bold text-zinc-400 uppercase tracking-widest">Live Output</span>
                  </div>
                  <div className="flex items-center gap-4 text-[10px] text-zinc-600 font-mono">
                    <span>Buffer: {logs.length}/500</span>
                    <button onClick={() => setLogs([])} className="hover:text-white transition-colors">Clear</button>
                  </div>
                </div>
                <div className="flex-1 overflow-y-auto p-4 font-mono text-xs leading-relaxed">
                  {logs.length > 0 ? (
                    logs.map((line, i) => (
                      <div key={i} className="flex gap-4 mb-1 group">
                        <span className="text-zinc-800 select-none w-8 text-right">{i + 1}</span>
                        <p className="text-zinc-300 break-all whitespace-pre-wrap">{line}</p>
                      </div>
                    ))
                  ) : (
                    <div className="h-full flex flex-col items-center justify-center text-zinc-700 opacity-50">
                      <Terminal className="w-8 h-8 mb-2" />
                      <p>Awaiting live connection...</p>
                    </div>
                  )}
                  <div ref={logEndRef} />
                </div>
              </div>
            </>
          ) : (
            <div className="flex-1 flex flex-col items-center justify-center gap-4 text-zinc-600">
              <div className="w-20 h-20 bg-white/5 rounded-full flex items-center justify-center border border-white/10 mb-2">
                <Search className="w-10 h-10 opacity-20" />
              </div>
              <h3 className="text-xl font-bold">No Data Available</h3>
              <p className="text-sm max-w-xs text-center leading-relaxed">Select a target from the sidebar or start a new scan to view the results.</p>
            </div>
          )}
        </div>
      </main>
    </div>
  );
}
