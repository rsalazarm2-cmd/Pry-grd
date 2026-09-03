"""DTOs Pydantic para la Capa Oro (Datamarts Multidimensionales y Balances).

Define los contratos para los balances por libro/ledger (CU-11), balances por cuenta PyG (CU-12),
métricas de integridad contable (CU-13) y resultado global de generación de datamarts.
"""

from typing import List, Optional
from pydantic import BaseModel, Field


class LedgerBalanceItemDTO(BaseModel):
    """Fila de balance acumulado por libro contable (Ledger)."""

    ledger_name: str
    total_debit: float = 0.0
    total_credit: float = 0.0
    imbalance_amount: float = 0.0
    is_balanced: bool = True


class AccountBalanceItemDTO(BaseModel):
    """Fila de balance por cuenta natural / combinación contable."""

    account_code: str
    account_name: Optional[str] = "CUENTA_CONTABLE"
    total_debit: float = 0.0
    total_credit: float = 0.0
    net_balance: float = 0.0


class GoldIntegritySummaryDTO(BaseModel):
    """CU-13: Resumen global de la ecuación fundamental contable."""

    total_debit: float = 0.0
    total_credit: float = 0.0
    global_imbalance: float = 0.0
    is_globally_balanced: bool = True
    imbalanced_entries_count: int = 0
    imbalanced_entries_amount: float = 0.0
    total_journals_count: int = 0


class GoldDatamartResultDTO(BaseModel):
    """Resultado de la generación de la Capa Oro."""

    status: str = "success"
    ledger_model_path: str = ""
    account_model_path: str = ""
    ledger_rows_count: int = 0
    account_rows_count: int = 0
    integrity: GoldIntegritySummaryDTO = Field(default_factory=GoldIntegritySummaryDTO)
    execution_time_seconds: float = 0.0
