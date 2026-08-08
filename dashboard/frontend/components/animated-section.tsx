"use client";

import type { ReactNode } from "react";

export function AnimatedSection({ children, className, delay = 0 }: { children: ReactNode; className?: string; delay?: number }) {
  return (
    <div className={`animate-fade-up ${className || ""}`} style={{ animationDelay: `${delay}s` }}>
      {children}
    </div>
  );
}

export function StaggerContainer({ children, className }: { children: ReactNode; className?: string }) {
  return <div className={className}>{children}</div>;
}

export function StaggerItem({ children, className }: { children: ReactNode; className?: string }) {
  return <div className={`animate-fade-up ${className || ""}`} style={{ animationDelay: `${0.08 * 0}s` }}>{children}</div>;
}
