"""Tests para el Evaluador de Reglas Condicionales No-Code (CU-09 & CU-10).

Valida que:
1. Las condiciones (GT, LT, EQ, NEQ, IS_NULL) se compilen a CASE WHEN vectorizados.
2. La evaluación sobre Parquet DuckDB retorne el conteo exacto de coincidencias y muestras.
"""

from pathlib import Path
import duckdb
import pytest

from src.silver.domain.rule_expression_dto import (
    ConditionalRuleDTO,
    RuleConditionDTO,
)
from src.silver.infrastructure.silver_rule_evaluator_engine import (
    SilverRuleEvaluatorEngine,
)


@pytest.fixture
def conn():
    return duckdb.connect(":memory:")


@pytest.fixture
def parquet_rules(conn, test_data_dir: Path) -> str:
    path = test_data_dir / "rules_test.parquet"
    conn.execute(f"""
        COPY (
            SELECT * FROM (VALUES
                (150000.0, 'MANUAL',  'UserA'),
                (50000.0,  'AUTOMATICO', 'UserB'),
                (120000.0, 'MANUAL',  'UserC'),
                (8000.0,   'MANUAL',  'UserD')
            ) AS t(MONTO, ORIGEN, USUARIO)
        ) TO '{path}' (FORMAT PARQUET)
    """)
    return str(path)


def test_build_case_expression_gt(conn):
    """Verifica compilación CASE WHEN con operador GT."""
    engine = SilverRuleEvaluatorEngine(conn)
    rule = ConditionalRuleDTO(
        rule_name="REGLA_MONTO",
        conditions=[RuleConditionDTO(column_name="MONTO", operator="GT", value=100000)],
        then_result_column="RIESGO",
        then_value="ALTO",
        else_value="NORMAL",
    )
    sql = engine.build_case_expression(rule)
    assert 'TRY_CAST("MONTO" AS DOUBLE) > 100000' in sql
    assert "THEN 'ALTO'" in sql
    assert "ELSE 'NORMAL'" in sql


def test_evaluate_rule_preview_matches(conn, parquet_rules):
    """Evalúa coincidencia sobre datos sintéticos (MONTO > 100000 AND ORIGEN == 'MANUAL')."""
    engine = SilverRuleEvaluatorEngine(conn)
    rule = ConditionalRuleDTO(
        rule_name="REGLA_SOX",
        conditions=[
            RuleConditionDTO(column_name="MONTO", operator="GT", value=100000),
            RuleConditionDTO(column_name="ORIGEN", operator="EQ", value="MANUAL"),
        ],
        logical_operator="AND",
        then_result_column="RIESGO_SOX",
        then_value="CRITICO",
        else_value="OK",
    )
    result = engine.evaluate_rule_preview(parquet_rules, rule)

    assert result.total_rows == 4
    assert result.matches_count == 2  # 150000 MANUAL & 120000 MANUAL
    assert result.matches_percentage == 50.0
    assert len(result.sample_rows) == 2
    assert result.sample_rows[0]["RIESGO_SOX"] == "CRITICO"


def test_evaluate_rule_preview_is_null(conn, test_data_dir: Path):
    """Verifica el operador IS_NULL."""
    path = str(test_data_dir / "null_rules_test.parquet")
    conn.execute(f"""
        COPY (
            SELECT * FROM (VALUES
                (1, NULL),
                (2, 'APROBADO'),
                (3, '')
            ) AS t(ID, ESTADO)
        ) TO '{path}' (FORMAT PARQUET)
    """)

    engine = SilverRuleEvaluatorEngine(conn)
    rule = ConditionalRuleDTO(
        rule_name="REGLA_NULOS",
        conditions=[RuleConditionDTO(column_name="ESTADO", operator="IS_NULL", value=None)],
        then_result_column="FLAG_NULO",
        then_value="PENDIENTE",
        else_value="OK",
    )
    result = engine.evaluate_rule_preview(path, rule)

    assert result.total_rows == 3
    assert result.matches_count == 2  # NULL y ''


def test_evaluate_rule_preview_nested_ast(conn, parquet_rules):
    """Verifica compilación y evaluación de Árbol AST ((A AND B) OR C)."""
    from src.silver.domain.rule_expression_dto import RuleGroupDTO

    engine = SilverRuleEvaluatorEngine(conn)
    # ((MONTO > 100000 AND ORIGEN == 'MANUAL') OR USUARIO == 'UserB')
    group_a = RuleGroupDTO(
        logical_operator="AND",
        conditions=[
            RuleConditionDTO(column_name="MONTO", operator="GT", value=100000),
            RuleConditionDTO(column_name="ORIGEN", operator="EQ", value="MANUAL"),
        ],
    )
    root = RuleGroupDTO(
        logical_operator="OR",
        conditions=[RuleConditionDTO(column_name="USUARIO", operator="EQ", value="UserB")],
        sub_groups=[group_a],
    )

    rule = ConditionalRuleDTO(
        rule_name="REGLA_AST_COMPLEJA",
        root_group=root,
        then_result_column="ALERTA_AST",
        then_value="RIESGO",
        else_value="OK",
    )
    result = engine.evaluate_rule_preview(parquet_rules, rule)

    # 150000 MANUAL (Group A match)
    # 50000 AUTOMATICO UserB (UserB match)
    # 120000 MANUAL (Group A match)
    # Total matches = 3 out of 4
    assert result.matches_count == 3
    assert "(" in result.sql_expression
