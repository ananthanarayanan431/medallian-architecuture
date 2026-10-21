"""Pure bronze -> silver transformations. No I/O here so they're easy to unit test."""

from datetime import UTC, datetime
from decimal import Decimal
from typing import Any

from app.schemas import SilverOrder

VALID_STATUSES = {"placed", "shipped", "delivered", "cancelled"}


def clean_order(bronze_id: int, payload: dict[str, Any]) -> SilverOrder:
    """Normalise a raw order payload. Raises ValueError on unrecoverable records."""
    status = str(payload.get("status", "placed")).strip().lower()
    if status not in VALID_STATUSES:
        raise ValueError(f"unknown status {status!r}")

    quantity = int(payload["quantity"])
    unit_price = Decimal(str(payload["unit_price"])).quantize(Decimal("0.01"))

    order_ts = datetime.fromisoformat(str(payload["order_ts"]))
    if order_ts.tzinfo is None:
        order_ts = order_ts.replace(tzinfo=UTC)

    return SilverOrder(
        order_id=str(payload["order_id"]).strip(),
        customer_id=str(payload["customer_id"]).strip(),
        product=str(payload["product"]).strip().lower(),
        quantity=quantity,
        unit_price=unit_price,
        amount=unit_price * quantity,
        status=status,
        order_ts=order_ts.astimezone(UTC),
        bronze_id=bronze_id,
    )
