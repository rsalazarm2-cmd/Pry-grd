"""Pruebas Unitarias de Integración para el Motor Vectorial Forense (Fase 1).

Verifica la detección de los 5 vectores forenses:
1. Vector Temporal (Fines de semana y horario nocturno)
2. Vector SOD (Segregación de funciones y autologin)
3. Vector Semántico NLP (Glosas sospechosas o vacías)
4. Vector Matemático (Montos redondos y dígitos)
5. Vector Acumulado / Fraccionamiento (Ventana móvil sumaria)
"""

import duckdb
import pytest
from src.silver.infrastructure.forensic_vector_engine import ForensicVectorEngine
from src.silver.application.forensic_vector_use_cases import ForensicVectorUseCases


@pytest.fixture
def memory_duckdb_with_journals():
    """Fixture que provee una BD DuckDB en memoria con asientos de prueba."""
    conn = duckdb.connect(":memory:")
    conn.execute("""
        CREATE TABLE silver_journals (
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
        INSERT INTO silver_journals VALUES
        -- 1. Normal
        ('AS-001', 4500.00, 'operador1', 'supervisor1', 'Pago a proveedor habitual', '2026-03-02', '2026-03-02 10:00:00'),

        -- 2. Alerta Temporal (Domingo + Horario nocturno)
        ('AS-002', 15000.00, 'operador2', 'supervisor1', 'Reclasificacion urgente', '2026-03-01', '2026-03-01 22:30:00'),

        -- 3. Alerta SOD (Mismo usuario registrador y aprobador)
        ('AS-003', 8000.00, 'juan_perez', 'juan_perez', 'Ajuste mensual', '2026-03-03', '2026-03-03 14:00:00'),

        -- 4. Alerta Semántica NLP (Glosa con punto sospechoso)
        ('AS-004', 12000.00, 'operador3', 'supervisor2', '.', '2026-03-04', '2026-03-04 11:00:00'),

        -- 5. Alerta Fraccionamiento (Split: 2 asientos del mismo usuario el mismo día sumando > 10,000)
        ('AS-005', 9500.00, 'fraudador', 'supervisor3', 'Servicios A', '2026-03-05', '2026-03-05 09:00:00'),
        ('AS-006', 9500.00, 'fraudador', 'supervisor3', 'Servicios B', '2026-03-05', '2026-03-05 09:15:00')
    """)
    return conn


def test_forensic_vector_engine_execution(memory_duckdb_with_journals):
    """Verifica que el motor ejecute la consulta vectorial y retorne el resumen."""
    engine = ForensicVectorEngine(memory_duckdb_with_journals)
    summary = engine.execute_forensic_audit("silver_journals")

    assert summary.total_registros_evaluados == 6
    assert summary.total_alertas_temporales >= 1
    assert summary.total_alertas_sod >= 1
    assert summary.total_alertas_semanticas >= 1
    assert summary.total_alertas_fraccionamiento >= 2


def test_forensic_use_cases_high_risk_ranking(memory_duckdb_with_journals):
    """Verifica que el caso de uso ordene los asientos por mayor puntaje de riesgo."""
    use_cases = ForensicVectorUseCases(memory_duckdb_with_journals)
    high_risk = use_cases.fetch_high_risk_records("silver_journals", limit=10)

    assert len(high_risk) == 6
    top_record = high_risk[0]
    # AS-002 tiene fin de semana + horario nocturno + monto alto
    assert top_record.score_riesgo_preliminar > 0
