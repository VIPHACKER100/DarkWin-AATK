import type { HTMLAttributes } from "react";
import { cn } from "@/lib/utils";

interface CardProps extends HTMLAttributes<HTMLDivElement> {
  elevated?: boolean;
  featured?: boolean;
}

export function Card({ className, elevated, featured, children, ...props }: CardProps) {
  const shared = "rounded-xl border transition-all duration-300 group";
  const hover = "hover:shadow-xl hover:-translate-y-0.5";

  if (featured) {
    return (
      <div
        className={cn(
          "relative rounded-xl bg-gradient-to-br from-[var(--accent)] via-[var(--accent-secondary)] to-[var(--accent)] p-[2px] shadow-[var(--shadow-accent-lg)]",
          className
        )}
        {...props}
      >
        <div className={cn(shared, "h-full w-full rounded-[calc(0.75rem-2px)] bg-[var(--card)] border-0", hover)}>
          <div className="absolute inset-0 rounded-[calc(0.75rem-2px)] bg-gradient-to-br from-[var(--accent)]/[0.03] to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-300 pointer-events-none" />
          {children}
        </div>
      </div>
    );
  }

  return (
    <div
      className={cn(
        shared,
        "border-[var(--border)] bg-[var(--card)] shadow-md",
        elevated && hover,
        className
      )}
      {...props}
    >
      {elevated && (
        <div className="absolute inset-0 rounded-xl bg-gradient-to-br from-[var(--accent)]/[0.03] to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-300 pointer-events-none" />
      )}
      {children}
    </div>
  );
}

export function CardHeader({ className, ...props }: HTMLAttributes<HTMLDivElement>) {
  return <div className={cn("px-6 pt-6 pb-0", className)} {...props} />;
}

export function CardContent({ className, ...props }: HTMLAttributes<HTMLDivElement>) {
  return <div className={cn("p-6", className)} {...props} />;
}
