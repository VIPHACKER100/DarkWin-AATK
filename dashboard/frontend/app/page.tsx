"use client";

import { useState, useEffect, useRef, useCallback } from "react";
import {
  Activity, Terminal, Target, FileText, Zap, Shield, Clock,
  ChevronRight, Maximize2, RefreshCcw, Search, Play, Wifi,
  WifiOff, Loader2, AlertCircle, CheckCircle2, XCircle,
  ChevronDown, History, Layers, Trash2, Eye, EyeOff, CornerDownLeft,
  Radio, Globe, Server, Cpu
} from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";
import {
  getTargets, getReportUrl, getToolStatus, startScan,
  getCurrentScan, getScanHistory, deleteTarget, deleteSession
} from "@/lib/api";
import { socket } from "@/lib/socket";
import { cn } from "@/lib/utils";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { AnimatedSection, StaggerContainer, StaggerItem } from "@/components/animated-section";

interface SessionInfo { name: string; hasReport: boolean; modified: string; }
interface TargetData { target: string; sessions: SessionInfo[]; }
interface ScanProgress { scan_id: string | null; target: string | null; mode: string | null; status: string; phase: string | null; started_at: string | null; }
interface Toast { id: number; type: "success" | "error" | "info"; message: string; }

let toastId = 0;

