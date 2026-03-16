import { promises as fs } from "node:fs";
import path from "node:path";

import type { BenchmarkFile } from "@/types/results";

let cached: BenchmarkFile | null = null;

const RESULTS_PATH = path.join(
  process.cwd(),
  "..",
  "backend",
  "results",
  "results.json"
);

export async function loadBenchmarkResults(): Promise<BenchmarkFile> {
  if (cached) {
    return cached;
  }

  const fileContents = await fs.readFile(RESULTS_PATH, "utf-8");
  cached = JSON.parse(fileContents) as BenchmarkFile;
  return cached;
}
