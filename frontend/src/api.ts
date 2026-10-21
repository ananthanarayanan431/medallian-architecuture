export type LayerSummary = {
  bronze_total: number;
  bronze_pending: number;
  bronze_failed: number;
  silver_rows: number;
  gold_rows: number;
};

export type PipelineRun = {
  id: number;
  pipeline: string;
  status: string;
  rows_processed: number;
  rows_failed: number;
  started_at: string;
  finished_at: string | null;
  error: string | null;
};

export type DailyRevenue = {
  day: string;
  product: string;
  orders: number;
  units: number;
  revenue: number;
};

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`/api${path}`, {
    headers: { "Content-Type": "application/json" },
    ...init,
  });
  if (!res.ok) throw new Error(`${res.status} ${await res.text()}`);
  return res.json() as Promise<T>;
}

export const api = {
  summary: () => request<LayerSummary>("/layers/summary"),
  runs: () => request<PipelineRun[]>("/pipelines/runs"),
  dailyRevenue: () => request<DailyRevenue[]>("/gold/daily-revenue"),
  runPipeline: (name: string) => request(`/pipelines/${name}/run`, { method: "POST" }),
  ingest: (records: Record<string, unknown>[]) =>
    request<{ inserted: number }>("/bronze/orders", {
      method: "POST",
      body: JSON.stringify({ source: "ui-seed", records }),
    }),
};