function GradientText({ children, className }: { children: React.ReactNode; className?: string }) {
  return (
    <span className={cn("gradient-text", className)}>
      {children}
    </span>
  );
}

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
  const pollRef = useRef<ReturnType<typeof setInterval> | null>(null);
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
    // eslint-disable-next-line
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
      return () => { if (pollRef.current) clearInterval(pollRef.current); };
    }
  }, [socketStatus]);

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
    } catch (err: unknown) {
      const error = err as { response?: { data?: { error?: string } }, message?: string };
      setStartError(error?.response?.data?.error || error?.message || "Failed to start scan");
    }
  };

  useEffect(() => {
    const handler = (e: KeyboardEvent) => {
      if (e.key === "Enter" && e.target === scanInputRef.current) handleStartScan();
      if (e.key === "Escape") setLogs([]);
    };
    window.addEventListener("keydown", handler);
    return () => window.removeEventListener("keydown", handler);
  });

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

  const modeConfig: Record<string, { label: string; color: string; icon: typeof Globe }> = {
    recon: { label: "Recon", color: "from-cyan-500 to-blue-500", icon: Globe },
    scan: { label: "Scan", color: "from-amber-500 to-orange-500", icon: Server },
    bounty: { label: "Bounty", color: "from-rose-500 to-pink-500", icon: Cpu },
  };

  return (
    <div className="flex h-screen w-full bg-[var(--background)] text-[var(--foreground)] selection:bg-[var(--accent)]/30">
      {/* ── Toasts ── */}
      <div className="fixed top-4 right-4 z-50 flex flex-col gap-2 max-w-sm">
        <AnimatePresence>
          {toasts.map(t => (
            <motion.div
              key={t.id}
              initial={{ opacity: 0, x: 100 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: 100 }}
              transition={{ duration: 0.3, ease: [0.16, 1, 0.3, 1] }}
              className={cn(
                "px-5 py-3 rounded-xl shadow-lg border text-sm font-medium flex items-center gap-3 backdrop-blur-md",
                t.type === "success" && "bg-emerald-900/80 border-emerald-700/50 text-emerald-200",
                t.type === "error" && "bg-red-900/80 border-red-700/50 text-red-200",
                t.type === "info" && "bg-zinc-800/80 border-zinc-700/50 text-zinc-200"
              )}
            >
              {t.type === "success" ? <CheckCircle2 className="w-4 h-4 text-emerald-400" /> :
               t.type === "error" ? <AlertCircle className="w-4 h-4 text-red-400" /> :
               <Activity className="w-4 h-4 text-zinc-400" />}
              {t.message}
            </motion.div>
          ))}
        </AnimatePresence>
      </div>

      {/* ── Sidebar ── */}
      <aside className="w-72 lg:w-80 border-r border-[var(--border)] flex flex-col bg-[var(--card)] flex-shrink-0 relative">
        <div className="absolute inset-0 pointer-events-none" style={{ backgroundImage: "radial-gradient(circle, rgba(0,82,255,0.03) 1px, transparent 1px)", backgroundSize: "32px 32px" }} />
        <div className="relative z-10 p-5 lg:p-6 border-b border-[var(--border)] flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-[var(--accent)] to-[var(--accent-secondary)] flex items-center justify-center shadow-[0_4px_14px_rgba(0,82,255,0.25)]">
            <Shield className="w-5 h-5 text-white" />
          </div>
          <div className="min-w-0">
            <h1 className="font-display text-lg leading-tight">DARKWIN</h1>
            <p className="text-[10px] text-[var(--muted-foreground)] uppercase tracking-[0.15em] font-mono-label truncate">Control Center</p>
          </div>
        </div>

        <div className="relative z-10 px-4 pt-4 pb-2">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-3.5 h-3.5 text-[var(--muted-foreground)]/50" />
            <input
              value={targetFilter}
              onChange={e => setTargetFilter(e.target.value)}
              placeholder="Filter targets..."
              className="w-full h-10 rounded-lg border border-[var(--border)] bg-transparent pl-9 pr-3 text-xs font-mono text-[var(--foreground)] placeholder:text-[var(--muted-foreground)]/40 outline-none transition-colors focus:border-[var(--accent)]/50"
            />
          </div>
        </div>

        <div className="relative z-10 flex-1 overflow-y-auto p-4 space-y-0.5">
          <div className="flex items-center justify-between px-2 mb-3">
            <span className="font-mono-label text-[10px] uppercase tracking-[0.15em] text-[var(--muted-foreground)]">
              Targets
              {filteredTargets.length > 0 && <span className="text-[var(--muted-foreground)]/50 ml-1">({filteredTargets.length})</span>}
            </span>
            <button onClick={fetchData} className="p-1 hover:bg-[var(--muted)] rounded transition-colors">
              <RefreshCcw className="w-3 h-3 text-[var(--muted-foreground)]/60" />
            </button>
          </div>
          {filteredTargets.length === 0 && !loading && (
            <p className="text-xs text-[var(--muted-foreground)]/50 text-center py-8 font-mono">No targets found</p>
          )}
          <StaggerContainer>
            {filteredTargets.map(t => (
              <StaggerItem key={t.target}>
                <div className="group relative">
                  <button
                    onClick={() => { setSelectedTarget(t.target); setSelectedSession(t.sessions[0]?.name || null); }}
                    className={cn(
                      "w-full text-left p-2.5 rounded-xl flex items-center justify-between transition-all duration-200",
                      selectedTarget === t.target
                        ? "bg-gradient-to-r from-[var(--accent)]/10 to-transparent border border-[var(--accent)]/20 shadow-sm"
                        : "hover:bg-[var(--muted)] border border-transparent"
                    )}
                  >
                    <div className="flex items-center gap-3 min-w-0">
                      <div className={cn(
                        "w-7 h-7 rounded-lg flex items-center justify-center transition-all duration-300",
                        selectedTarget === t.target ? "bg-gradient-to-br from-[var(--accent)] to-[var(--accent-secondary)] group-hover:scale-110" : "bg-[var(--muted)] group-hover:scale-105"
                      )}>
                        <Target className={cn("w-3.5 h-3.5 transition-transform duration-300", selectedTarget === t.target ? "text-white" : "text-[var(--muted-foreground)]")} />
                      </div>
                      <span className={cn("text-sm truncate", selectedTarget === t.target ? "font-medium text-white" : "text-[var(--muted-foreground)]")}>
                        {t.target}
                      </span>
                    </div>
                    <div className="flex items-center gap-1.5 flex-shrink-0">
                      <span className="font-mono-label text-[10px] text-[var(--muted-foreground)]/50">{t.sessions.length}</span>
                      <ChevronRight className={cn(
                        "w-3.5 h-3.5 transition-all duration-300",
                        selectedTarget === t.target ? "translate-x-0 text-[var(--accent)]" : "-translate-x-1 opacity-0 group-hover:translate-x-0 group-hover:opacity-100 text-[var(--muted-foreground)]/40"
                      )} />
                    </div>
                  </button>
                  <button
                    onClick={() => setConfirmDelete(`target:${t.target}`)}
                    className="absolute right-2 top-1/2 -translate-y-1/2 p-1.5 opacity-0 group-hover:opacity-100 hover:bg-red-500/20 rounded-lg transition-all"
                  >
                    <Trash2 className="w-3 h-3 text-red-500/70" />
                  </button>
                </div>
              </StaggerItem>
            ))}
          </StaggerContainer>
          {loading && Array.from({ length: 3 }).map((_, i) => (
            <div key={i} className="p-2.5 rounded-xl animate-pulse"><div className="h-4 bg-[var(--muted)] rounded w-3/4" /></div>
          ))}
        </div>

        <div className="relative z-10 p-4 border-t border-[var(--border)] bg-[var(--muted)]/50 space-y-2">
          <button
            onClick={() => { setShowTools(!showTools); if (!toolStatus) handleRefreshTools(); }}
            className="w-full flex items-center justify-between p-2.5 hover:bg-[var(--muted)] rounded-xl transition-colors group"
          >
            <div className="flex items-center gap-2.5">
              <Layers className="w-4 h-4 text-[var(--muted-foreground)]/50 group-hover:text-[var(--muted-foreground)]" />
              <span className="text-xs font-medium text-[var(--muted-foreground)]/70 group-hover:text-[var(--muted-foreground)]">Tool Status</span>
            </div>
            {toolStatus && (
              <div className="flex items-center gap-2">
                <span className={cn("font-mono-label text-[10px]", missingCount === 0 ? "text-emerald-500" : "text-red-400")}>
                  {totalTools - missingCount}/{totalTools}
                </span>
                <ChevronDown className={cn("w-3 h-3 text-[var(--muted-foreground)]/40 transition-transform", showTools && "rotate-180")} />
              </div>
            )}
          </button>
          <AnimatePresence>
            {showTools && toolStatus && (
              <motion.div
                initial={{ height: 0, opacity: 0 }}
                animate={{ height: "auto", opacity: 1 }}
                exit={{ height: 0, opacity: 0 }}
                className="overflow-hidden"
              >
                <div className="max-h-40 overflow-y-auto space-y-0.5 pl-2 pr-1">
                  {Object.entries(toolStatus).map(([name, ok]) => (
                    <div key={name} className="flex items-center justify-between py-1">
                      <span className="font-mono-label text-[11px] text-[var(--muted-foreground)]/60 truncate">{name}</span>
                      {ok ? <CheckCircle2 className="w-3 h-3 text-emerald-500/70 flex-shrink-0" /> : <XCircle className="w-3 h-3 text-red-500/70 flex-shrink-0" />}
                    </div>
                  ))}
                </div>
                <button onClick={handleRefreshTools} className="w-full mt-2 py-1.5 font-mono-label text-[10px] text-[var(--muted-foreground)]/50 hover:text-[var(--muted-foreground)] transition-colors">
                  ↻ refresh
                </button>
              </motion.div>
            )}
          </AnimatePresence>
          <div className="flex items-center justify-between p-2.5 rounded-xl bg-[var(--muted)]/50">
            <div className="flex items-center gap-2.5">
              {socketStatus === "connected" ? <Wifi className="w-3.5 h-3.5 text-emerald-500" /> :
               socketStatus === "reconnecting" ? <Loader2 className="w-3.5 h-3.5 text-amber-500 animate-spin" /> :
               <WifiOff className="w-3.5 h-3.5 text-red-500" />}
              <span className="font-mono-label text-xs text-[var(--muted-foreground)]">
                {socketStatus === "connected" ? "Online" : socketStatus === "reconnecting" ? "Reconnecting" : "Offline"}
              </span>
            </div>
            <div className={cn(
              "w-2 h-2 rounded-full",
              socketStatus === "connected" ? "bg-emerald-500 animate-pulse shadow-[0_0_6px_rgba(16,185,129,0.5)]" :
              socketStatus === "reconnecting" ? "bg-amber-500 animate-pulse" : "bg-red-500"
            )} />
          </div>
        </div>
      </aside>

      {/* ── Main ── */}
      <main className="flex-1 flex flex-col relative overflow-hidden">
        <div className="absolute top-0 right-0 w-96 h-96 bg-[var(--accent)]/5 rounded-full blur-[150px] pointer-events-none" />
        <div className="absolute bottom-0 left-1/4 w-64 h-64 bg-[var(--accent-secondary)]/5 rounded-full blur-[150px] pointer-events-none" />

        <header className="relative z-10 h-[72px] border-b border-[var(--border)] flex items-center justify-between px-6 lg:px-8 bg-[var(--background)]/80 backdrop-blur-md">
          <div>
            <p className="font-mono-label text-[10px] uppercase tracking-[0.15em] text-[var(--muted-foreground)]/60 mb-0.5">Active Session</p>
            <div className="flex items-center gap-2">
              <p className="font-display text-xl tracking-tight truncate max-w-[200px] lg:max-w-xs">
                {selectedTarget || <span className="text-[var(--muted-foreground)]/40">No Target</span>}
              </p>
              {selectedSession && (
                <>
                  <ChevronRight className="w-4 h-4 text-[var(--muted-foreground)]/30 flex-shrink-0" />
                  <span className="font-mono-label text-sm text-[var(--muted-foreground)]/60 truncate max-w-[150px]">{selectedSession}</span>
                </>
              )}
            </div>
          </div>
          <div className="flex items-center gap-3">
            {currentTarget && currentTarget.sessions.length > 0 && (
              <>
                <select
                  value={selectedSession || ""}
                  onChange={e => setSelectedSession(e.target.value)}
                  className="h-10 rounded-xl border border-[var(--border)] bg-transparent px-3 text-xs font-mono text-[var(--foreground)] outline-none focus:border-[var(--accent)]/50 transition-colors"
                >
                  {currentTarget.sessions.map(s => <option key={s.name} value={s.name}>{s.name}</option>)}
                </select>
                <Button size="sm" onClick={() => selectedSession && handleSubscribe(selectedSession)}>
                  <Zap className="w-3.5 h-3.5 group-hover:translate-x-0.5 transition-transform duration-200" /> Listen
                </Button>
                {selectedSession && (
                  <button
                    onClick={() => setConfirmDelete(`session:${selectedTarget}/${selectedSession}`)}
                    className="p-2 hover:bg-red-500/20 rounded-xl transition-colors text-[var(--muted-foreground)]/50 hover:text-red-400"
                  >
                    <Trash2 className="w-4 h-4" />
                  </button>
                )}
              </>
            )}
          </div>
        </header>

        <div className="relative z-10 flex-1 overflow-y-auto p-6 lg:p-8 flex flex-col gap-6">
          {/* ── Scan Initiation ── */}
          <AnimatedSection>
            <Card featured>
              <CardContent className="p-6 lg:p-8">
                <div className="flex items-center gap-4 mb-6">
                  <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-[var(--accent)] to-[var(--accent-secondary)] flex items-center justify-center shadow-[0_4px_14px_rgba(0,82,255,0.2)]">
                    <Radio className="w-5 h-5 text-white" />
                  </div>
                  <div>
                    <h2 className="font-display text-3xl">New <GradientText>Scan</GradientText></h2>
                    <p className="font-mono-label text-[11px] text-[var(--muted-foreground)]/60 mt-0.5">Press Enter to launch</p>
                  </div>
                </div>
                <div className="flex flex-col sm:flex-row gap-3">
                  <div className="flex-1 relative">
                    <input
                      ref={scanInputRef}
                      value={scanTarget}
                      onChange={e => setScanTarget(e.target.value)}
                      placeholder="target.com"
                      className="h-12 w-full rounded-xl border border-[var(--border)] bg-[var(--background)]/50 pr-10 pl-4 text-sm font-mono text-[var(--foreground)] placeholder:text-[var(--muted-foreground)]/30 outline-none transition-all duration-200 focus:border-[var(--accent)] focus:ring-2 focus:ring-[var(--ring)] focus:ring-offset-2 focus:ring-offset-[var(--card)] disabled:opacity-40"
                      disabled={currentScan.status === "running"}
                    />
                    <CornerDownLeft className="absolute right-3.5 top-1/2 -translate-y-1/2 w-4 h-4 text-[var(--muted-foreground)]/30 pointer-events-none" />
                  </div>
                  <div className="flex gap-2">
                    {(Object.entries(modeConfig) as [string, typeof modeConfig['recon']][]).map(([key, cfg]) => {
                      const Icon = cfg.icon;
                      return (
                        <button
                          key={key}
                          onClick={() => setScanMode(key)}
                          className={cn(
                            "h-12 px-4 rounded-xl text-xs font-bold uppercase tracking-wider transition-all duration-200 flex items-center gap-2",
                            scanMode === key
                              ? `bg-gradient-to-r ${cfg.color} text-white shadow-sm`
                              : "border border-[var(--border)] text-[var(--muted-foreground)]/60 hover:border-[var(--accent)]/30 hover:text-[var(--foreground)]"
                          )}
                        >
                          <Icon className="w-3.5 h-3.5" />
                          {cfg.label}
                        </button>
                      );
                    })}
                  </div>
                  <Button
                    size="lg"
                    onClick={handleStartScan}
                    disabled={currentScan.status === "running" || !scanTarget.trim()}
                    className="h-12 shrink-0"
                  >
                    {currentScan.status === "running" ? (
                      <Loader2 className="w-4 h-4 animate-spin" />
                    ) : (
                      <Play className="w-4 h-4 fill-white" />
                    )}
                    {currentScan.status === "running" ? "Running..." : "Launch"}
                  </Button>
                </div>
                {startError && (
                  <p className="mt-3 font-mono-label text-xs text-red-400 flex items-center gap-1.5">
                    <AlertCircle className="w-3.5 h-3.5" />{startError}
                  </p>
                )}
              </CardContent>
            </Card>
          </AnimatedSection>

          {/* ── Current Scan Progress ── */}
          {currentScan.status === "running" && (
            <AnimatedSection>
              <div className="relative rounded-xl border border-[var(--accent)]/20 bg-[var(--foreground)] text-[var(--background)] overflow-hidden">
                <div className="absolute inset-0 pointer-events-none" style={{ backgroundImage: "radial-gradient(circle, rgba(255,255,255,0.05) 1px, transparent 1px)", backgroundSize: "32px 32px" }} />
                <div className="relative z-10 p-6">
                  <div className="flex items-center justify-between mb-4">
                    <div className="flex items-center gap-3">
                      <motion.div
                        className="w-10 h-10 rounded-xl bg-gradient-to-br from-[var(--accent)] to-[var(--accent-secondary)] flex items-center justify-center shadow-[var(--shadow-accent)]"
                        animate={{ y: [0, -3, 0] }}
                        transition={{ duration: 4, repeat: Infinity, ease: "easeInOut" }}
                      >
                        <Activity className="w-5 h-5 text-white" />
                      </motion.div>
                      <div>
                        <p className="font-display text-base text-[var(--background)]"><GradientText>{currentScan.mode?.toUpperCase()}</GradientText> scan</p>
                        <p className="font-mono-label text-xs text-[var(--background)]/50">{currentScan.target}</p>
                      </div>
                    </div>
                    <span className="font-mono-label text-[10px] text-[var(--background)]/40 bg-[var(--background)]/5 px-3 py-1.5 rounded-lg border border-[var(--background)]/10">
                      {currentScan.phase}
                    </span>
                  </div>
                  <div className="w-full h-2 rounded-full bg-[var(--background)]/10 overflow-hidden">
                    <motion.div
                      className="h-full rounded-full bg-gradient-to-r from-[var(--accent)] to-[var(--accent-secondary)]"
                      initial={{ width: "5%" }}
                      animate={{ width: currentScan.phase === "done" ? "100%" : "60%" }}
                      transition={{ duration: 0.5, ease: [0.16, 1, 0.3, 1] }}
                    />
                  </div>
                  <p className="mt-3 font-mono-label text-[11px] text-[var(--background)]/40">
                    Phase: {currentScan.phase || "starting..."}
                  </p>
                </div>
              </div>
            </AnimatedSection>
          )}

          {/* ── Failed Scan ── */}
          {currentScan.status === "failed" && (
            <AnimatedSection>
              <div className="rounded-xl border border-red-500/20 bg-gradient-to-br from-red-500/5 to-transparent p-5 flex items-center gap-4">
                <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-red-600 to-red-500 flex items-center justify-center shadow-[0_4px_14px_rgba(220,38,38,0.25)]">
                  <AlertCircle className="w-5 h-5 text-white" />
                </div>
                <div>
                  <p className="font-display text-base text-red-300">Scan <GradientText>Failed</GradientText></p>
                  <p className="font-mono-label text-xs text-red-400/70 mt-0.5">{currentScan.phase}</p>
                </div>
              </div>
            </AnimatedSection>
          )}

          {/* ── Scan History ── */}
          {scanHistory.length > 0 && (
            <details className="group">
              <summary className="flex items-center gap-2 font-mono-label text-xs text-[var(--muted-foreground)]/50 hover:text-[var(--muted-foreground)] cursor-pointer list-none transition-colors">
                <History className="w-3.5 h-3.5" /> Scan History ({scanHistory.length})
              </summary>
              <div className="mt-3 space-y-1">
                {scanHistory.slice(0, 10).map(s => (
                  <div key={s.scan_id} className="flex items-center gap-3 font-mono-label text-[11px] text-[var(--muted-foreground)]/60 p-2.5 rounded-xl bg-[var(--muted)]/30">
                    <span className="w-16 flex-shrink-0">{s.started_at ? new Date(s.started_at).toLocaleTimeString() : "?"}</span>
                    <span className={cn(
                      "w-14 uppercase",
                      s.mode === "recon" ? "text-cyan-500" : s.mode === "scan" ? "text-amber-500" : "text-rose-500"
                    )}>{s.mode}</span>
                    <span className="truncate">{s.target}</span>
                    <span className={cn(
                      "ml-auto font-medium",
                      s.status === "completed" ? "text-emerald-500" :
                      s.status === "failed" ? "text-red-500" : "text-amber-500"
                    )}>{s.status}</span>
                  </div>
                ))}
              </div>
            </details>
          )}

          {/* ── Report + Log ── */}
          {selectedTarget && selectedSession && currentTarget ? (
            (() => {
              const sessionInfo = currentTarget.sessions.find(s => s.name === selectedSession);
              return (
                <>
                  {sessionInfo?.hasReport ? (
                    <Card className="flex-1 min-h-[350px] overflow-hidden relative group !p-0 !border-0">
                      <div className="absolute top-4 right-4 z-10 flex gap-2 opacity-0 group-hover:opacity-100 transition-opacity duration-200">
                        <a
                          href={getReportUrl(selectedTarget, selectedSession)}
                          target="_blank"
                          className="p-2 rounded-xl bg-[var(--card)]/90 border border-[var(--border)] hover:bg-[var(--muted)] transition-colors backdrop-blur-md"
                        >
                          <Maximize2 className="w-4 h-4 text-[var(--muted-foreground)]" />
                        </a>
                      </div>
                      <iframe
                        src={getReportUrl(selectedTarget, selectedSession)}
                        className="w-full h-full border-none rounded-xl"
                        title="Scan Report"
                      />
                    </Card>
                  ) : (
                    <Card className="flex-1 min-h-[200px]">
                      <CardContent className="flex flex-col items-center justify-center h-full gap-3 py-12">
                        <FileText className="w-10 h-10 text-[var(--muted-foreground)]/20" />
                        <p className="font-mono-label text-sm text-[var(--muted-foreground)]/40">No report generated</p>
                      </CardContent>
                    </Card>
                  )}

                  {/* ── Terminal ── */}
                  <Card className="bg-[var(--foreground)] border-transparent overflow-hidden relative">
                    <div className="absolute inset-0 pointer-events-none" style={{ backgroundImage: "radial-gradient(circle, rgba(255,255,255,0.05) 1px, transparent 1px)", backgroundSize: "32px 32px" }} />
                    <div className="relative z-10 px-5 py-3.5 border-b border-white/10 flex items-center justify-between bg-black/20">
                      <div className="flex items-center gap-2.5">
                        <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-[var(--accent)] to-[var(--accent-secondary)] flex items-center justify-center shadow-[var(--shadow-accent)]">
                          <Terminal className="w-4 h-4 text-white" />
                        </div>
                        <span className="font-mono-label text-xs uppercase tracking-[0.1em] text-white/70">Live Output</span>
                      </div>
                      <div className="flex items-center gap-4 font-mono-label text-[10px] text-white/50">
                        <button
                          onClick={() => setAutoScroll(!autoScroll)}
                          className={cn("flex items-center gap-1.5 hover:text-white/80 transition-colors", !autoScroll && "text-white/30")}
                        >
                          {autoScroll ? <Eye className="w-3 h-3" /> : <EyeOff className="w-3 h-3" />}
                          {autoScroll ? "Auto" : "Paused"}
                        </button>
                        <span>Buf: {logs.length}/500</span>
                        <button onClick={() => setLogs([])} className="hover:text-white/80 transition-colors">Clear</button>
                      </div>
                    </div>
                    <div className="relative z-10 h-56 overflow-y-auto p-4 font-mono text-xs leading-relaxed">
                      {logs.length > 0 ? (
                        logs.map((line, i) => (
                          <div key={i} className="flex gap-3 mb-0.5 group">
                            <span className="text-white/30 select-none w-7 text-right flex-shrink-0">{i + 1}</span>
                            <p className="text-white/90 break-all whitespace-pre-wrap">{line}</p>
                          </div>
                        ))
                      ) : (
                        <div className="h-full flex flex-col items-center justify-center text-white/30">
                          <Terminal className="w-8 h-8 mb-2" />
                          <p className="font-mono-label text-xs">Awaiting live connection...</p>
                          <p className="font-mono-label text-[10px] mt-1 opacity-60">Press Listen or start a scan</p>
                        </div>
                      )}
                      <div ref={logEndRef} />
                    </div>
                  </Card>
                </>
              );
            })()
          ) : (
            <AnimatedSection delay={0.2}>
              <div className="flex-1 flex flex-col items-center justify-center gap-5 min-h-[400px]">
                <motion.div
                  className="w-24 h-24 rounded-2xl bg-gradient-to-br from-[var(--accent)]/10 to-[var(--accent-secondary)]/5 border border-[var(--accent)]/20 flex items-center justify-center"
                  animate={{ y: [0, -4, 0] }}
                  transition={{ duration: 5, repeat: Infinity, ease: "easeInOut" }}
                >
                  <Search className="w-10 h-10 text-[var(--accent)]/40" />
                </motion.div>
                <div className="text-center">
                  <h2 className="font-display text-2xl text-[var(--muted-foreground)]/60 mb-2">No <GradientText>Data</GradientText> Available</h2>
                  <p className="font-mono-label text-sm text-[var(--muted-foreground)]/30 max-w-xs">
                    Enter a target above and launch a scan, or select an existing target from the sidebar.
                  </p>
                </div>
              </div>
            </AnimatedSection>
          )}
        </div>
      </main>

      {/* ── Confirm Delete Modal ── */}
      <AnimatePresence>
        {confirmDelete && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 backdrop-blur-sm"
          >
            <motion.div
              initial={{ scale: 0.9, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              exit={{ scale: 0.9, opacity: 0 }}
              transition={{ duration: 0.2, ease: [0.16, 1, 0.3, 1] }}
              className="rounded-xl border border-[var(--border)] bg-[var(--card)] p-6 max-w-sm w-full mx-4 shadow-2xl"
            >
              <div className="flex items-center gap-3 mb-4">
                <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-red-600 to-red-500 flex items-center justify-center">
                  <AlertCircle className="w-5 h-5 text-white" />
                </div>
                <h3 className="font-display text-lg">Confirm Deletion</h3>
              </div>
              <p className="font-mono-label text-sm text-[var(--muted-foreground)]/60 mb-6">
                {confirmDelete.startsWith("target:")
                  ? `Delete all sessions for "${confirmDelete.slice(7)}"? This cannot be undone.`
                  : `Delete session "${confirmDelete.split("/")[1]}" for "${confirmDelete.split("/")[0].slice(8)}"?`
                }
              </p>
              <div className="flex gap-3 justify-end">
                <Button variant="secondary" size="sm" onClick={() => setConfirmDelete(null)}>
                  Cancel
                </Button>
                <Button
                  variant="danger"
                  size="sm"
                  onClick={() =>
                    confirmDelete.startsWith("target:")
                      ? handleDeleteTarget(confirmDelete.slice(7))
                      : handleDeleteSession(...confirmDelete.slice(8).split("/") as [string, string])
                  }
                >
                  Delete
                </Button>
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
