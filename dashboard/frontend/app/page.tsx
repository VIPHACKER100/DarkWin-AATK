"use client";

import { useState, useEffect, useRef, useCallback } from "react";
import {
  Activity, Terminal, Target, FileText, Zap, Shield, Clock,
  ChevronRight, Maximize2, RefreshCcw, Search, Play, Wifi,
  WifiOff, Loader2, AlertCircle, CheckCircle2, XCircle,
  ChevronDown, History, Layers, Trash2, Eye, EyeOff, CornerDownLeft
} from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";
import {
  getTargets, getReportUrl, getToolStatus, startScan,
  getCurrentScan, getScanHistory, deleteTarget, deleteSession, API_BASE
} from "@/lib/api";
import { socket } from "@/lib/socket";

interface SessionInfo { name: string; hasReport: boolean; modified: string; }
interface TargetData { target: string; sessions: SessionInfo[]; }
interface ScanProgress { scan_id: string | null; target: string | null; mode: string | null; status: string; phase: string | null; started_at: string | null; }
interface Toast { id: number; type: "success" | "error" | "info"; message: string; }

let toastId = 0;

export default function Dashboard() {
  const [targets, setTargets] = useState<TargetData[]>([]);
  const [selectedTarget, setSelectedTarget] = useState<string | null>(null);
  const [selectedSession, setSelectedSession] = useState<string | null>(null);
  const [logs, setLogs] = useState<string[]>([]);
  const [autoScroll, setAutoScroll] = useState(true);
  const [loading, setLoading] = useState(true);
  const [targetFilter, setTargetFilter] = useState("");
  const [socketStatus, setSocketStatus] = useState<"connected" | "disconnected" | "reconnecting">("disconnected");
  const [toolStatus, setToolStatus] = useState<Record<string, boolean> | null>(null);
  const [showTools, setShowTools] = useState(false);
  const [scanTarget, setScanTarget] = useState("");
  const [scanMode, setScanMode] = useState("recon");
  const [currentScan, setCurrentScan] = useState<ScanProgress>({ scan_id: null, target: null, mode: null, status: "idle", phase: null, started_at: null });
  const [scanHistory, setScanHistory] = useState<ScanProgress[]>([]);
  const [startError, setStartError] = useState("");
  const [toasts, setToasts] = useState<Toast[]>([]);
  const [confirmDelete, setConfirmDelete] = useState<string | null>(null);
  const logEndRef = useRef<HTMLDivElement>(null);
  const pollRef = useRef<ReturnType<typeof setInterval>>();
  const scanInputRef = useRef<HTMLInputElement>(null);

  const addToast = useCallback((type: Toast["type"], message: string) => {
    const id = ++toastId;
    setToasts(prev => [...prev, { id, type, message }]);
    setTimeout(() => setToasts(prev => prev.filter(t => t.id !== id)), 5000);
  }, []);

  const fetchData = useCallback(async () => {
    try {
      const data = await getTargets();
      setTargets(data);
      if (data.length > 0 && !selectedTarget) {
        setSelectedTarget(data[0].target);
        const s = data[0].sessions;
        if (s.length > 0) setSelectedSession(s[0].name);
      }
    } catch { /* ignore */ }
    finally { setLoading(false); }
  }, [selectedTarget]);

  useEffect(() => {
    fetchData();
    socket.connect();
    getScanHistory().then(setScanHistory).catch(() => {});
    socket.on("connect", () => setSocketStatus("connected"));
    socket.on("disconnect", () => setSocketStatus("disconnected"));
    socket.on("reconnecting", () => setSocketStatus("reconnecting"));
    socket.on("connect_error", () => setSocketStatus("disconnected"));
    socket.on("scan_update", (data: { scan_id: string; line: string }) => {
      setLogs(prev => [...prev.slice(-499), data.line]);
    });
    socket.on("scan_phase", (data: { phase: string }) => {
      setCurrentScan(prev => ({ ...prev, phase: data.phase }));
    });
    socket.on("scan_done", () => {
      setCurrentScan(prev => ({ ...prev, status: "completed", phase: "done" }));
      addToast("success", "Scan completed");
      fetchData();
    });
    socket.on("scan_error", (data: { error: string }) => {
      setCurrentScan(prev => ({ ...prev, status: "failed", phase: data.error }));
      addToast("error", `Scan failed: ${data.error}`);
    });
    socket.on("target_deleted", fetchData);
    socket.on("session_deleted", fetchData);
    return () => { socket.disconnect(); };
  }, [fetchData, addToast]);

  useEffect(() => {
    if (autoScroll) logEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [logs, autoScroll]);

  useEffect(() => {
    if (socketStatus === "connected") {
      pollRef.current = setInterval(async () => {
        try { setCurrentScan(await getCurrentScan()); }
        catch { /* ignore */ }
      }, 3000);
      return () => clearInterval(pollRef.current);
    }
  }, [socketStatus]);

  useEffect(() => {
    const handler = (e: KeyboardEvent) => {
      if (e.key === "Enter" && e.target === scanInputRef.current) handleStartScan();
      if (e.key === "Escape") setLogs([]);
    };
    window.addEventListener("keydown", handler);
    return () => window.removeEventListener("keydown", handler);
  });

  const handleSubscribe = (session: string) => {
    if (!selectedTarget) return;
    setLogs([]);
    socket.emit("subscribe", { scan_id: `${selectedTarget}/${session}` });
  };

  const handleStartScan = async () => {
    if (!scanTarget.trim() || currentScan.status === "running") return;
    setStartError("");
    setLogs([]);
    try {
      const result = await startScan(scanTarget.trim(), scanMode);
      setCurrentScan({ scan_id: result.scan_id, target: result.target, mode: result.mode, status: "running", phase: "queued", started_at: new Date().toISOString() });
      socket.emit("subscribe", { scan_id: result.scan_id });
    } catch (err: any) {
      setStartError(err?.response?.data?.error || err?.message || "Failed to start scan");
    }
  };

  const handleRefreshTools = async () => {
    setToolStatus(null);
    try { setToolStatus(await getToolStatus()); }
    catch { setToolStatus({}); }
  };

  const handleDeleteTarget = async (target: string) => {
    try {
      await deleteTarget(target);
      addToast("info", `Deleted target: ${target}`);
      if (selectedTarget === target) { setSelectedTarget(null); setSelectedSession(null); }
      setConfirmDelete(null);
    } catch { addToast("error", `Failed to delete ${target}`); }
  };

  const handleDeleteSession = async (target: string, session: string) => {
    try {
      await deleteSession(target, session);
      addToast("info", `Deleted session: ${session}`);
      if (selectedTarget === target && selectedSession === session) setSelectedSession(null);
      setConfirmDelete(null);
    } catch { addToast("error", `Failed to delete ${session}`); }
  };

  const filteredTargets = targets.filter(t =>
    t.target.toLowerCase().includes(targetFilter.toLowerCase())
  );
  const currentTarget = targets.find(t => t.target === selectedTarget);
  const missingCount = toolStatus ? Object.values(toolStatus).filter(v => !v).length : 0;
  const totalTools = toolStatus ? Object.keys(toolStatus).length : 0;
  const modeColors: Record<string, string> = { recon: "text-cyan-400 bg-cyan-500/10 border-cyan-500/20", scan: "text-amber-400 bg-amber-500/10 border-amber-500/20", bounty: "text-rose-400 bg-rose-500/10 border-rose-500/20" };

  return (
    <div className="flex h-screen w-full bg-[#050505] text-white font-sans selection:bg-cyan-500/30" onKeyDownCapture={() => {}}>
      {/* ── Toasts ── */}
      <div className="fixed top-4 right-4 z-50 flex flex-col gap-2 max-w-sm">
        <AnimatePresence>
          {toasts.map(t => (
            <motion.div key={t.id} initial={{ opacity: 0, x: 100 }} animate={{ opacity: 1, x: 0 }} exit={{ opacity: 0, x: 100 }}
              className={`px-4 py-3 rounded-lg shadow-2xl border text-sm font-mono flex items-center gap-3 ${
                t.type === "success" ? "bg-emerald-900/90 border-emerald-700 text-emerald-200" :
                t.type === "error" ? "bg-red-900/90 border-red-700 text-red-200" :
                "bg-zinc-800/90 border-zinc-700 text-zinc-200"}`}>
              {t.type === "success" ? <CheckCircle2 className="w-4 h-4 text-emerald-400" /> :
               t.type === "error" ? <AlertCircle className="w-4 h-4 text-red-400" /> :
               <Activity className="w-4 h-4 text-zinc-400" />}
              {t.message}
            </motion.div>
          ))}
        </AnimatePresence>
      </div>

      {/* ── Sidebar ── */}
      <aside className="w-72 lg:w-80 border-r border-white/5 flex flex-col bg-[#0a0a0a] flex-shrink-0">
        <div className="p-4 lg:p-6 border-b border-white/5 flex items-center gap-3">
          <div className="w-9 h-9 lg:w-10 lg:h-10 bg-cyan-500/10 rounded-lg flex items-center justify-center border border-cyan-500/20">
            <Shield className="w-5 h-5 lg:w-6 lg:h-6 text-cyan-400" />
          </div>
          <div className="min-w-0">
            <h1 className="font-bold tracking-tight text-base lg:text-lg leading-tight">DARKWIN</h1>
            <p className="text-[10px] text-zinc-500 uppercase tracking-[0.2em] truncate">Control Center v1.1.0</p>
          </div>
        </div>

        <div className="px-4 pt-4 pb-2">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-3.5 h-3.5 text-zinc-600" />
            <input value={targetFilter} onChange={e => setTargetFilter(e.target.value)}
              placeholder="Filter targets..." className="w-full bg-white/5 border border-white/10 rounded-lg pl-9 pr-3 py-2 text-xs font-mono outline-none focus:border-cyan-500/50 transition-colors placeholder:text-zinc-700" />
          </div>
        </div>

        <div className="flex-1 overflow-y-auto p-4 space-y-1">
          <div className="flex items-center justify-between px-2 mb-2">
            <span className="text-[11px] font-bold text-zinc-500 uppercase tracking-wider">Targets {filteredTargets.length > 0 && <span className="text-zinc-700">({filteredTargets.length})</span>}</span>
            <button onClick={fetchData} className="p-1 hover:bg-white/5 rounded transition-colors">
              <RefreshCcw className="w-3 h-3 text-zinc-500" />
            </button>
          </div>
          {filteredTargets.length === 0 && !loading && (
            <p className="text-xs text-zinc-700 text-center py-8">No targets found</p>
          )}
          {filteredTargets.map(t => (
            <div key={t.target} className="group relative">
              <button onClick={() => { setSelectedTarget(t.target); setSelectedSession(t.sessions[0]?.name || null); }}
                className={`w-full text-left p-3 rounded-lg flex items-center justify-between transition-all ${
                  selectedTarget === t.target ? "bg-cyan-500/10 border border-cyan-500/20" : "hover:bg-white/5 border border-transparent"}`}>
                <div className="flex items-center gap-3 min-w-0">
                  <Target className={`w-4 h-4 flex-shrink-0 ${selectedTarget === t.target ? "text-cyan-400" : "text-zinc-500"}`} />
                  <span className={`text-sm font-medium truncate ${selectedTarget === t.target ? "text-white" : "text-zinc-400"}`}>{t.target}</span>
                </div>
                <div className="flex items-center gap-2 flex-shrink-0">
                  <span className="text-[10px] text-zinc-700">{t.sessions.length}</span>
                  <ChevronRight className={`w-4 h-4 transition-transform ${selectedTarget === t.target ? "translate-x-0 text-cyan-400" : "translate-x-2 opacity-0 group-hover:translate-x-0 group-hover:opacity-100 text-zinc-600"}`} />
                </div>
              </button>
              <button onClick={() => setConfirmDelete(`target:${t.target}`)}
                className="absolute right-2 top-1/2 -translate-y-1/2 p-1.5 opacity-0 group-hover:opacity-100 hover:bg-red-500/20 rounded transition-all">
                <Trash2 className="w-3 h-3 text-red-500" />
              </button>
            </div>
          ))}
          {loading && Array.from({ length: 3 }).map((_, i) => (
            <div key={i} className="p-3 rounded-lg animate-pulse"><div className="h-4 bg-white/5 rounded w-3/4" /></div>
          ))}
        </div>

        <div className="p-4 border-t border-white/5 bg-black/20 space-y-2">
          <button onClick={() => { setShowTools(!showTools); if (!toolStatus) handleRefreshTools(); }}
            className="w-full flex items-center justify-between p-2.5 hover:bg-white/5 rounded-lg transition-colors group">
            <div className="flex items-center gap-2.5">
              <Layers className="w-4 h-4 text-zinc-500 group-hover:text-zinc-300" />
              <span className="text-xs text-zinc-400 group-hover:text-zinc-200">Tool Status</span>
            </div>
            {toolStatus && (
              <div className="flex items-center gap-2">
                <span className={`text-[10px] font-mono ${missingCount === 0 ? "text-emerald-500" : "text-red-400"}`}>{totalTools - missingCount}/{totalTools}</span>
                <ChevronDown className={`w-3.5 h-3.5 text-zinc-600 transition-transform ${showTools ? "rotate-180" : ""}`} />
              </div>
            )}
          </button>
          <AnimatePresence>
            {showTools && toolStatus && (
              <motion.div initial={{ height: 0, opacity: 0 }} animate={{ height: "auto", opacity: 1 }} exit={{ height: 0, opacity: 0 }} className="overflow-hidden">
                <div className="max-h-48 overflow-y-auto space-y-1 pl-2 pr-1">
                  {Object.entries(toolStatus).map(([name, ok]) => (
                    <div key={name} className="flex items-center justify-between py-1">
                      <span className="text-[11px] font-mono text-zinc-500 truncate">{name}</span>
                      {ok ? <CheckCircle2 className="w-3 h-3 text-emerald-500 flex-shrink-0" /> : <XCircle className="w-3 h-3 text-red-500 flex-shrink-0" />}
                    </div>
                  ))}
                </div>
                <button onClick={handleRefreshTools} className="w-full mt-2 py-1.5 text-[10px] text-zinc-600 hover:text-zinc-400 font-mono">↻ refresh</button>
              </motion.div>
            )}
          </AnimatePresence>
          <div className="flex items-center justify-between p-2.5 bg-white/5 rounded-lg">
            <div className="flex items-center gap-2.5">
              {socketStatus === "connected" ? <Wifi className="w-3.5 h-3.5 text-emerald-500" /> :
               socketStatus === "reconnecting" ? <Loader2 className="w-3.5 h-3.5 text-amber-500 animate-spin" /> :
               <WifiOff className="w-3.5 h-3.5 text-red-500" />}
              <span className="text-xs font-mono text-zinc-400">
                {socketStatus === "connected" ? "Online" : socketStatus === "reconnecting" ? "Reconnecting" : "Offline"}
              </span>
            </div>
            <div className={`w-2 h-2 rounded-full ${socketStatus === "connected" ? "bg-emerald-500 animate-pulse" :
              socketStatus === "reconnecting" ? "bg-amber-500 animate-pulse" : "bg-red-500"}`} />
          </div>
        </div>
      </aside>

      {/* ── Main ── */}
      <main className="flex-1 flex flex-col relative overflow-hidden">
        <header className="h-20 border-b border-white/5 flex items-center justify-between px-6 lg:px-8 bg-black/40 backdrop-blur-md z-10">
          <div>
            <h2 className="text-xs font-bold text-zinc-500 uppercase tracking-widest mb-0.5">Active Session</h2>
            <div className="flex items-center gap-2">
              <p className="text-lg font-bold tracking-tight truncate max-w-[200px] lg:max-w-xs">{selectedTarget || "No Target"}</p>
              {selectedSession && <><ChevronRight className="w-4 h-4 text-zinc-700 flex-shrink-0" /><span className="text-zinc-400 font-mono text-sm truncate max-w-[150px]">{selectedSession}</span></>}
            </div>
          </div>
          <div className="flex items-center gap-3">
            {currentTarget && currentTarget.sessions.length > 0 && (
              <>
                <select value={selectedSession || ""} onChange={e => setSelectedSession(e.target.value)}
                  className="bg-white/5 border border-white/10 rounded-md px-3 py-1.5 text-xs font-mono outline-none focus:border-cyan-500/50 transition-colors">
                  {currentTarget.sessions.map(s => <option key={s.name} value={s.name}>{s.name}</option>)}
                </select>
                <button onClick={() => selectedSession && handleSubscribe(selectedSession)}
                  className="flex items-center gap-2 bg-cyan-500 hover:bg-cyan-400 text-black font-bold px-4 py-1.5 rounded-md text-xs transition-all shadow-lg shadow-cyan-500/20 active:scale-95">
                  <Zap className="w-3 h-3 fill-black" /> Listen
                </button>
                {selectedSession && (
                  <button onClick={() => setConfirmDelete(`session:${selectedTarget}/${selectedSession}`)}
                    className="p-2 hover:bg-red-500/20 rounded-lg transition-colors text-zinc-500 hover:text-red-400">
                    <Trash2 className="w-4 h-4" />
                  </button>
                )}
              </>
            )}
          </div>
        </header>

        <div className="flex-1 overflow-y-auto p-6 flex flex-col gap-5">
          {/* ── Scan Panel ── */}
          <motion.div initial={{ opacity: 0, y: -10 }} animate={{ opacity: 1, y: 0 }} className="bg-black/60 rounded-xl border border-white/5 p-5">
            <div className="flex items-center gap-3 mb-4">
              <Play className="w-5 h-5 text-cyan-400" />
              <h3 className="text-sm font-bold text-zinc-300 uppercase tracking-wider">New Scan</h3>
              <span className="text-[10px] text-zinc-700 font-mono ml-auto">Enter ↵ to launch</span>
            </div>
            <div className="flex flex-col sm:flex-row gap-3">
              <div className="flex-1 relative">
                <input ref={scanInputRef} value={scanTarget} onChange={e => setScanTarget(e.target.value)} placeholder="target.com"
                  className="w-full bg-white/5 border border-white/10 rounded-lg px-4 py-2.5 pr-8 text-sm font-mono outline-none focus:border-cyan-500/50 transition-colors placeholder:text-zinc-700"
                  disabled={currentScan.status === "running"} />
                <CornerDownLeft className="absolute right-3 top-1/2 -translate-y-1/2 w-3.5 h-3.5 text-zinc-700 pointer-events-none" />
              </div>
              <div className="flex gap-2">
                {["recon", "scan", "bounty"].map(m => (
                  <button key={m} onClick={() => setScanMode(m)}
                    className={`px-4 py-2.5 rounded-lg text-xs font-bold uppercase tracking-wider border transition-all ${
                      scanMode === m ? modeColors[m] : "text-zinc-600 border-white/10 hover:border-white/20 hover:text-zinc-400"}`}>
                    {m}
                  </button>
                ))}
              </div>
              <button onClick={handleStartScan} disabled={currentScan.status === "running" || !scanTarget.trim()}
                className="flex items-center gap-2 bg-cyan-500 hover:bg-cyan-400 disabled:bg-zinc-800 disabled:text-zinc-600 text-black font-bold px-6 py-2.5 rounded-lg text-xs transition-all shadow-lg shadow-cyan-500/20 active:scale-95 whitespace-nowrap">
                {currentScan.status === "running" ? <Loader2 className="w-4 h-4 animate-spin" /> : <Play className="w-4 h-4 fill-black" />}
                {currentScan.status === "running" ? "Running..." : "Launch"}
              </button>
            </div>
            {startError && <p className="mt-3 text-xs text-red-400 font-mono flex items-center gap-1.5"><AlertCircle className="w-3.5 h-3.5" />{startError}</p>}
          </motion.div>

          {/* ── Progress ── */}
          {currentScan.status === "running" && (
            <motion.div initial={{ opacity: 0, height: 0 }} animate={{ opacity: 1, height: "auto" }} className="bg-black/60 rounded-xl border border-cyan-500/20 p-5">
              <div className="flex items-center justify-between mb-3">
                <div className="flex items-center gap-2">
                  <Loader2 className="w-4 h-4 text-cyan-400 animate-spin" />
                  <span className="text-sm font-bold text-cyan-400">{currentScan.mode?.toUpperCase()} scan on {currentScan.target}</span>
                </div>
                <span className="text-[10px] text-zinc-600 font-mono">{currentScan.phase}</span>
              </div>
              <div className="w-full bg-white/5 rounded-full h-1.5 overflow-hidden">
                <motion.div className="h-full bg-gradient-to-r from-cyan-500 to-emerald-500 rounded-full"
                  initial={{ width: "5%" }} animate={{ width: currentScan.phase === "done" ? "100%" : "60%" }}
                  transition={{ duration: 0.5 }} />
              </div>
              <p className="mt-2 text-[11px] text-zinc-600 font-mono">Phase: {currentScan.phase || "starting..."}</p>
            </motion.div>
          )}

          {/* ── Failed Scan ── */}
          {currentScan.status === "failed" && (
            <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="bg-red-900/20 rounded-xl border border-red-500/20 p-4 flex items-center gap-3">
              <AlertCircle className="w-5 h-5 text-red-400 flex-shrink-0" />
              <div>
                <p className="text-sm font-bold text-red-300">Scan Failed</p>
                <p className="text-xs font-mono text-red-400 mt-0.5">{currentScan.phase}</p>
              </div>
            </motion.div>
          )}

          {/* ── Scan History ── */}
          {scanHistory.length > 0 && (
            <details className="group">
              <summary className="flex items-center gap-2 text-xs text-zinc-600 hover:text-zinc-400 cursor-pointer list-none">
                <History className="w-3.5 h-3.5" /> Scan History ({scanHistory.length})
              </summary>
              <div className="mt-2 space-y-1">
                {scanHistory.slice(0, 10).map(s => (
                  <div key={s.scan_id} className="flex items-center gap-3 text-[11px] font-mono text-zinc-600 p-2 bg-white/5 rounded-lg">
                    <span className="text-zinc-500 w-16 flex-shrink-0">{s.started_at ? new Date(s.started_at).toLocaleTimeString() : "?"}</span>
                    <span className={`${modeColors[s.mode || "recon"]?.split(" ")[0] || "text-zinc-400"} w-12`}>{s.mode?.toUpperCase()}</span>
                    <span className="text-zinc-400 truncate">{s.target}</span>
                    <span className={`ml-auto ${s.status === "completed" ? "text-emerald-500" : s.status === "failed" ? "text-red-500" : "text-amber-500"}`}>{s.status}</span>
                  </div>
                ))}
              </div>
            </details>
          )}

          {/* ── Content Area ── */}
          {selectedTarget && selectedSession && currentTarget ? (
            (() => {
              const sessionInfo = currentTarget.sessions.find(s => s.name === selectedSession);
              return (
                <>
                  {sessionInfo?.hasReport ? (
                    <div className="flex-1 bg-black rounded-xl border border-white/5 overflow-hidden relative group min-h-[350px]">
                      <div className="absolute top-4 right-4 z-10 flex gap-2 opacity-0 group-hover:opacity-100 transition-opacity">
                        <a href={getReportUrl(selectedTarget, selectedSession)} target="_blank"
                          className="p-2 bg-black/80 border border-white/10 rounded-md hover:bg-white/10">
                          <Maximize2 className="w-4 h-4" />
                        </a>
                      </div>
                      <iframe src={getReportUrl(selectedTarget, selectedSession)} className="w-full h-full border-none" title="Scan Report" />
                    </div>
                  ) : (
                    <div className="flex-1 bg-black rounded-xl border border-white/5 flex flex-col items-center justify-center gap-3 min-h-[200px] text-zinc-600">
                      <FileText className="w-8 h-8 opacity-30" />
                      <p className="text-sm font-mono">No report generated for this session</p>
                    </div>
                  )}

                  {/* ── Terminal ── */}
                  <div className="h-56 bg-[#0a0a0a] rounded-xl border border-white/5 flex flex-col overflow-hidden">
                    <div className="px-4 py-3 border-b border-white/5 flex items-center justify-between bg-black/40">
                      <div className="flex items-center gap-2">
                        <Terminal className="w-4 h-4 text-cyan-400" />
                        <span className="text-xs font-bold text-zinc-400 uppercase tracking-widest">Live Output</span>
                      </div>
                      <div className="flex items-center gap-4 text-[10px] text-zinc-600 font-mono">
                        <button onClick={() => setAutoScroll(!autoScroll)}
                          className={`flex items-center gap-1.5 hover:text-white transition-colors ${autoScroll ? "" : "text-zinc-500"}`}>
                          {autoScroll ? <Eye className="w-3 h-3" /> : <EyeOff className="w-3 h-3" />}
                          {autoScroll ? "Auto" : "Paused"}
                        </button>
                        <span>Buffer: {logs.length}/500</span>
                        <button onClick={() => setLogs([])} className="hover:text-white transition-colors">Clear</button>
                      </div>
                    </div>
                    <div className="flex-1 overflow-y-auto p-4 font-mono text-xs leading-relaxed">
                      {logs.length > 0 ? logs.map((line, i) => (
                        <div key={i} className="flex gap-4 mb-1 group">
                          <span className="text-zinc-800 select-none w-8 text-right flex-shrink-0">{i + 1}</span>
                          <p className="text-zinc-300 break-all whitespace-pre-wrap">{line}</p>
                        </div>
                      )) : (
                        <div className="h-full flex flex-col items-center justify-center text-zinc-700 opacity-50">
                          <Terminal className="w-8 h-8 mb-2" />
                          <p>Awaiting live connection...</p>
                          <p className="text-[10px] mt-1">Press Listen or start a scan</p>
                        </div>
                      )}
                      <div ref={logEndRef} />
                    </div>
                  </div>
                </>
              );
            })()
          ) : (
            <div className="flex-1 flex flex-col items-center justify-center gap-4 text-zinc-600 min-h-[300px]">
              <div className="w-20 h-20 bg-white/5 rounded-full flex items-center justify-center border border-white/10 mb-2">
                <Search className="w-10 h-10 opacity-20" />
              </div>
              <h3 className="text-xl font-bold">No Data Available</h3>
              <p className="text-sm max-w-xs text-center leading-relaxed">Enter a target above and launch a scan, or select an existing target from the sidebar.</p>
            </div>
          )}
        </div>
      </main>

      {/* ── Confirm Delete Modal ── */}
      <AnimatePresence>
        {confirmDelete && (
          <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}
            className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 backdrop-blur-sm">
            <motion.div initial={{ scale: 0.9 }} animate={{ scale: 1 }} exit={{ scale: 0.9 }}
              className="bg-zinc-900 border border-zinc-800 rounded-xl p-6 max-w-sm w-full mx-4 shadow-2xl">
              <div className="flex items-center gap-3 mb-4">
                <AlertCircle className="w-6 h-6 text-red-400" />
                <h3 className="text-lg font-bold">Confirm Deletion</h3>
              </div>
              <p className="text-sm text-zinc-400 mb-6">
                {confirmDelete.startsWith("target:") ? `Delete all sessions for "${confirmDelete.slice(7)}"? This cannot be undone.` :
                 `Delete session "${confirmDelete.split("/")[1]}" for "${confirmDelete.split("/")[0].slice(8)}"?`}
              </p>
              <div className="flex gap-3 justify-end">
                <button onClick={() => setConfirmDelete(null)}
                  className="px-4 py-2 rounded-lg text-xs font-bold border border-zinc-700 text-zinc-400 hover:bg-zinc-800 transition-colors">Cancel</button>
                <button onClick={() => confirmDelete.startsWith("target:") ? handleDeleteTarget(confirmDelete.slice(7)) : handleDeleteSession(...confirmDelete.slice(8).split("/") as [string, string])}
                  className="px-4 py-2 rounded-lg text-xs font-bold bg-red-600 hover:bg-red-500 text-white transition-colors">Delete</button>
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
