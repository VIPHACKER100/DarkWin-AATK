"use client";

import { forwardRef, type ButtonHTMLAttributes, type ReactNode } from "react";
import { cn } from "@/lib/utils";

interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: "primary" | "secondary" | "ghost" | "danger";
  size?: "sm" | "md" | "lg";
}

export const Button = forwardRef<HTMLButtonElement, ButtonProps>(
  ({ className, variant = "primary", size = "md", children, ...props }, ref) => {
    const base = "inline-flex items-center justify-center gap-2 font-medium rounded-xl transition-all duration-200 focus-visible:!outline-offset-2 active:scale-[0.98] disabled:opacity-40 disabled:pointer-events-none group";

    const variants: Record<string, string> = {
      primary: "bg-gradient-to-r from-[var(--accent)] to-[#4D7CFF] text-white shadow-sm hover:shadow-[var(--shadow-accent)] hover:-translate-y-0.5 hover:brightness-110",
      secondary: "bg-transparent border border-[var(--border)] text-[var(--foreground)] hover:bg-[var(--muted)] hover:border-[var(--accent)]/30 hover:shadow-sm",
      ghost: "bg-transparent text-[var(--muted-foreground)] hover:text-[var(--foreground)] hover:bg-[var(--muted)]",
      danger: "bg-gradient-to-r from-red-600 to-red-500 text-white shadow-sm hover:shadow-[0_4px_14px_rgba(220,38,38,0.25)] hover:-translate-y-0.5",
    };

    const sizes: Record<string, string> = {
      sm: "h-9 px-3 text-xs rounded-lg",
      md: "h-11 px-5 text-sm",
      lg: "h-14 px-7 text-base",
    };

    return (
      <button ref={ref} className={cn(base, variants[variant], sizes[size], className)} {...props}>
        {children}
      </button>
    );
  }
);
Button.displayName = "Button";
