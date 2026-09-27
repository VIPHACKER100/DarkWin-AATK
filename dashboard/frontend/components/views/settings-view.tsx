"use client";

import React, { useState, useEffect } from "react";
import {
  Settings,
  Key,
  Sliders,
  Save,
  Check,
  AlertCircle,
  Eye,
  EyeOff,
} from "lucide-react";
import { getConfig, saveConfig } from "@/lib/api";

export interface DarkWinConfig {
  general?: {
    threads?: number;
    timeout?: number;
    user_agent?: string;
  };
  api_keys?: {
    github_token?: string;
    hibp_api_key?: string;
    hunter_api_key?: string;
    shodan_api_key?: string;
    [key: string]: string | undefined;
  };
  reporting?: {
    author?: string;
    company?: string;
  };
  [key: string]: any;
}

export function SettingsView() {
  const [config, setConfig] = useState<DarkWinConfig | null>(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [saved, setSaved] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [showKeys, setShowKeys] = useState(false);

  useEffect(() => {
    getConfig()
      .then(setConfig)
      .catch(() => setError("Failed to load engine configuration"))
      .finally(() => setLoading(false));
  }, []);

  const handleSave = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!config) return;
    setSaving(true);
    setError(null);
    try {
      await saveConfig(config);
      setSaved(true);
      setTimeout(() => setSaved(false), 3000);
    } catch (err: unknown) {
      const errorMsg = (err as { response?: { data?: { error?: string } } })?.response?.data?.error;
      setError(errorMsg || "Failed to save configuration");
    } finally {
      setSaving(false);
    }
  };

  if (loading) {
    return (
      <div className="h-64 flex items-center justify-center text-slate-500 font-mono text-xs">
        Loading configuration...
      </div>
    );
  }

  return (
    <div className="space-y-6 max-w-4xl">
      <div className="glass-panel p-6 rounded-2xl border border-slate-800 flex items-center justify-between">
        <div>
          <h2 className="text-base font-bold text-white font-mono flex items-center gap-2">
            <Settings className="h-5 w-5 text-blue-400" />
            Scanner Engine Configuration Studio
          </h2>
          <p className="text-xs text-slate-400 mt-1">
            Manage core YAML parameters, API integrations, and scanning defaults
          </p>
        </div>

        {saved && (
          <span className="flex items-center gap-1.5 text-xs text-emerald-400 font-mono bg-emerald-950/60 px-3 py-1 rounded-xl border border-emerald-500/30">
            <Check className="h-3.5 w-3.5" /> Saved Successfully
          </span>
        )}
      </div>

      <form onSubmit={handleSave} className="space-y-6">
        {/* General Settings Card */}
        <div className="glass-panel p-6 rounded-2xl border border-slate-800 space-y-4">
          <h3 className="text-xs font-bold uppercase tracking-wider text-slate-300 font-mono flex items-center gap-2">
            <Sliders className="h-4 w-4 text-cyan-400" />
            General Engine Concurrency & Execution
          </h3>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-xs font-mono">
            <div className="space-y-1.5">
              <label className="text-slate-400">Default Concurrency Threads</label>
              <input
                type="number"
                min="1"
                max="100"
                value={config?.general?.threads || 10}
                onChange={(e) =>
                  setConfig({
                    ...config,
                    general: { ...config?.general, threads: Number(e.target.value) },
                  })
                }
                className="w-full px-3 py-2 rounded-xl bg-slate-900 border border-slate-800 text-slate-200 focus:outline-none focus:border-blue-500"
              />
            </div>

            <div className="space-y-1.5">
              <label className="text-slate-400">Subprocess Timeout (seconds)</label>
              <input
                type="number"
                min="30"
                max="3600"
                value={config?.general?.timeout || 300}
                onChange={(e) =>
                  setConfig({
                    ...config,
                    general: { ...config?.general, timeout: Number(e.target.value) },
                  })
                }
                className="w-full px-3 py-2 rounded-xl bg-slate-900 border border-slate-800 text-slate-200 focus:outline-none focus:border-blue-500"
              />
            </div>

            <div className="space-y-1.5 md:col-span-2">
              <label className="text-slate-400">HTTP User-Agent String</label>
              <input
                type="text"
                value={config?.general?.user_agent || ""}
                onChange={(e) =>
                  setConfig({
                    ...config,
                    general: { ...config?.general, user_agent: e.target.value },
                  })
                }
                className="w-full px-3 py-2 rounded-xl bg-slate-900 border border-slate-800 text-slate-200 focus:outline-none focus:border-blue-500"
              />
            </div>
          </div>
        </div>

        {/* API Keys Card */}
        <div className="glass-panel p-6 rounded-2xl border border-slate-800 space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="text-xs font-bold uppercase tracking-wider text-slate-300 font-mono flex items-center gap-2">
              <Key className="h-4 w-4 text-purple-400" />
              OSINT & Threat Intelligence API Keys
            </h3>
            <button
              type="button"
              onClick={() => setShowKeys(!showKeys)}
              className="text-xs text-slate-400 hover:text-white flex items-center gap-1 font-mono"
            >
              {showKeys ? <EyeOff className="h-3.5 w-3.5" /> : <Eye className="h-3.5 w-3.5" />}
              <span>{showKeys ? "Hide Keys" : "Show Keys"}</span>
            </button>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-xs font-mono">
            <div className="space-y-1.5">
              <label className="text-slate-400">GitHub Personal Access Token</label>
              <input
                type={showKeys ? "text" : "password"}
                placeholder="ghp_xxxxxxxxxxxx"
                value={config?.api_keys?.github_token || ""}
                onChange={(e) =>
                  setConfig({
                    ...config,
                    api_keys: { ...config?.api_keys, github_token: e.target.value },
                  })
                }
                className="w-full px-3 py-2 rounded-xl bg-slate-900 border border-slate-800 text-slate-200 focus:outline-none focus:border-blue-500"
              />
            </div>

            <div className="space-y-1.5">
              <label className="text-slate-400">HaveIBeenPwned API Key</label>
              <input
                type={showKeys ? "text" : "password"}
                placeholder="hibp_api_key"
                value={config?.api_keys?.hibp_api_key || ""}
                onChange={(e) =>
                  setConfig({
                    ...config,
                    api_keys: { ...config?.api_keys, hibp_api_key: e.target.value },
                  })
                }
                className="w-full px-3 py-2 rounded-xl bg-slate-900 border border-slate-800 text-slate-200 focus:outline-none focus:border-blue-500"
              />
            </div>

            <div className="space-y-1.5">
              <label className="text-slate-400">Hunter.io API Key</label>
              <input
                type={showKeys ? "text" : "password"}
                placeholder="hunter_api_key"
                value={config?.api_keys?.hunter_api_key || ""}
                onChange={(e) =>
                  setConfig({
                    ...config,
                    api_keys: { ...config?.api_keys, hunter_api_key: e.target.value },
                  })
                }
                className="w-full px-3 py-2 rounded-xl bg-slate-900 border border-slate-800 text-slate-200 focus:outline-none focus:border-blue-500"
              />
            </div>

            <div className="space-y-1.5">
              <label className="text-slate-400">Shodan API Key</label>
              <input
                type={showKeys ? "text" : "password"}
                placeholder="shodan_api_key"
                value={config?.api_keys?.shodan_api_key || ""}
                onChange={(e) =>
                  setConfig({
                    ...config,
                    api_keys: { ...config?.api_keys, shodan_api_key: e.target.value },
                  })
                }
                className="w-full px-3 py-2 rounded-xl bg-slate-900 border border-slate-800 text-slate-200 focus:outline-none focus:border-blue-500"
              />
            </div>
          </div>
        </div>

        {error && (
          <div className="p-3 rounded-xl bg-red-950/40 border border-red-500/40 text-xs text-red-300 font-mono flex items-center gap-2">
            <AlertCircle className="h-4 w-4 text-red-400" />
            <span>{error}</span>
          </div>
        )}

        <div className="flex justify-end">
          <button
            type="submit"
            disabled={saving}
            className="flex items-center gap-2 px-6 py-2.5 rounded-xl text-xs font-bold text-white bg-blue-600 hover:bg-blue-500 font-mono transition-all disabled:opacity-50"
          >
            <Save className="h-4 w-4" />
            <span>{saving ? "Saving..." : "Save Configuration"}</span>
          </button>
        </div>
      </form>
    </div>
  );
}
