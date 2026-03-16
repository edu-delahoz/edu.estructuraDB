import { EXPECTED_BATCH_SIZES } from "@/lib/constants";
import { nsToMilliseconds } from "@/lib/format";
import type {
  BenchmarkResultEntry,
  DatasetMode,
  Operation,
  Structure,
} from "@/types/results";

export interface BatchComparisonPoint {
  batch: number;
  label: string;
  abb?: number;
  bplus?: number;
  hasData: boolean;
}

export function filterResults(
  entries: BenchmarkResultEntry[],
  datasetMode: DatasetMode,
  operation: Operation
): BenchmarkResultEntry[] {
  return entries.filter(
    (entry) =>
      entry.dataset_mode === datasetMode && entry.operation === operation
  );
}

export function buildBatchComparisonData(
  entries: BenchmarkResultEntry[],
  expectedBatchSizes: number[] = EXPECTED_BATCH_SIZES
): BatchComparisonPoint[] {
  const dataMap = new Map<
    number,
    Partial<Record<Structure, BenchmarkResultEntry>>
  >();

  entries.forEach((entry) => {
    if (typeof entry.batch_size !== "number") {
      return;
    }
    const existing = dataMap.get(entry.batch_size) ?? {};
    existing[entry.structure] = entry;
    dataMap.set(entry.batch_size, existing);
  });

  const combinedSizes = Array.from(
    new Set([...expectedBatchSizes, ...dataMap.keys()])
  ).sort((a, b) => a - b);

  return combinedSizes.map((batch) => {
    const pair = dataMap.get(batch);
    return {
      batch,
      label: `Lote ${batch.toLocaleString("es-CO")}`,
      abb: pair?.abb ? nsToMilliseconds(pair.abb.average_ns) : undefined,
      bplus: pair?.bplus ? nsToMilliseconds(pair.bplus.average_ns) : undefined,
      hasData: Boolean(pair?.abb || pair?.bplus),
    };
  });
}

export function getObservedBatchSizes(entries: BenchmarkResultEntry[]): number[] {
  const sizes = new Set<number>();
  entries.forEach((entry) => {
    if (typeof entry.batch_size === "number") {
      sizes.add(entry.batch_size);
    }
  });
  return Array.from(sizes).sort((a, b) => a - b);
}

export function getMissingBatchSizes(
  observed: number[],
  expected: number[] = EXPECTED_BATCH_SIZES
): number[] {
  return expected.filter((size) => !observed.includes(size));
}

interface FindCriteria {
  structure: Structure;
  datasetMode: DatasetMode;
  operation: Operation;
  batchSize?: number;
}

export function findResult(
  entries: BenchmarkResultEntry[],
  criteria: FindCriteria
): BenchmarkResultEntry | undefined {
  return entries.find((entry) => {
    const matchesBatch =
      criteria.batchSize === undefined
        ? entry.batch_size === undefined
        : entry.batch_size === criteria.batchSize;
    return (
      entry.structure === criteria.structure &&
      entry.dataset_mode === criteria.datasetMode &&
      entry.operation === criteria.operation &&
      matchesBatch
    );
  });
}

export interface SpeedupSummary {
  datasetMode: DatasetMode;
  operation: Operation;
  batchSize?: number;
  faster: Structure;
  slower: Structure;
  ratio: number;
}

export function computeSpeedup(
  entries: BenchmarkResultEntry[],
  datasetMode: DatasetMode,
  operation: Operation,
  batchSize?: number
): SpeedupSummary | null {
  const abb = findResult(entries, {
    structure: "abb",
    datasetMode,
    operation,
    batchSize,
  });
  const bplus = findResult(entries, {
    structure: "bplus",
    datasetMode,
    operation,
    batchSize,
  });

  if (!abb || !bplus) {
    return null;
  }

  const faster = abb.average_ns < bplus.average_ns ? "abb" : "bplus";
  const slower = faster === "abb" ? "bplus" : "abb";
  const fastEntry = faster === "abb" ? abb : bplus;
  const slowEntry = slower === "abb" ? abb : bplus;

  return {
    datasetMode,
    operation,
    batchSize,
    faster,
    slower,
    ratio: slowEntry.average_ns / fastEntry.average_ns,
  };
}
