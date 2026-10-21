import { useCallback, useEffect, useState } from "react";
import { api, type DailyRevenue, type LayerSummary, type PipelineRun } from "./api";
import { GoldTable } from "./components/GoldTable";
import { LayerCards } from "./components/LayerCards";
import { RunsTable } from "./components/RunsTable";
import { sampleOrders } from "./sampleData";

export default function App() {
  const [summary, setSummary] = useState<LayerSummary | null>(null);
  const [runs, setRuns] = useState<PipelineRun[]>([]);
  const [gold, setGold] = useState<DailyRevenue[]>([]);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const refresh = useCallback(async () => {
    try {
      const [s, r, g] = await Promise.all([api.summary(), api.runs(), api.dailyRevenue()]);
      setSummary(s);
      setRuns(r);
      setGold(g);
      setError(null);
    } catch (e) {
      setError(String(e));
    }
  }, []);

  useEffect(() => {
    refresh();
  }, [refresh]);

  const act = (fn: () => Promise<unknown>) => async () => {
    setBusy(true);
    try {
      await fn();
    } catch (e) {
      setError(String(e));
    } finally {
      setBusy(false);
      refresh();
    }
  };

  return (
    <main>
      <header>
        <h1>Medallion Console</h1>
        <p>Postgres (bronze) → ClickHouse (silver, gold)</p>
      </header>

      {error && <div className="error">{error}</div>}

      <LayerCards summary={summary} />

      <section className="actions">
        <button disabled={busy} onClick={act(() => api.ingest(sampleOrders()))}>
          Seed 50 raw orders
        </button>
        <button disabled={busy} onClick={act(() => api.runPipeline("bronze_to_silver"))}>
          Run bronze → silver
        </button>
        <button disabled={busy} onClick={act(() => api.runPipeline("silver_to_gold"))}>
          Run silver → gold
        </button>
        <button disabled={busy} onClick={refresh} className="secondary">
          Refresh
        </button>
      </section>

      <section>
        <h2>Gold · daily revenue</h2>
        <GoldTable rows={gold} />
      </section>

      <section>
        <h2>Pipeline runs</h2>
        <RunsTable runs={runs} />
      </section>
    </main>
  );
}
