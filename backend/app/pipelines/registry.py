from collections.abc import Callable

from app.pipelines import bronze_to_silver, silver_to_gold
from app.pipelines.runs import RunStats

PIPELINES: dict[str, Callable[[], RunStats]] = {
    "bronze_to_silver": bronze_to_silver.run,
    "silver_to_gold": silver_to_gold.run,
}
