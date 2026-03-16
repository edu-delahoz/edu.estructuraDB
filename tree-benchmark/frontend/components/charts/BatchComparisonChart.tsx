"use client";

import type { BatchComparisonPoint } from "@/lib/transform";
import { formatNumber } from "@/lib/format";
import {
  Bar,
  BarChart,
  CartesianGrid,
  Legend,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
  type TooltipProps,
} from "recharts";

interface BatchComparisonChartProps {
  title: string;
  description?: string;
  data: BatchComparisonPoint[];
  unit?: "ms" | "s";
  showLegend?: boolean;
}

const numberFormatter = new Intl.NumberFormat("es-CO", {
  minimumFractionDigits: 0,
  maximumFractionDigits: 2,
});

type TooltipValue = string | number | (string | number)[];

export function BatchComparisonChart({
  title,
  description,
  data,
  unit = "ms",
  showLegend = true,
}: BatchComparisonChartProps) {
  const missingBatches = data.filter((point) => !point.hasData);
  const tooltipFormatter: TooltipProps<TooltipValue, string>["formatter"] = (
    value,
    name
  ) => {
    if (typeof value !== "number") {
      return ["Sin datos", name ?? ""];
    }
    return [`${numberFormatter.format(value)} ${unit}`, name ?? ""];
  };

  return (
    <section className="rounded-2xl border border-slate-200 bg-white/90 p-6 shadow-sm dark:border-slate-800 dark:bg-slate-900/80">
      <div className="mb-4">
        <h3 className="text-lg font-semibold text-slate-900 dark:text-white">
          {title}
        </h3>
        {description && (
          <p className="mt-1 text-sm text-slate-500 dark:text-slate-400">
            {description}
          </p>
        )}
      </div>
      <div className="h-80 w-full">
        <ResponsiveContainer width="100%" height="100%">
          <BarChart data={data} barGap={8}>
            <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
            <XAxis dataKey="label" tick={{ fontSize: 12 }} />
            <YAxis
              tickFormatter={(value) => `${numberFormatter.format(value)} ${unit}`}
              width={80}
            />
            <Tooltip formatter={tooltipFormatter} />
            {showLegend && <Legend />}
            <Bar dataKey="abb" name="ABB" fill="#f97316" radius={[4, 4, 0, 0]} />
            <Bar
              dataKey="bplus"
              name="B+ Tree"
              fill="#0ea5e9"
              radius={[4, 4, 0, 0]}
            />
          </BarChart>
        </ResponsiveContainer>
      </div>
      {missingBatches.length > 0 && (
        <p className="mt-4 text-xs text-slate-500 dark:text-slate-400">
          Sin mediciones para los lotes: {" "}
          {missingBatches.map((point) => formatNumber(point.batch, { maximumFractionDigits: 0 })).join(
            ", "
          )}.
        </p>
      )}
    </section>
  );
}
