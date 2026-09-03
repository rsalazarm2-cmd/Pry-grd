"""Motor DuckDB Vectorizado para Generación de Datamarts Oro (CU-11, CU-12, CU-13).

Agrega datos limpios de la Capa Plata para generar:
- gold_balance_by_ledger.parquet (CU-11)
- gold_balance_by_account.parquet (CU-12)
- Métricas de validación de la ecuación contable (CU-13)
"""

import logging, time
from pathlib import Path
import duckdb

from src.gold.domain.gold_models_dto import (
    GoldDatamartResultDTO,
    GoldIntegritySummaryDTO,
)

logger = logging.getLogger(__name__)


def _safe(path: Path) -> str:
    return str(path.resolve()).replace("'", "''")


def _get_cols(conn: duckdb.DuckDBPyConnection, pq: str) -> dict:
    schema = conn.execute(f"DESCRIBE SELECT * FROM read_parquet('{pq}')").fetchall()
    return {r[0].upper(): r[0] for r in schema}


class GoldDatamartEngine:
    """Motor DuckDB nativo para la Capa Oro."""

    def __init__(self, conn: duckdb.DuckDBPyConnection):
        self._conn = conn

    def generate_all_datamarts(
        self, silver_parquet_path: str, target_gold_dir: str
    ) -> GoldDatamartResultDTO:
        t0 = time.time()
        s_path = Path(silver_parquet_path).resolve()
        g_dir = Path(target_gold_dir).resolve()
        g_dir.mkdir(parents=True, exist_ok=True)

        if not s_path.exists():
            return GoldDatamartResultDTO(status="error")

        l_path = g_dir / "gold_balance_by_ledger.parquet"
        a_path = g_dir / "gold_balance_by_account.parquet"

        l_rows = self.generate_ledger_balance(s_path, l_path)
        a_rows = self.generate_account_balance(s_path, a_path)
        integrity = self.compute_integrity_summary(s_path)

        return GoldDatamartResultDTO(
            status="success",
            ledger_model_path=str(l_path),
            account_model_path=str(a_path),
            ledger_rows_count=l_rows,
            account_rows_count=a_rows,
            integrity=integrity,
            execution_time_seconds=round(time.time() - t0, 4),
        )

    def generate_ledger_balance(self, silver_path: Path, target_path: Path) -> int:
        pq = _safe(silver_path)
        cols = _get_cols(self._conn, pq)
        ledger_c = cols.get("NOMBRE_LIBRO", cols.get("LEDGER_NAME", cols.get("LIBRO", "'LIBRO_PRINCIPAL'")))
        dr_c = cols.get("CARGO_MONEDA_FUNCIONAL", cols.get("CARGO", cols.get("ENTERED_DR", "0.0")))
        cr_c = cols.get("ABONO_MONEDA_FUNCIONAL", cols.get("ABONO", cols.get("ENTERED_CR", "0.0")))

        query = f"""
            COPY (
                SELECT
                    COALESCE(CAST({ledger_c} AS VARCHAR), 'LIBRO_GENERAL') AS LEDGER_NAME,
                    COALESCE(SUM(TRY_CAST({dr_c} AS DOUBLE)), 0.0) AS TOTAL_CARGOS,
                    COALESCE(SUM(TRY_CAST({cr_c} AS DOUBLE)), 0.0) AS TOTAL_ABONOS,
                    ABS(COALESCE(SUM(TRY_CAST({dr_c} AS DOUBLE)), 0.0) - COALESCE(SUM(TRY_CAST({cr_c} AS DOUBLE)), 0.0)) AS DIFERENCIA,
                    CASE WHEN ABS(COALESCE(SUM(TRY_CAST({dr_c} AS DOUBLE)), 0.0) - COALESCE(SUM(TRY_CAST({cr_c} AS DOUBLE)), 0.0)) <= 0.01
                         THEN 'CUADRADO' ELSE 'DESCUADRADO' END AS ESTADO_CUADRE
                FROM read_parquet('{pq}')
                GROUP BY LEDGER_NAME
            ) TO '{_safe(target_path)}' (FORMAT PARQUET)
        """
        self._conn.execute(query)
        return self._conn.execute(f"SELECT COUNT(*) FROM read_parquet('{_safe(target_path)}')").fetchone()[0]

    def generate_account_balance(self, silver_path: Path, target_path: Path) -> int:
        pq = _safe(silver_path)
        cols = _get_cols(self._conn, pq)
        acct_c = cols.get("CUENTA_CONTABLE", cols.get("CODE_COMBINATION", cols.get("CUENTA", "'SIN_CUENTA'")))
        dr_c = cols.get("CARGO_MONEDA_FUNCIONAL", cols.get("CARGO", cols.get("ENTERED_DR", "0.0")))
        cr_c = cols.get("ABONO_MONEDA_FUNCIONAL", cols.get("ABONO", cols.get("ENTERED_CR", "0.0")))

        query = f"""
            COPY (
                SELECT
                    COALESCE(CAST({acct_c} AS VARCHAR), 'SIN_CUENTA') AS ACCOUNT_CODE,
                    COALESCE(SUM(TRY_CAST({dr_c} AS DOUBLE)), 0.0) AS TOTAL_CARGOS,
                    COALESCE(SUM(TRY_CAST({cr_c} AS DOUBLE)), 0.0) AS TOTAL_ABONOS,
                    (COALESCE(SUM(TRY_CAST({dr_c} AS DOUBLE)), 0.0) - COALESCE(SUM(TRY_CAST({cr_c} AS DOUBLE)), 0.0)) AS SALDO_NETO
                FROM read_parquet('{pq}')
                GROUP BY ACCOUNT_CODE
                ORDER BY TOTAL_CARGOS DESC
            ) TO '{_safe(target_path)}' (FORMAT PARQUET)
        """
        self._conn.execute(query)
        return self._conn.execute(f"SELECT COUNT(*) FROM read_parquet('{_safe(target_path)}')").fetchone()[0]

    def compute_integrity_summary(self, silver_path: Path) -> GoldIntegritySummaryDTO:
        pq = _safe(silver_path)
        cols = _get_cols(self._conn, pq)
        dr_c = cols.get("CARGO_MONEDA_FUNCIONAL", cols.get("CARGO", cols.get("ENTERED_DR", "0.0")))
        cr_c = cols.get("ABONO_MONEDA_FUNCIONAL", cols.get("ABONO", cols.get("ENTERED_CR", "0.0")))
        folio_c = cols.get("FOLIO_ASIENTO", cols.get("JE_HEADER_ID", cols.get("ASIENTO")))

        g_q = f"SELECT SUM(TRY_CAST({dr_c} AS DOUBLE)), SUM(TRY_CAST({cr_c} AS DOUBLE)) FROM read_parquet('{pq}')"
        row_g = self._conn.execute(g_q).fetchone()
        tot_dr, tot_cr = float(row_g[0] or 0.0), float(row_g[1] or 0.0)
        diff_g = abs(tot_dr - tot_cr)

        imb_count, imb_amt = 0, 0.0
        if folio_c:
            imb_q = f"""
                SELECT COUNT(*), COALESCE(SUM(diff), 0.0) FROM (
                    SELECT {folio_c}, ABS(SUM(TRY_CAST({dr_c} AS DOUBLE)) - SUM(TRY_CAST({cr_c} AS DOUBLE))) AS diff
                    FROM read_parquet('{pq}')
                    GROUP BY {folio_c}
                    HAVING diff > 0.01
                )
            """
            row_i = self._conn.execute(imb_q).fetchone()
            imb_count, imb_amt = int(row_i[0] or 0), float(row_i[1] or 0.0)

        tot_j = self._conn.execute(f"SELECT COUNT(*) FROM read_parquet('{pq}')").fetchone()[0]

        return GoldIntegritySummaryDTO(
            total_debit=round(tot_dr, 2),
            total_credit=round(tot_cr, 2),
            global_imbalance=round(diff_g, 2),
            is_globally_balanced=(diff_g <= 0.01),
            imbalanced_entries_count=imb_count,
            imbalanced_entries_amount=round(imb_amt, 2),
            total_journals_count=tot_j,
        )
