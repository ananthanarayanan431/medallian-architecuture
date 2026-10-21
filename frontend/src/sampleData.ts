const PRODUCTS = ["Widget", "Gadget", "Gizmo", "Doohickey"];
const STATUSES = ["placed", "shipped", "delivered", "cancelled"];

/** Generates raw orders, including a few deliberately bad ones to exercise silver validation. */
export function sampleOrders(count = 50): Record<string, unknown>[] {
  return Array.from({ length: count }, (_, i) => {
    const daysAgo = Math.floor(Math.random() * 7);
    const ts = new Date(Date.now() - daysAgo * 86_400_000).toISOString();
    const order: Record<string, unknown> = {
      order_id: `o-${crypto.randomUUID().slice(0, 8)}`,
      customer_id: `c-${Math.ceil(Math.random() * 20)}`,
      product: PRODUCTS[i % PRODUCTS.length],
      quantity: 1 + Math.floor(Math.random() * 5),
      unit_price: +(5 + Math.random() * 45).toFixed(2),
      status: STATUSES[Math.floor(Math.random() * STATUSES.length)],
      order_ts: ts,
    };
    if (i % 17 === 0) order.status = "lost-in-transit";
    return order;
  });
}
