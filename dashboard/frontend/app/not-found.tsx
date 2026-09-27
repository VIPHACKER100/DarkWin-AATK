import Link from "next/link";

export default function NotFound() {
  return (
    <div className="h-screen w-full flex items-center justify-center p-6 bg-slate-950 font-mono text-center">
      <div className="max-w-md w-full p-6 rounded-2xl bg-slate-900/80 border border-slate-800 space-y-4">
        <h1 className="text-3xl font-extrabold text-blue-400">404</h1>
        <h2 className="text-base font-bold text-white">Target Not Found</h2>
        <p className="text-xs text-slate-400">
          The requested dashboard view or route does not exist.
        </p>
        <Link
          href="/"
          className="inline-block px-4 py-2 rounded-xl bg-blue-600 hover:bg-blue-500 text-white text-xs font-semibold tracking-wide transition-all shadow-lg shadow-blue-600/30"
        >
          Return to Control Center
        </Link>
      </div>
    </div>
  );
}
