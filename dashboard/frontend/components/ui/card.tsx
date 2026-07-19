import type { HTMLAttributes } from "react";
import { cn } from "@/lib/utils";

interface CardProps extends HTMLAttributes<HTMLDivElement> {
  elevated?: boolean;
  featured?: boolean;
}

export function Card({ className, elevated, featured, children, ...props }: CardProps) {
  return (
    <div
      className={cn(
        "rounded-xl border bg-[var(--card)] transition-all duration-200",
        featured
          ? "relative bg-gradient-to-br from-[var(--accent)] via-[var(--accent-secondary)] to-[var(--accent)] p-[2px] shadow-[0_8px_24px_rgba(0,82,255,0.2)]"
          : elevated
            ? "border-[var(--border)] shadow-md hover:shadow-xl hover:-translate-y-0.5"
            : "border-[var(--border)] shadow-sm",
        className
      )}
      {...props}
    >
      {featured ? (
        <div className="h-full w-full rounded-[calc(0.75rem-2px)] bg-[var(--card)]">
          {children}
        </div>
      ) : children}
    </div>
  );
}

export function CardHeader({ className, ...props }: HTMLAttributes<HTMLDivElement>) {
  return <div className={cn("px-6 pt-6 pb-0", className)} {...props} />;
}

export function CardContent({ className, ...props }: HTMLAttributes<HTMLDivElement>) {
  return <div className={cn("p-6", className)} {...props} />;
}
