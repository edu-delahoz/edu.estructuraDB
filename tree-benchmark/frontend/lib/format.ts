import { DATASET_LABELS, OPERATION_LABELS, STRUCTURE_LABELS } from "@/lib/constants";
import type { DatasetMode, Operation, Structure } from "@/types/results";

const decimalFormatter = new Intl.NumberFormat("es-CO", {
  minimumFractionDigits: 0,
  maximumFractionDigits: 2,
});

const integerFormatter = new Intl.NumberFormat("es-CO", {
  maximumFractionDigits: 0,
});

export function nsToMilliseconds(value: number): number {
  return value / 1_000_000;
}

export function formatDuration(ns: number): string {
  if (!Number.isFinite(ns)) {
    return "-";
  }
  const ms = nsToMilliseconds(ns);
  if (ms >= 1000) {
    return `${decimalFormatter.format(ms / 1000)} s`;
  }
  if (ms >= 1) {
    return `${decimalFormatter.format(ms)} ms`;
  }
  return `${decimalFormatter.format(ms * 1000)} µs`;
}

export function formatNumber(value: number, options?: Intl.NumberFormatOptions): string {
  const formatter = new Intl.NumberFormat("es-CO", {
    minimumFractionDigits: 0,
    maximumFractionDigits: 2,
    ...options,
  });
  return formatter.format(value);
}

export function formatBatchLabel(batchSize?: number): string {
  if (!batchSize) {
    return "-";
  }
  return `${integerFormatter.format(batchSize)} registros`;
}

export function formatStructure(structure: Structure): string {
  return STRUCTURE_LABELS[structure] ?? structure.toUpperCase();
}

export function formatDataset(mode: DatasetMode): string {
  return DATASET_LABELS[mode] ?? mode;
}

export function formatOperation(operation: Operation): string {
  return OPERATION_LABELS[operation] ?? operation;
}
