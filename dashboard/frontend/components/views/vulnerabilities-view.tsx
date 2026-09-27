"use client";

import React, { useState } from "react";
import {
  ShieldAlert,
  Search,
  Filter,
  ExternalLink,
  Copy,
  Check,
  X,
  AlertTriangle,
  Info,
  Bug,
} from "lucide-react";
import { VulnerabilityFinding } from "@/lib/api";
import { cn } from "@/lib/utils";

interface VulnerabilitiesViewProps {
  findings: VulnerabilityFinding[];
}

export function VulnerabilitiesView({ findings }: VulnerabilitiesViewProps) {
  const [selectedSeverity, setSelectedSeverity] = useState<string>("ALL");
  const [search, setSearch] = useState("");
  const [activeFinding, setActiveFinding] = useState<VulnerabilityFinding | null>(null);
  const [copied, setCopied] = useState(false);

  // Sample findings if none loaded yet
  const displayFindings: VulnerabilityFinding[] = findings.length > 0 ? findings : [
    {
      id: "VULN-001",
      title: "Reflected Cross-Site Scripting (XSS) in Search Parameter",
      severity: "HIGH",
      target: "example.com",
      category: "XSS",
      description: "User input supplied via the 'q' parameter is reflected in the HTML response without HTML entity encoding, allowing execution of arbitrary client-side JavaScript.",
      poc: "curl -i -s -k -X $'GET' $'https://example.com/search?q=%3Cscript%3Ealert(document.domain)%3C/script%3E'",
      remediation: "Implement context-aware HTML entity encoding or utilize a secure template framework with auto-escaping enabled.",
      timestamp: "2026-09-27T16:20:00Z"
    },
    {
      id: "VULN-002",
      title: "Blind SQL Injection via Time-Based Delay",
      severity: "CRITICAL",
      target: "api.example.com",
      category: "SQLi",
      description: "Database backend executes time-delayed payloads (e.g. pg_sleep(5)), confirming unescaped SQL parameter concatenation.",
      poc: "curl -X POST 'https://api.example.com/v1/auth' -d '{\"user\": \"admin' AND (SELECT 1 FROM (SELECT(PG_SLEEP(5)))a)--\"}'",
      remediation: "Use parameterized prepared statements with bind variables across all database queries.",
      timestamp: "2026-09-27T17:10:00Z"
    },
    {
      id: "VULN-003",
      title: "Insecure Direct Object Reference (IDOR) on Invoice API",
      severity: "HIGH",
      target: "billing.example.com",
      category: "IDOR",
      description: "Accessing `/api/invoices/10492` allows viewing invoices of other tenant accounts without authorization check.",
      poc: "curl -H 'Authorization: Bearer <user_token>' 'https://billing.example.com/api/invoices/10492'",
      remediation: "Enforce object-level access control verifying authenticated user ownership before returning entity records.",
      timestamp: "2026-09-27T17:45:00Z"
    },
    {
      id: "VULN-004",
      title: "Public AWS S3 Bucket Allowing Anonymous Read",
      severity: "MEDIUM",
      target: "assets.example.com",
      category: "Cloud",
      description: "Permissive S3 bucket ACL exposes internal static asset backups to anonymous internet users.",
      poc: "aws s3 ls s3://assets.example.com --no-sign-request",
      remediation: "Enable AWS S3 Block Public Access at both the bucket and account levels.",
      timestamp: "2026-09-27T18:05:00Z"
    }
  ];

  const filtered = displayFindings.filter((f) => {
    const matchesSev = selectedSeverity === "ALL" || f.severity === selectedSeverity;
    const matchesSearch =
      f.title.toLowerCase().includes(search.toLowerCase()) ||
      f.target.toLowerCase().includes(search.toLowerCase()) ||
      (f.category || "").toLowerCase().includes(search.toLowerCase());
    return matchesSev && matchesSearch;
  });

  const getSeverityBadge = (severity: string) => {
    switch (severity) {
      case "CRITICAL":
        return "bg-red-950/70 text-red-400 border-red-500/40";
      case "HIGH":
        return "bg-orange-950/70 text-orange-400 border-orange-500/40";
      case "MEDIUM":
        return "bg-amber-950/70 text-amber-400 border-amber-500/40";
      case "LOW":
        return "bg-cyan-950/70 text-cyan-400 border-cyan-500/40";
      default:
        return "bg-slate-900 text-slate-400 border-slate-700";
    }
  };

  const handleCopyPoC = () => {
    if (!activeFinding?.poc) return;
    navigator.clipboard.writeText(activeFinding.poc);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="space-y-6">
      {/* Top Filter Bar */}
      <div className="glass-panel p-4 rounded-2xl border border-slate-800 flex flex-wrap items-center justify-between gap-4">
        {/* Severity Tabs */}
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

        {/* Search */}
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
            {filtered.map((item, idx) => (
              <tr
                key={idx}
                onClick={() => setActiveFinding(item)}
                className="hover:bg-slate-800/30 cursor-pointer transition-colors group"
              >
                <td className="px-5 py-3">
                  <span
                    className={cn(
                      "px-2 py-0.5 rounded text-[10px] font-bold border",
                      getSeverityBadge(item.severity)
                    )}
                  >
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
                    Inspect PoC →
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Finding Detail Drawer Modal */}
      {activeFinding && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/80 backdrop-blur-sm p-4 animate-in fade-in duration-150">
          <div className="relative w-full max-w-2xl rounded-2xl border border-slate-800 bg-[#0A0E17] shadow-2xl overflow-hidden p-6 space-y-5">
            <div className="flex items-start justify-between pb-4 border-b border-slate-800">
              <div>
                <div className="flex items-center gap-2 mb-1.5">
                  <span
                    className={cn(
                      "px-2 py-0.5 rounded text-[10px] font-bold border font-mono",
                      getSeverityBadge(activeFinding.severity)
                    )}
                  >
                    {activeFinding.severity}
                  </span>
                  <span className="text-xs text-blue-400 font-mono">{activeFinding.target}</span>
                </div>
                <h3 className="text-base font-bold text-white font-mono">{activeFinding.title}</h3>
              </div>
              <button
                onClick={() => setActiveFinding(null)}
                className="p-1.5 text-slate-400 hover:text-white rounded-lg hover:bg-slate-800"
              >
                <X className="h-4 w-4" />
              </button>
            </div>

            {/* Description */}
            <div className="space-y-1.5">
              <h4 className="text-xs font-semibold uppercase tracking-wider text-slate-400 font-mono">
                Technical Description
              </h4>
              <p className="text-xs text-slate-300 leading-relaxed font-mono">
                {activeFinding.description}
              </p>
            </div>

            {/* Proof of Concept (PoC) */}
            {activeFinding.poc && (
              <div className="space-y-1.5">
                <div className="flex items-center justify-between">
                  <h4 className="text-xs font-semibold uppercase tracking-wider text-slate-400 font-mono">
                    Reproduction Proof-of-Concept
                  </h4>
                  <button
                    onClick={handleCopyPoC}
                    className="flex items-center gap-1 text-[11px] text-blue-400 hover:text-blue-300 font-mono"
                  >
                    {copied ? <Check className="h-3 w-3 text-emerald-400" /> : <Copy className="h-3 w-3" />}
                    <span>{copied ? "Copied" : "Copy PoC"}</span>
                  </button>
                </div>
                <pre className="p-3 rounded-xl bg-slate-950 border border-slate-800 text-xs text-emerald-400 font-mono overflow-x-auto">
                  <code>{activeFinding.poc}</code>
                </pre>
              </div>
            )}

            {/* Remediation */}
            {activeFinding.remediation && (
              <div className="space-y-1.5">
                <h4 className="text-xs font-semibold uppercase tracking-wider text-slate-400 font-mono">
                  Remediation & Defense
                </h4>
                <div className="p-3 rounded-xl bg-slate-900/60 border border-slate-800 text-xs text-slate-300 font-mono leading-relaxed">
                  {activeFinding.remediation}
                </div>
              </div>
            )}

            <div className="flex justify-end pt-2">
              <button
                onClick={() => setActiveFinding(null)}
                className="px-4 py-2 rounded-xl text-xs font-mono font-medium text-slate-300 bg-slate-800 hover:bg-slate-700 transition-colors"
              >
                Close Drawer
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
