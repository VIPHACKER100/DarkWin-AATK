"use client";

import { cn } from "@/lib/utils";

interface SectionLabelProps {
  children: string;
  className?: string;
  pulse?: boolean;
}

export function SectionLabel({ children, className, pulse = true }: SectionLabelProps) {
  return (
    <div className={cn("inline-flex items-center gap-3 rounded-full border border-[var(--accent)]/30 bg-[var(--accent)]/5 px-5 py-2", className)}>
      <span
        className={cn(
          "h-2 w-2 rounded-full bg-[var(--accent)]",
          pulse && "animate-pulse"
        )}
      />
      <span className="font-mono-label text-xs uppercase tracking-[0.15em] text-[var(--accent)]">
        {children}
      </span>
    </div>
  );
}
