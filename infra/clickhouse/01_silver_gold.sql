-- SILVER: cleaned, typed, deduplicated (latest load wins per order_id).
CREATE DATABASE IF NOT EXISTS silver;

CREATE TABLE IF NOT EXISTS silver.orders
(
    order_id    String,
    customer_id String,
    product     LowCardinality(String),
    quantity    UInt32,
    unit_price  Decimal(12, 2),
    amount      Decimal(14, 2),
    status      LowCardinality(String),
    order_ts    DateTime64(3, 'UTC'),
    bronze_id   UInt64,
    _loaded_at  DateTime64(3, 'UTC') DEFAULT now64(3)
)
ENGINE = ReplacingMergeTree(_loaded_at)
PARTITION BY toYYYYMM(order_ts)
ORDER BY order_id;

-- GOLD: business-level aggregates, rebuilt from silver.
CREATE DATABASE IF NOT EXISTS gold;

CREATE TABLE IF NOT EXISTS gold.daily_revenue
(
    day          Date,
    product      LowCardinality(String),
    orders       UInt64,
    units        UInt64,
    revenue      Decimal(18, 2),
    _computed_at DateTime64(3, 'UTC') DEFAULT now64(3)
)
ENGINE = ReplacingMergeTree(_computed_at)
ORDER BY (day, product);
