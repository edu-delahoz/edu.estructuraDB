import type { DatasetMode, Operation, Structure } from "@/types/results";

export const STRUCTURE_LABELS: Record<Structure, string> = {
  abb: "ABB",
  bplus: "B+ Tree",
};

export const DATASET_LABELS: Record<DatasetMode, string> = {
  ordered: "IDs ordenados",
  random: "IDs aleatorios",
};

export const OPERATION_LABELS: Record<Operation, string> = {
  build: "Construcción",
  exact_search: "Búsqueda exacta",
  range_search: "Búsqueda por rango",
};

export const EXPECTED_BATCH_SIZES = [100, 1_000, 2_000, 5_000];
