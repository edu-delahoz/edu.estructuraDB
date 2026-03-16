import type { ReactNode } from "react";

export interface TableColumn {
  key: string;
  label: string;
  align?: "left" | "center" | "right";
}

export interface TableRow {
  id: string;
  data: Record<string, ReactNode>;
}

interface MetricTableProps {
  title?: string;
  description?: string;
  columns: TableColumn[];
  rows: TableRow[];
  footnote?: string;
}

const ALIGN_CLASS: Record<NonNullable<TableColumn["align"]>, string> = {
  left: "text-left",
  center: "text-center",
  right: "text-right",
};

export function MetricTable({
  title,
  description,
  columns,
  rows,
  footnote,
}: MetricTableProps) {
  return (
    <section className="rounded-2xl border border-slate-200 bg-white/90 shadow-sm dark:border-slate-800 dark:bg-slate-900/80">
      <div className="px-6 py-5">
        {title && (
          <h3 className="text-lg font-semibold text-slate-900 dark:text-white">
            {title}
          </h3>
        )}
        {description && (
          <p className="mt-1 text-sm text-slate-500 dark:text-slate-400">
            {description}
          </p>
        )}
      </div>
      <div className="overflow-x-auto">
        <table className="w-full min-w-max text-left text-sm text-slate-600 dark:text-slate-300">
          <thead className="text-xs uppercase tracking-wide text-slate-500 dark:text-slate-400">
            <tr>
              {columns.map((column) => (
                <th
                  key={column.key}
                  scope="col"
                  className={`px-4 py-3 font-semibold ${ALIGN_CLASS[column.align ?? "left"]}`}
                >
                  {column.label}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {rows.length === 0 && (
              <tr>
                <td
                  colSpan={columns.length}
                  className="px-4 py-6 text-center text-sm text-slate-500 dark:text-slate-400"
                >
                  Sin datos para esta combinación.
                </td>
              </tr>
            )}
            {rows.map((row) => (
              <tr
                key={row.id}
                className="border-t border-slate-100 last:border-b dark:border-slate-800"
              >
                {columns.map((column) => (
                  <td
                    key={`${row.id}-${column.key}`}
                    className={`px-4 py-3 ${ALIGN_CLASS[column.align ?? "left"]}`}
                  >
                    {row.data[column.key] ?? "-"}
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      {footnote && (
        <div className="border-t border-slate-100 px-6 py-3 text-xs text-slate-500 dark:border-slate-800 dark:text-slate-400">
          {footnote}
        </div>
      )}
    </section>
  );
}
