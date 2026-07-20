"use client";

import { forwardRef, type InputHTMLAttributes } from "react";
import { cn } from "@/lib/utils";

interface InputProps extends InputHTMLAttributes<HTMLInputElement> {
  label?: string;
}

export const Input = forwardRef<HTMLInputElement, InputProps>(
  ({ className, label, id, ...props }, ref) => {
    return (
      <div className="space-y-1.5">
        {label && (
          <label htmlFor={id} className="text-xs font-medium text-[var(--muted-foreground)] tracking-wide uppercase font-mono-label">
            {label}
          </label>
        )}
        <input
          ref={ref}
          id={id}
          className={cn(
            "h-12 w-full rounded-xl border border-[var(--border)] bg-transparent px-4 py-2.5 text-sm font-mono text-[var(--foreground)] placeholder:text-[var(--muted-foreground)]/50 outline-none transition-all duration-200 focus:border-[var(--accent)] focus:ring-2 focus:ring-[var(--ring)] focus:ring-offset-2 focus:ring-offset-[var(--background)] disabled:opacity-40",
            className
          )}
          {...props}
        />
      </div>
    );
  }
);
Input.displayName = "Input";
