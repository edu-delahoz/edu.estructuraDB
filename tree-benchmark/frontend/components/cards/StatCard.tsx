import type { ReactNode } from "react";
import clsx from "clsx";

interface StatCardProps {
  title: string;
  value: string;
  description?: string;
  icon?: ReactNode;
  accent?: "primary" | "secondary" | "neutral";
}

const ACCENT_STYLES: Record<NonNullable<StatCardProps["accent"]>, string> = {
  primary: "bg-sky-100 text-sky-800 dark:bg-sky-900/40 dark:text-sky-100",
  secondary:
    "bg-emerald-100 text-emerald-800 dark:bg-emerald-900/30 dark:text-emerald-50",
  neutral: "bg-slate-100 text-slate-700 dark:bg-slate-800 dark:text-slate-100",
};

export function StatCard({
  title,
  value,
  description,
  icon,
  accent = "neutral",
}: StatCardProps) {
  return (
    <article className="rounded-2xl border border-slate-200 bg-white/90 p-5 shadow-sm dark:border-slate-800 dark:bg-slate-900/80">
      <div className="flex items-start justify-between gap-4">
        <div>
          <p className="text-sm font-medium uppercase tracking-wide text-slate-500 dark:text-slate-400">
            {title}
          </p>
          <p className="mt-2 text-2xl font-semibold text-slate-900 dark:text-white">
            {value}
          </p>
        </div>
        {icon && (
          <span
            className={clsx(
              "inline-flex h-10 w-10 items-center justify-center rounded-xl text-lg font-semibold",
              ACCENT_STYLES[accent]
            )}
          >
            {icon}
          </span>
        )}
      </div>
      {description && (
        <p className="mt-3 text-sm text-slate-500 dark:text-slate-400">
          {description}
        </p>
      )}
    </article>
  );
}
