"use client";

import React, { useEffect } from "react";
import { AlertTriangle, RefreshCw } from "lucide-react";

export default function ErrorBoundary({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  useEffect(() => {
    console.error("Dashboard error caught by boundary:", error);
  }, [error]);

  return (
    <div className="h-screen w-full flex items-center justify-center p-6 bg-slate-950 font-mono">
      <div className="max-w-md w-full p-6 rounded-2xl bg-slate-900/80 border border-red-500/30 text-center space-y-5">
        <div className="inline-flex p-3 rounded-xl bg-red-950/50 border border-red-500/20 text-red-400">
          <AlertTriangle className="h-8 w-8" />
        </div>

        <div className="space-y-2">
          <h2 className="text-base font-bold text-white">Component Render Error</h2>
          <p className="text-xs text-slate-400">
            {error?.message || "An unexpected error occurred while rendering the dashboard view."}
          </p>
          {error?.digest && (
            <p className="text-[10px] text-slate-600">Digest: {error.digest}</p>
          )}
        </div>

        <div className="flex items-center justify-center gap-3 pt-2">
          <button
            onClick={() => reset()}
            className="flex items-center gap-2 px-4 py-2 rounded-xl bg-blue-600 hover:bg-blue-500 text-white text-xs font-semibold tracking-wide transition-all shadow-lg shadow-blue-600/30 cursor-pointer"
          >
            <RefreshCw className="h-3.5 w-3.5" />
            <span>Try Again</span>
          </button>
          <button
            onClick={() => window.location.reload()}
            className="px-4 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-300 text-xs font-semibold tracking-wide border border-slate-700 transition-all cursor-pointer"
          >
            Reload Page
          </button>
        </div>
      </div>
    </div>
  );
}
