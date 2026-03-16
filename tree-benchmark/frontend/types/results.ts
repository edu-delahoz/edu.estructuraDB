export type Structure = "abb" | "bplus";
export type DatasetMode = "ordered" | "random";
export type Operation = "build" | "exact_search" | "range_search";

export interface BenchmarkMetadata {
  seed: number;
  repeats: number;
  warmup_repeats: number;
  search_batch_sizes: number[];
  range_window_ids: number;
  notes?: string[];
}

export interface BenchmarkResultEntry {
  structure: Structure;
  dataset_mode: DatasetMode;
  operation: Operation;
  repeats: number;
  average_ns: number;
  median_ns: number;
  min_ns: number;
  max_ns: number;
  stddev_ns: number;
  batch_size?: number;
}

export interface BenchmarkFile {
  metadata: BenchmarkMetadata;
  results: BenchmarkResultEntry[];
}
