"""Pruebas Unitarias para el Motor de Scoring Consolidado de Riesgo en Capa Oro (Fase 3)."""

import duckdb
import pytest
from src.gold.infrastructure.gold_risk_scoring_engine import GoldRiskScoringEngine


@pytest.fixture
def memory_duckdb_journals():
    """Fixture que provee una BD DuckDB en memoria con asientos contables."""
    conn = duckdb.connect(":memory:")
    conn.execute("""
        CREATE TABLE test_journals (
            FOLIO_ASIENTO VARCHAR,
            CARGO_MONEDA_FUNCIONAL DOUBLE,
            USUARIO_REGISTRADOR VARCHAR,
            USUARIO_APROBADOR VARCHAR,
            GLOSA VARCHAR,
            FECHA_CONTABILIZACION DATE,
            FECHA_REGISTRO_CONTABLE TIMESTAMP
        )
    """)

    conn.execute("""
        INSERT INTO test_journals VALUES
        -- Normal
        ('J-001', 5000.00, 'usr1', 'supervisor1', 'Pago de nómina ordinaria', '2026-03-02', '2026-03-02 10:00:00'),
        -- Crítico (SOD + Fin de semana + Fraccionamiento)
        ('J-002', 9900.00, 'bad_user', 'bad_user', 'Ajuste manual urgente .', '2026-03-01', '2026-03-01 23:00:00'),
        ('J-003', 9900.00, 'bad_user', 'bad_user', 'Reclasificacion .', '2026-03-01', '2026-03-01 23:15:00')
    """)
    return conn


def test_gold_risk_scoring_engine_execution(memory_duckdb_journals):
    """Verifica que el motor de scoring calcule scores entre 0 y 100 y clasifique los asientos."""
    engine = GoldRiskScoringEngine(memory_duckdb_journals)
    datamart = engine.generate_executive_datamart("test_journals")

    assert datamart.total_asientos_analizados == 3
    assert datamart.total_asientos_criticos >= 2
    assert len(datamart.top_asientos_criticos) > 0

    top_j = datamart.top_asientos_criticos[0]
    assert top_j.score_global >= 70.0
    assert top_j.nivel_riesgo == "CRITICO"
    assert len(top_j.factores_riesgo) >= 2


def test_top_users_risk_aggregation(memory_duckdb_journals):
    """Verifica la agregación de riesgo por usuario en el Data Mart Ejecutivo Oro."""
    engine = GoldRiskScoringEngine(memory_duckdb_journals)
    datamart = engine.generate_executive_datamart("test_journals")

    assert len(datamart.top_usuarios_riesgosos) >= 1
    top_user = datamart.top_usuarios_riesgosos[0]
    assert top_user.usuario == "bad_user"
    assert top_user.asientos_alto_riesgo == 2
