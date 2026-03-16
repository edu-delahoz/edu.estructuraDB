import clsx from "clsx";

import { BatchComparisonChart } from "@/components/charts/BatchComparisonChart";
import { StatCard } from "@/components/cards/StatCard";
import {
  MetricTable,
  type TableColumn,
  type TableRow,
} from "@/components/tables/MetricTable";
import {
  DATASET_LABELS,
  EXPECTED_BATCH_SIZES,
  OPERATION_LABELS,
  STRUCTURE_LABELS,
} from "@/lib/constants";
import {
  formatDataset,
  formatDuration,
  formatNumber,
  formatOperation,
  formatStructure,
} from "@/lib/format";
import { loadBenchmarkResults } from "@/lib/loadResults";
import {
  buildBatchComparisonData,
  computeSpeedup,
  filterResults,
  getMissingBatchSizes,
  getObservedBatchSizes,
  type SpeedupSummary,
} from "@/lib/transform";
import type { BenchmarkResultEntry, DatasetMode } from "@/types/results";

const durationColumns: TableColumn[] = [
  { key: "average", label: "Promedio", align: "right" },
  { key: "median", label: "Mediana", align: "right" },
  { key: "min", label: "Mínimo", align: "right" },
  { key: "max", label: "Máximo", align: "right" },
  { key: "stddev", label: "Desv. Est.", align: "right" },
];

const buildColumns: TableColumn[] = [
  { key: "structure", label: "Estructura" },
  ...durationColumns,
];

const batchColumns: TableColumn[] = [
  { key: "batch", label: "Tamaño de lote" },
  { key: "structure", label: "Estructura" },
  ...durationColumns,
];

function toTableRows(
  entries: BenchmarkResultEntry[],
  includeBatch = false
): TableRow[] {
  const sorted = [...entries].sort((a, b) => {
    if (includeBatch) {
      const diff = (a.batch_size ?? 0) - (b.batch_size ?? 0);
      if (diff !== 0) {
        return diff;
      }
    }
    return a.structure.localeCompare(b.structure);
  });

  return sorted.map((entry) => ({
    id: `${entry.dataset_mode}-${entry.operation}-${entry.structure}-${entry.batch_size ?? 0}`,
    data: {
      ...(includeBatch && {
        batch: entry.batch_size
          ? `${formatNumber(entry.batch_size, { maximumFractionDigits: 0 })}`
          : "-",
      }),
      structure: formatStructure(entry.structure),
      average: formatDuration(entry.average_ns),
      median: formatDuration(entry.median_ns),
      min: formatDuration(entry.min_ns),
      max: formatDuration(entry.max_ns),
      stddev: formatDuration(entry.stddev_ns),
    },
  }));
}

function describeSpeedup(summary: SpeedupSummary): string {
  const datasetLabel = formatDataset(summary.datasetMode).toLowerCase();
  const operationLabel = formatOperation(summary.operation).toLowerCase();
  const faster = STRUCTURE_LABELS[summary.faster];
  const slower = STRUCTURE_LABELS[summary.slower];
  const ratio = formatNumber(summary.ratio, { maximumFractionDigits: 1 });
  const batchSuffix = summary.batchSize
    ? ` (lote ${formatNumber(summary.batchSize, { maximumFractionDigits: 0 })})`
    : "";
  return `${faster} es ${ratio}x más rápido que ${slower} en ${operationLabel} (${datasetLabel}${batchSuffix}).`;
}

