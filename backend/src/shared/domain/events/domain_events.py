from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict

@dataclass(frozen=True)
class DomainEvent:
    occurred_on: datetime = field(default_factory=datetime.now)

@dataclass(frozen=True)
class BronzeIngestedEvent(DomainEvent):
    project_id: str = ""
    target_parquet_path: str = ""
    rows_ingested: int = 0
    file_hash: str = ""

@dataclass(frozen=True)
class SilverTransformedEvent(DomainEvent):
    project_id: str = ""
    target_silver_path: str = ""
    rows_transformed: int = 0

@dataclass(frozen=True)
class GoldBalancesGeneratedEvent(DomainEvent):
    project_id: str = ""
    ledger_rows: int = 0
    account_rows: int = 0
