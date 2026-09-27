"use client";

import React, { useEffect } from "react";

export default function GlobalError({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  useEffect(() => {
    // Log the error to console for debugging
    console.error("Global Error Caught:", error);
  }, [error]);

  return (
    <html lang="en">
      <body className="bg-slate-950 text-slate-100 min-h-screen flex items-center justify-center p-6 font-mono">
        <div className="max-w-lg w-full p-8 rounded-2xl bg-slate-900/90 border border-red-500/40 shadow-2xl backdrop-blur-xl text-center space-y-6">
          <div className="inline-flex p-4 rounded-full bg-red-950/60 border border-red-500/30 text-red-400">
            <svg
              className="w-10 h-10"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"
              />
            </svg>
          </div>

          <div className="space-y-2">
            <h1 className="text-xl font-bold tracking-tight text-white">
              DARKWIN Subsystem Failure
            </h1>
            <p className="text-xs text-slate-400 leading-relaxed">
              {error?.message || "An unexpected runtime error occurred in the control center."}
            </p>
            {error?.digest && (
              <p className="text-[10px] text-slate-600 font-mono">
                Digest: {error.digest}
              </p>
            )}
          </div>

          <div className="flex items-center justify-center gap-3 pt-2">
            <button
              onClick={() => reset()}
              className="px-4 py-2 rounded-xl bg-blue-600 hover:bg-blue-500 text-white text-xs font-semibold tracking-wide transition-all shadow-lg shadow-blue-600/30 cursor-pointer"
            >
              Reload Subsystem
            </button>
            <button
              onClick={() => window.location.reload()}
              className="px-4 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-300 text-xs font-semibold tracking-wide border border-slate-700 transition-all cursor-pointer"
            >
              Hard Refresh
            </button>
          </div>
        </div>
      </body>
    </html>
  );
}
