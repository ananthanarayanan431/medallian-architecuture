import type { LayerSummary } from "../api";

export function LayerCards({ summary }: { summary: LayerSummary | null }) {
  const layers = [
    {
      key: "bronze",
      title: "Bronze",
      store: "Postgres · bronze.raw_orders",
      value: summary?.bronze_total,
      detail: summary && `${summary.bronze_pending} pending · ${summary.bronze_failed} failed`,
    },
    {
      key: "silver",
      title: "Silver",
      store: "ClickHouse · silver.orders",
      value: summary?.silver_rows,
      detail: "cleaned, typed, deduplicated",
    },
    {
      key: "gold",
      title: "Gold",
      store: "ClickHouse · gold.daily_revenue",
      value: summary?.gold_rows,
      detail: "business aggregates",
    },
  ];

  return (
    <div className="cards">
      {layers.map((l) => (
        <div key={l.key} className={`card card-${l.key}`}>
          <h2>{l.title}</h2>
          <div className="store">{l.store}</div>
          <div className="value">{l.value ?? "—"}</div>
          <div className="detail">{l.detail}</div>
        </div>
      ))}
    </div>
  );
}
