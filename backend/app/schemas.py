from datetime import datetime
from decimal import Decimal
from typing import Any

from pydantic import BaseModel, Field


class BronzeIngest(BaseModel):
    source: str = "api"
    records: list[dict[str, Any]] = Field(min_length=1)


class SilverOrder(BaseModel):
    order_id: str
    customer_id: str
    product: str
    quantity: int = Field(gt=0)
    unit_price: Decimal = Field(ge=0)
    amount: Decimal
    status: str
    order_ts: datetime
    bronze_id: int


class LayerSummary(BaseModel):
    bronze_total: int
    bronze_pending: int
    bronze_failed: int
    silver_rows: int
    gold_rows: int


class PipelineRun(BaseModel):
    id: int
    pipeline: str
    status: str
    rows_processed: int
    rows_failed: int
    started_at: datetime
    finished_at: datetime | None
    error: str | None


class DailyRevenue(BaseModel):
    day: str
    product: str
    orders: int
    units: int
    revenue: float
