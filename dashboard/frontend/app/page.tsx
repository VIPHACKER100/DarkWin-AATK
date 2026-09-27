"use client";

import React, { useState, useEffect, useCallback, useRef } from "react";
import { Sidebar, NavTab } from "@/components/sidebar";
import { Header } from "@/components/header";
import { ScanWizardModal } from "@/components/scan-wizard-modal";
import { OverviewView } from "@/components/views/overview-view";
import { TargetsView } from "@/components/views/targets-view";
import { VulnerabilitiesView } from "@/components/views/vulnerabilities-view";
import { TerminalView } from "@/components/views/terminal-view";
import { ToolsView } from "@/components/views/tools-view";
import { SettingsView } from "@/components/views/settings-view";
import {
  getTargets,
  getStats,
  getCurrentScan,
  startScan,
  stopScan,
  deleteTarget,
  deleteSession,
  TargetItem,
  SystemStats,
  CurrentScan,
  VulnerabilityFinding,
} from "@/lib/api";
import { socket } from "@/lib/socket";

export default function DashboardPage() {
  const [activeTab, setActiveTab] = useState<NavTab>("overview");
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);
  const [targets, setTargets] = useState<TargetItem[]>([]);
  const [selectedTarget, setSelectedTarget] = useState<string | null>(null);
  const [stats, setStats] = useState<SystemStats | null>(null);
  const [currentScan, setCurrentScan] = useState<CurrentScan>({
    scan_id: null,
    target: null,
    mode: null,
    status: "idle",
    phase: null,
    started_at: null,
    progress: 0,
  });
  const [logs, setLogs] = useState<string[]>([]);
  const [socketStatus, setSocketStatus] = useState<"connected" | "disconnected" | "reconnecting">("disconnected");
  const [scanModalOpen, setScanModalOpen] = useState(false);
  const [searchQuery, setSearchQuery] = useState("");
  const pollIntervalRef = useRef<NodeJS.Timeout | null>(null);

  const fetchData = useCallback(async () => {
    try {
      const [tData, sData, cScan] = await Promise.allSettled([
        getTargets(),
        getStats(),
        getCurrentScan(),
      ]);

      if (tData.status === "fulfilled") {
        setTargets(tData.value);
        if (tData.value.length > 0 && !selectedTarget) {
          setSelectedTarget(tData.value[0].target);
        }
      }
      if (sData.status === "fulfilled") {
        setStats(sData.value);
      }
      if (cScan.status === "fulfilled") {
        setCurrentScan(cScan.value);
      }
    } catch {
      // ignore
    }
  }, [selectedTarget]);

  useEffect(() => {
    fetchData();
    socket.connect();

    socket.on("connect", () => {
      setSocketStatus("connected");
    });
    socket.on("disconnect", () => setSocketStatus("disconnected"));
    socket.on("reconnecting", () => setSocketStatus("reconnecting"));
    socket.on("connect_error", () => setSocketStatus("disconnected"));

    socket.on("scan_update", (data: { scan_id: string; line: string }) => {
      setLogs((prev) => [...prev.slice(-999), data.line]);
    });

    socket.on("scan_phase", (data: { phase: string; mode?: string }) => {
      setCurrentScan((prev) => ({ ...prev, phase: data.phase, mode: data.mode || prev.mode }));
    });

    socket.on("scan_progress", (data: { progress: number; phase: string | null; mode?: string }) => {
      setCurrentScan((prev) => ({
        ...prev,
        progress: typeof data.progress === "number" ? data.progress : prev.progress,
        phase: data.phase ?? prev.phase,
      }));
    });

    socket.on("scan_done", () => {
      setCurrentScan((prev) => ({
        ...prev,
        status: "completed",
        phase: "done",
        progress: 100,
      }));
      fetchData();
    });

    socket.on("scan_error", (data: { error: string }) => {
      setCurrentScan((prev) => ({
        ...prev,
        status: "failed",
        phase: data.error,
      }));
    });

    socket.on("target_deleted", fetchData);
    socket.on("session_deleted", fetchData);

    // Heartbeat poll for current scan
    pollIntervalRef.current = setInterval(async () => {
      try {
        const scan = await getCurrentScan();
        setCurrentScan(scan);
      } catch {
        // ignore
      }
    }, 5000);

    return () => {
      socket.disconnect();
      if (pollIntervalRef.current) clearInterval(pollIntervalRef.current);
    };
  }, [fetchData]);

  const handleStartScan = async (target: string, mode: string) => {
    const res = await startScan(target, mode);
    setCurrentScan({
      scan_id: res.scan_id,
      target: res.target,
      mode: res.mode,
      status: "running",
      phase: "initializing",
      started_at: new Date().toISOString(),
      progress: 0,
    });
    // Subscribe to live log room for this scan
    socket.emit("subscribe", { scan_id: res.scan_id });
    setLogs([`[*] Scan pipeline '${mode}' initiated against target ${target}...`]);
    setActiveTab("terminal");
    fetchData();
  };

  const handleStopScan = async () => {
    try {
      await stopScan();
      setCurrentScan((prev) => ({ ...prev, status: "aborted", phase: "aborted by operator" }));
    } catch {
      // ignore
    }
  };

  const handleDeleteTarget = async (target: string) => {
    await deleteTarget(target);
    fetchData();
  };

  const handleDeleteSession = async (target: string, session: string) => {
    await deleteSession(target, session);
    fetchData();
  };

  const getTabTitle = () => {
    switch (activeTab) {
      case "overview":
        return { title: "Command Center & Analytics", subtitle: "Real-time threat landscape and scan orchestration" };
      case "targets":
        return { title: "Target & Asset Inventory", subtitle: "Subdomain enumeration, open ports, and discovered surface" };
      case "vulns":
        return { title: "Vulnerability Triage Hub", subtitle: "Identified security findings, severity ratings, and reproduction PoCs" };
      case "terminal":
        return { title: "Tactical Telemetry Stream", subtitle: "Live raw subprocess output and security tool logs" };
      case "tools":
        return { title: "Tool Arsenal Diagnostics", subtitle: "Verification and discovery status of external security binaries" };
      case "settings":
        return { title: "Configuration Studio", subtitle: "Engine concurrency, API credentials, and default profiles" };
    }
  };

  const { title, subtitle } = getTabTitle();

  return (
    <div className="flex h-screen w-full bg-[#07090E] text-slate-100 overflow-hidden font-sans selection:bg-blue-600 selection:text-white">
      {/* Sidebar Navigation */}
      <Sidebar
        activeTab={activeTab}
        setActiveTab={setActiveTab}
        collapsed={sidebarCollapsed}
        setCollapsed={setSidebarCollapsed}
        socketStatus={socketStatus}
        activeScan={currentScan.status === "running"}
      />

      {/* Main Content Area */}
      <div className="flex flex-1 flex-col overflow-hidden">
        {/* Global Header */}
        <Header
          title={title}
          subtitle={subtitle}
          currentScan={currentScan}
          onOpenScanModal={() => setScanModalOpen(true)}
          onStopScan={handleStopScan}
          onRefresh={fetchData}
          searchQuery={searchQuery}
          setSearchQuery={setSearchQuery}
        />

        {/* Dynamic Viewport */}
        <main className="flex-1 overflow-y-auto p-6 bg-grid-pattern">
          {activeTab === "overview" && (
            <OverviewView
              stats={stats}
              targets={targets}
              currentScan={currentScan}
              onOpenScanModal={() => setScanModalOpen(true)}
              onSelectTarget={(t) => setSelectedTarget(t)}
              onNavigateToTab={(tab) => setActiveTab(tab)}
            />
          )}

          {activeTab === "targets" && (
            <TargetsView
              targets={targets}
              selectedTarget={selectedTarget}
              onSelectTarget={setSelectedTarget}
              onDeleteTarget={handleDeleteTarget}
              onDeleteSession={handleDeleteSession}
            />
          )}

          {activeTab === "vulns" && <VulnerabilitiesView findings={[]} />}

          {activeTab === "terminal" && (
            <TerminalView
              logs={logs}
              currentScan={currentScan}
              onClearLogs={() => setLogs([])}
            />
          )}

          {activeTab === "tools" && <ToolsView />}

          {activeTab === "settings" && <SettingsView />}
        </main>
      </div>

      {/* Launch Scan Modal */}
      <ScanWizardModal
        isOpen={scanModalOpen}
        onClose={() => setScanModalOpen(false)}
        onStartScan={handleStartScan}
        initialTarget={selectedTarget || ""}
      />
    </div>
  );
}
