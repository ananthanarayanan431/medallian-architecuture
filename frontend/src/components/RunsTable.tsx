import type { PipelineRun } from "../api";

export function RunsTable({ runs }: { runs: PipelineRun[] }) {
  return (
    <table>
      <thead>
        <tr>
          <th>#</th>
          <th>Pipeline</th>
          <th>Status</th>
          <th>Processed</th>
          <th>Failed</th>
          <th>Started</th>
        </tr>
      </thead>
      <tbody>
        {runs.map((r) => (
          <tr key={r.id} title={r.error ?? undefined}>
            <td>{r.id}</td>
            <td>{r.pipeline}</td>
            <td className={`status-${r.status}`}>{r.status}</td>
            <td>{r.rows_processed}</td>
            <td>{r.rows_failed}</td>
            <td>{new Date(r.started_at).toLocaleString()}</td>
          </tr>
        ))}
        {runs.length === 0 && (
          <tr>
            <td colSpan={6} className="empty">No runs yet</td>
          </tr>
        )}
      </tbody>
    </table>
  );
}
