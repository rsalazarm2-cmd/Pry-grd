"""Tests para el Motor de Auditoría Forense y Detección de Riesgos (CU-16 a CU-19).

Valida que:
1. analyze_sod_violations detecte violaciones de Maker == Checker.
2. analyze_forensic_traps detecte trampas de 00:00:00 y montos redondos > $100K.
3. run_full_forensic_audit calcule correctamente el Financial Integrity Risk Score.
"""

from pathlib import Path
import duckdb
import pytest

from src.audit.infrastructure.forensic_audit_engine import ForensicAuditEngine


@pytest.fixture
def conn():
    return duckdb.connect(":memory:")


@pytest.fixture
def silver_forensic_parquet(conn, test_data_dir: Path) -> Path:
    path = test_data_dir / "silver_forensic.parquet"
    conn.execute(f"""
        COPY (
            SELECT * FROM (VALUES
                ('1001', 'UserA', 'UserA', '2025-01-15 00:00:00', '2025-01-15 10:00:00', 'ENE-2025', 100000.0),
                ('1002', 'UserB', 'UserC', '2025-01-16 14:30:00', '2025-01-16 15:00:00', 'ENE-2025', 45000.0),
                ('1003', 'UserD', 'UserD', '2025-01-17 09:00:00', '2025-01-17 09:05:00', 'ENE-2025', 200000.0)
            ) AS t(FOLIO_ASIENTO, USUARIO_REGISTRADOR, USUARIO_APROBADOR, FECHA_REGISTRO_CONTABLE, FECHA_CONTABILIZACION, PERIODO_CONTABLE, CARGO_MONEDA_FUNCIONAL)
        ) TO '{path}' (FORMAT PARQUET)
    """)
    return path


def test_analyze_sod_violations(conn, silver_forensic_parquet: Path):
    """CU-16: Detecta violaciones de SoD (Maker == Checker)."""
    engine = ForensicAuditEngine(conn)
    sod_list = engine.analyze_sod_violations(silver_forensic_parquet)

    assert len(sod_list) == 2  # Asientos 1001 y 1003 (UserA==UserA y UserD==UserD)
    assert sod_list[0].usuario_registrador == sod_list[0].usuario_aprobador


def test_analyze_forensic_traps(conn, silver_forensic_parquet: Path):
    """CU-17: Detecta trampas de 00:00:00 y montos redondos > $100K."""
    engine = ForensicAuditEngine(conn)
    traps = engine.analyze_forensic_traps(silver_forensic_parquet)

    # 1001 tiene medianoche + monto redondo 100K; 1003 tiene monto redondo 200K
    midnight_traps = [t for t in traps if t.tipo_trampa == "MIDNIGHT_STAMP"]
    round_traps = [t for t in traps if t.tipo_trampa == "ROUND_AMOUNT"]

    assert len(midnight_traps) >= 1
    assert len(round_traps) >= 2


def test_run_full_forensic_audit_score(conn, silver_forensic_parquet: Path):
    """CU-19: Revisa el Financial Integrity Risk Score consolidado."""
    engine = ForensicAuditEngine(conn)
    matrix = engine.run_full_forensic_audit(silver_forensic_parquet)

    assert matrix.score.total_asientos_analizados == 3
    assert matrix.score.sod_violations_count == 2
    assert matrix.score.financial_integrity_score < 100.0  # Penalizado por los hallazgos
    assert matrix.score.nivel_riesgo_global in ["ALTO", "CRITICO", "MEDIO"]
