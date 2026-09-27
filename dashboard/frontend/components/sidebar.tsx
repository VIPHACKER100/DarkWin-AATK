"use client";

import React from "react";
import {
  Activity,
  Target,
  ShieldAlert,
  Terminal,
  Wrench,
  Settings,
  Zap,
  Radio,
  Wifi,
  WifiOff,
  ChevronLeft,
  ChevronRight,
} from "lucide-react";
import { cn } from "@/lib/utils";

export type NavTab = "overview" | "targets" | "vulns" | "terminal" | "tools" | "settings";

interface SidebarProps {
  activeTab: NavTab;
  setActiveTab: (tab: NavTab) => void;
  collapsed: boolean;
  setCollapsed: (collapsed: boolean) => void;
  socketStatus: "connected" | "disconnected" | "reconnecting";
  activeScan: boolean;
}

export function Sidebar({
  activeTab,
  setActiveTab,
  collapsed,
  setCollapsed,
  socketStatus,
  activeScan,
}: SidebarProps) {
  const navItems = [
    { id: "overview", label: "Overview", icon: Activity, badge: null },
    { id: "targets", label: "Targets & Assets", icon: Target, badge: null },
    { id: "vulns", label: "Vulnerabilities", icon: ShieldAlert, badge: "Alert" },
    { id: "terminal", label: "Live Terminal", icon: Terminal, badge: activeScan ? "Active" : null },
    { id: "tools", label: "Tool Arsenal", icon: Wrench, badge: null },
    { id: "settings", label: "Config Studio", icon: Settings, badge: null },
  ] as const;

  return (
    <aside
      className={cn(
        "relative flex flex-col justify-between border-r border-slate-800/80 bg-[#0A0E17]/95 backdrop-blur-xl transition-all duration-300 z-30",
        collapsed ? "w-20" : "w-64"
      )}
    >
      {/* Brand Header */}
      <div>
        <div className="flex items-center justify-between px-4 py-5 border-b border-slate-800/60">
          <div className="flex items-center gap-3 overflow-hidden">
            <div className="relative flex h-10 w-10 shrink-0 items-center justify-center rounded-xl bg-gradient-to-br from-blue-600 to-cyan-500 shadow-lg shadow-blue-600/30">
              <Zap className="h-5 w-5 text-white animate-pulse" />
              {activeScan && (
                <span className="absolute -top-1 -right-1 flex h-3 w-3">
                  <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-cyan-400 opacity-75"></span>
                  <span className="relative inline-flex rounded-full h-3 w-3 bg-cyan-500"></span>
                </span>
              )}
            </div>
            {!collapsed && (
              <div className="flex flex-col">
                <span className="font-bold tracking-wider text-white text-base font-mono-label flex items-center gap-1.5">
                  DARKWIN
                  <span className="text-[10px] uppercase tracking-normal px-1.5 py-0.5 rounded bg-blue-950/80 border border-blue-500/30 text-blue-400 font-semibold">
                    AATK
                  </span>
                </span>
                <span className="text-[11px] text-slate-400 font-mono-label">v1.3.0 · Command C2</span>
              </div>
            )}
          </div>
          <button
            onClick={() => setCollapsed(!collapsed)}
            className="p-1.5 rounded-lg text-slate-400 hover:text-white hover:bg-slate-800/60 transition-colors"
            title={collapsed ? "Expand Sidebar" : "Collapse Sidebar"}
          >
            {collapsed ? <ChevronRight className="h-4 w-4" /> : <ChevronLeft className="h-4 w-4" />}
          </button>
        </div>

        {/* Navigation Items */}
        <nav className="p-3 space-y-1.5">
          {navItems.map((item) => {
            const Icon = item.icon;
            const isActive = activeTab === item.id;
            return (
              <button
                key={item.id}
                onClick={() => setActiveTab(item.id as NavTab)}
                className={cn(
                  "w-full flex items-center gap-3.5 px-3.5 py-3 rounded-xl text-sm font-medium transition-all group relative",
                  isActive
                    ? "bg-gradient-to-r from-blue-600/20 to-blue-500/10 text-white border border-blue-500/40 shadow-lg shadow-blue-500/10"
                    : "text-slate-400 hover:text-slate-200 hover:bg-slate-800/40 border border-transparent"
                )}
                title={collapsed ? item.label : undefined}
              >
                <Icon
                  className={cn(
                    "h-5 w-5 shrink-0 transition-transform group-hover:scale-110",
                    isActive ? "text-blue-400" : "text-slate-400 group-hover:text-slate-200"
                  )}
                />
                {!collapsed && (
                  <span className="truncate flex-1 text-left tracking-wide">{item.label}</span>
                )}
                {!collapsed && item.badge && (
                  <span
                    className={cn(
                      "text-[10px] px-2 py-0.5 rounded-full font-mono font-semibold tracking-wider uppercase",
                      item.badge === "Active"
                        ? "bg-cyan-500/20 text-cyan-300 border border-cyan-500/30 animate-pulse"
                        : "bg-red-500/20 text-red-300 border border-red-500/30"
                    )}
                  >
                    {item.badge}
                  </span>
                )}
                {/* Active indicator bar */}
                {isActive && (
                  <span className="absolute left-0 top-2 bottom-2 w-1 rounded-r bg-blue-500" />
                )}
              </button>
            );
          })}
        </nav>
      </div>

      {/* Telemetry Status Footer */}
      <div className="p-3 border-t border-slate-800/60 bg-[#070A11]/60">
        <div
          className={cn(
            "flex items-center gap-3 p-2.5 rounded-xl border border-slate-800/80 bg-slate-900/50",
            collapsed ? "justify-center" : "justify-between"
          )}
        >
          <div className="flex items-center gap-2.5">
            <span className="relative flex h-2.5 w-2.5">
              {socketStatus === "connected" ? (
                <>
                  <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
                  <span className="relative inline-flex rounded-full h-2.5 w-2.5 bg-emerald-500"></span>
                </>
              ) : (
                <span className="relative inline-flex rounded-full h-2.5 w-2.5 bg-rose-500"></span>
              )}
            </span>
            {!collapsed && (
              <span className="text-xs font-mono font-medium text-slate-300">
                {socketStatus === "connected" ? "Live Telemetry" : "Disconnected"}
              </span>
            )}
          </div>
          {!collapsed && (
            <span className="text-[10px] font-mono uppercase tracking-wider text-slate-500">
              WS :5000
            </span>
          )}
        </div>
      </div>
    </aside>
  );
}
