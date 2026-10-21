import type { DailyRevenue } from "../api";

export function GoldTable({ rows }: { rows: DailyRevenue[] }) {
  return (
    <table>
      <thead>
        <tr>
          <th>Day</th>
          <th>Product</th>
          <th>Orders</th>
          <th>Units</th>
          <th>Revenue</th>
        </tr>
      </thead>
      <tbody>
        {rows.map((r) => (
          <tr key={`${r.day}-${r.product}`}>
            <td>{r.day}</td>
            <td>{r.product}</td>
            <td>{r.orders}</td>
            <td>{r.units}</td>
            <td>{r.revenue.toFixed(2)}</td>
          </tr>
        ))}
        {rows.length === 0 && (
          <tr>
            <td colSpan={5} className="empty">Run silver → gold to populate</td>
          </tr>
        )}
      </tbody>
    </table>
  );
}