export default async function BenchmarkDashboard() {
  const { metadata, results } = await loadBenchmarkResults();
  const datasetModes: DatasetMode[] = ["ordered", "random"];
  const observedBatchSizes = getObservedBatchSizes(results);
  const missingBatchSizes = getMissingBatchSizes(observedBatchSizes);

  const summaryCards = [
    {
      title: "Semilla",
      value: `#${metadata.seed}`,
      description: "Reproducibilidad del dataset",
      accent: "primary" as const,
    },
    {
      title: "Repeticiones",
      value: `${metadata.repeats} + ${metadata.warmup_repeats} calentamiento`,
      description: "Promedios por punto de medición",
      accent: "secondary" as const,
    },
    {
      title: "Operaciones",
      value: `${new Set(results.map((r) => r.operation)).size} métricas`,
      description: "build / exact / range",
      accent: "neutral" as const,
    },
    {
      title: "Lotes medidos",
      value: observedBatchSizes
        .map((size) => formatNumber(size, { maximumFractionDigits: 0 }))
        .join("  -  ") || "N/D",
      description: "El panel resalta lotes faltantes",
      accent: "neutral" as const,
    },
  ];

  const speedups = [
    computeSpeedup(results, "ordered", "build"),
    computeSpeedup(results, "random", "build"),
    computeSpeedup(results, "ordered", "exact_search", 1000),
    computeSpeedup(results, "random", "exact_search", 100),
  ].filter(Boolean) as SpeedupSummary[];

  const datasetSections = datasetModes.map((mode) => {
    const buildEntries = filterResults(results, mode, "build");
    const exactEntries = filterResults(results, mode, "exact_search");
    const rangeEntries = filterResults(results, mode, "range_search");

    return {
      mode,
      label: DATASET_LABELS[mode],
      buildEntries,
      exactEntries,
      rangeEntries,
      exactChart: buildBatchComparisonData(exactEntries, EXPECTED_BATCH_SIZES),
      rangeChart: buildBatchComparisonData(rangeEntries, [metadata.range_window_ids]),
    };
  });

  const notes = metadata.notes ?? [];

  return (
    <main className="min-h-screen bg-slate-50 pb-16 text-slate-900">
      <div className="mx-auto max-w-6xl px-4 py-10 sm:px-6 lg:px-8 lg:py-14">
        <header>
          <p className="text-sm font-semibold uppercase tracking-widest text-slate-500">
            Fase 6  -  Visualización de benchmark
          </p>
          <h1 className="mt-2 text-3xl font-bold tracking-tight text-slate-900 lg:text-4xl">
            ABB vs B+ Tree - Panel de resultados
          </h1>
          <p className="mt-4 text-base text-slate-600 lg:text-lg">
            El backend generó <code className="rounded bg-slate-200 px-1 py-0.5 text-xs">results.json</code> y
            esta vista lo consume directamente para presentar métricas de construcción, búsqueda exacta y de rango
            bajo diferentes patrones de IDs.
          </p>
        </header>

        <section className="mt-8 grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
          {summaryCards.map((card) => (
            <StatCard
              key={card.title}
              title={card.title}
              value={card.value}
              description={card.description}
              accent={card.accent}
            />
          ))}
        </section>

        <section className="mt-8 rounded-3xl border border-slate-200 bg-white/90 p-6 shadow-sm">
          <h2 className="text-xl font-semibold text-slate-900">Cobertura de lotes evaluados</h2>
          <p className="mt-1 text-sm text-slate-600">
            El backend define cuatro tamaños objetivo (100, 1k, 2k, 5k). El panel muestra cuáles ya cuentan con mediciones.
          </p>
          <div className="mt-4 flex flex-wrap gap-3">
            {EXPECTED_BATCH_SIZES.map((size) => {
              const missing = missingBatchSizes.includes(size);
              return (
                <span
                  key={size}
                  className={clsx(
                    "rounded-full px-4 py-1 text-xs font-semibold",
                    missing
                      ? "bg-rose-100 text-rose-700"
                      : "bg-emerald-100 text-emerald-700"
                  )}
                >
                  Lote {formatNumber(size, { maximumFractionDigits: 0 })} {missing ? " -  pendiente" : " -  ok"}
                </span>
              );
            })}
          </div>
          {missingBatchSizes.length > 0 && (
            <p className="mt-3 text-sm text-rose-700">
              Faltan mediciones para los lotes: {" "}
              {missingBatchSizes
                .map((size) => formatNumber(size, { maximumFractionDigits: 0 }))
                .join(", ")}
              .
            </p>
          )}
        </section>

        <div className="mt-10 space-y-10">
          {datasetSections.map((section) => (
            <section key={section.mode} className="rounded-3xl border border-slate-200 bg-white/95 p-6 shadow-sm">
              <header className="flex flex-col gap-2 lg:flex-row lg:items-center lg:justify-between">
                <div>
                  <p className="text-sm font-semibold uppercase tracking-wide text-slate-500">
                    {section.label}
                  </p>
                  <h2 className="text-2xl font-bold text-slate-900">Comparativa completa</h2>
                </div>
                <p className="text-sm text-slate-500 lg:max-w-sm">
                  {section.mode === "ordered"
                    ? "IDs consecutivos exponen los peores casos de inserción para ABB; B+ Tree mantiene estabilidad al balancear páginas."
                    : "IDs aleatorios evitan degradación de ABB y muestran diferencias más cerradas, especialmente en construcción."}
                </p>
              </header>

              <div className="mt-6 grid gap-6 lg:grid-cols-2">
                <MetricTable
                  title="Construcción"
                  description="Tiempo para crear la estructura a partir del CSV."
                  columns={buildColumns}
                  rows={toTableRows(section.buildEntries)}
                />
                <div className="grid gap-4">
                  {section.buildEntries.map((entry) => {
                    const cardKey = `${section.mode}-build-${entry.structure}`;
                    const cardTitle = `${formatStructure(entry.structure)} - ${OPERATION_LABELS.build}`;
                    const cardDescription = `Mediana ${formatDuration(
                      entry.median_ns
                    )} - Desv ${formatDuration(entry.stddev_ns)}`;
                    return (
                      <StatCard
                        key={cardKey}
                        title={cardTitle}
                        value={formatDuration(entry.average_ns)}
                        description={cardDescription}
                        accent={entry.structure === "bplus" ? "primary" : "neutral"}
                      />
                    );
                  })}
                </div>
              </div>

              <div className="mt-8 grid gap-6 lg:grid-cols-[5fr,4fr]">
                <BatchComparisonChart
                  title="Búsqueda exacta"
                  description="Comparación directa entre ABB y B+ Tree para cada tamaño de lote."
                  data={section.exactChart}
                />
                <MetricTable
                  title="Detalle de búsqueda exacta"
                  columns={batchColumns}
                  rows={toTableRows(section.exactEntries, true)}
                />
              </div>

              <div className="mt-8 grid gap-6 lg:grid-cols-[4fr,5fr]">
                <MetricTable
                  title="Búsqueda por rango"
                  description="Range search solo aplica a B+ Tree en esta implementación."
                  columns={batchColumns}
                  rows={toTableRows(section.rangeEntries, true)}
                  footnote="ABB no tiene soporte para range search en esta fase."
                />
                <BatchComparisonChart
                  title="Rendimiento de range search"
                  description="Valores en milisegundos; solo se grafican los datos disponibles."
                  data={section.rangeChart}
                  showLegend={false}
                />
              </div>
            </section>
          ))}
        </div>

        {notes.length > 0 && (
          <section className="mt-10 rounded-3xl border border-slate-200 bg-slate-900/90 p-6 text-slate-100 shadow-sm">
            <h2 className="text-xl font-semibold">Notas del experimento</h2>
            <ul className="mt-3 space-y-2 text-sm text-slate-200">
              {notes.map((note) => (
                <li key={note} className="flex gap-2">
                  <span aria-hidden className="text-slate-400">-</span>
                  <span>{note}</span>
                </li>
              ))}
            </ul>
          </section>
        )}

        <section className="mt-10 rounded-3xl border border-slate-200 bg-white/95 p-6 shadow-sm">
          <h2 className="text-2xl font-bold text-slate-900">Conclusiones</h2>
          <p className="mt-2 text-sm text-slate-600">
            Puntos clave derivados directamente de los valores de <code>results.json</code>.
          </p>
          <ul className="mt-4 space-y-3 text-sm text-slate-700">
            {speedups.map((summary) => (
              <li key={`${summary.datasetMode}-${summary.operation}-${summary.batchSize ?? "na"}`}>
                {describeSpeedup(summary)}
              </li>
            ))}
            {missingBatchSizes.length === 0 ? (
              <li>Todos los lotes solicitados cuentan con mediciones.</li>
            ) : (
              <li>
                Pendiente repetir el benchmark para lotes {" "}
                {missingBatchSizes
                  .map((size) => formatNumber(size, { maximumFractionDigits: 0 }))
                  .join(", ")}
                , lo cual completará la comparación esperada (100/1k/2k/5k).
              </li>
            )}
            <li>
              Las búsquedas por rango solo están instrumentadas en B+ Tree, por lo que cualquier análisis de ventanas debe
              interpretarse con esa restricción.
            </li>
          </ul>
        </section>
      </div>
    </main>
  );
}
