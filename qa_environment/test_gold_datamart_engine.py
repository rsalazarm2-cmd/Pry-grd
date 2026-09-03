"""Tests para el Motor de Datamarts Oro e Integridad Contable (CU-11, CU-12, CU-13).

Valida que:
1. gold_balance_by_ledger.parquet se genere con los totales y estado de cuadre correctos.
2. gold_balance_by_account.parquet agrupe por cuenta y calcule el saldo neto.
3. compute_integrity_summary detecte la ecuación contable y los asientos descuadrados.
"""

from pathlib import Path
import duckdb
import pytest

from src.gold.infrastructure.gold_datamart_engine import GoldDatamartEngine


@pytest.fixture
def conn():
    return duckdb.connect(":memory:")


@pytest.fixture
def silver_sample_parquet(conn, test_data_dir: Path) -> Path:
    path = test_data_dir / "silver_sample.parquet"
    conn.execute(f"""
        COPY (
            SELECT * FROM (VALUES
                ('LIBRO_OPERATIVO', '1001', '110101', 1000.0, 0.0),
                ('LIBRO_OPERATIVO', '1001', '210101', 0.0, 1000.0),
                ('LIBRO_OPERATIVO', '1002', '110101', 500.0, 0.0),
                ('LIBRO_OPERATIVO', '1002', '210101', 0.0, 400.0),
                ('LIBRO_FISCAL',    '1003', '510101', 250.0, 250.0)
            ) AS t(NOMBRE_LIBRO, FOLIO_ASIENTO, CUENTA_CONTABLE, CARGO_MONEDA_FUNCIONAL, ABONO_MONEDA_FUNCIONAL)
        ) TO '{path}' (FORMAT PARQUET)
    """)
    return path


def test_generate_ledger_balance(conn, silver_sample_parquet: Path, test_data_dir: Path):
    """CU-11: Verifica agregación por libro contable."""
    engine = GoldDatamartEngine(conn)
    gold_dir = test_data_dir / "gold_out"
    gold_dir.mkdir(exist_ok=True)
    target_path = gold_dir / "gold_balance_by_ledger.parquet"

    rows = engine.generate_ledger_balance(silver_sample_parquet, target_path)
    assert rows == 2  # LIBRO_OPERATIVO y LIBRO_FISCAL

    data = conn.execute(f"SELECT * FROM read_parquet('{target_path}') ORDER BY LEDGER_NAME").fetchall()
    # LIBRO_FISCAL: CARGOS=250, ABONOS=250, DIFERENCIA=0 -> CUADRADO
    # LIBRO_OPERATIVO: CARGOS=1500, ABONOS=1400, DIFERENCIA=100 -> DESCUADRADO
    res_dict = {r[0]: (r[1], r[2], r[3], r[4]) for r in data}
    assert res_dict["LIBRO_FISCAL"][3] == "CUADRADO"
    assert res_dict["LIBRO_OPERATIVO"][3] == "DESCUADRADO"


def test_generate_account_balance(conn, silver_sample_parquet: Path, test_data_dir: Path):
    """CU-12: Verifica agregación por cuenta contable PyG."""
    engine = GoldDatamartEngine(conn)
    gold_dir = test_data_dir / "gold_out"
    gold_dir.mkdir(exist_ok=True)
    target_path = gold_dir / "gold_balance_by_account.parquet"

    rows = engine.generate_account_balance(silver_sample_parquet, target_path)
    assert rows == 3  # 110101, 210101, 510101

    data = conn.execute(f"SELECT ACCOUNT_CODE, SALDO_NETO FROM read_parquet('{target_path}') WHERE ACCOUNT_CODE='110101'").fetchone()
    assert data[1] == 1500.0  # 1000 + 500


def test_compute_integrity_summary(conn, silver_sample_parquet: Path):
    """CU-13: Verifica la ecuación contable y detección de descuadres."""
    engine = GoldDatamartEngine(conn)
    integrity = engine.compute_integrity_summary(silver_sample_parquet)

    assert integrity.total_debit == 1750.0  # 1000 + 500 + 250
    assert integrity.total_credit == 1650.0 # 1000 + 400 + 250
    assert integrity.global_imbalance == 100.0
    assert integrity.is_globally_balanced is False
    assert integrity.imbalanced_entries_count == 1 # Asiento 1002 (500 vs 400)
