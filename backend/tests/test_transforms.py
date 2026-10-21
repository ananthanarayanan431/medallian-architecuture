from decimal import Decimal

import pytest

from app.pipelines.transforms import clean_order

RAW = {
    "order_id": " o-1 ",
    "customer_id": "c-1",
    "product": " Widget ",
    "quantity": "3",
    "unit_price": 9.999,
    "status": "SHIPPED",
    "order_ts": "2026-10-01T12:00:00Z",
}


def test_clean_order_normalises_fields():
    order = clean_order(42, RAW)
    assert order.order_id == "o-1"
    assert order.product == "widget"
    assert order.status == "shipped"
    assert order.quantity == 3
    assert order.unit_price == Decimal("10.00")
    assert order.amount == Decimal("30.00")
    assert order.order_ts.utcoffset().total_seconds() == 0
    assert order.bronze_id == 42


def test_clean_order_rejects_unknown_status():
    with pytest.raises(ValueError, match="unknown status"):
        clean_order(1, {**RAW, "status": "lost"})


def test_clean_order_rejects_missing_field():
    payload = {k: v for k, v in RAW.items() if k != "product"}
    with pytest.raises(KeyError):
        clean_order(1, payload)
