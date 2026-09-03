"""Motor DuckDB Nativo de Evaluación de Reglas Condicionales No-Code con AST (CU-09 & CU-10).

Traduce reglas compuestas e interconectadas con sub-grupos ((A AND B) OR C)
a sentencias CASE WHEN vectorizadas en SQL con paréntesis anidados.
"""

import logging
from pathlib import Path
import duckdb

from src.silver.domain.rule_expression_dto import (
    ConditionalRuleDTO,
    RuleConditionDTO,
    RuleGroupDTO,
    RuleEvaluationResultDTO,
)

logger = logging.getLogger(__name__)


def _safe(path: Path) -> str:
    return str(path.resolve()).replace("'", "''")


def _compile_condition(cond: RuleConditionDTO) -> str:
    """Traduce 1 condición atómica a expresión SQL DuckDB."""
    col = f'"{cond.column_name}"'
    op = cond.operator.upper()
    val = cond.value

    if op == "EQ":
        return f"{col} = '{val}'" if isinstance(val, str) else f"{col} = {val}"
    elif op == "NEQ":
        return f"{col} != '{val}'" if isinstance(val, str) else f"{col} != {val}"
    elif op == "GT":
        return f"TRY_CAST({col} AS DOUBLE) > {val}"
    elif op == "GTE":
        return f"TRY_CAST({col} AS DOUBLE) >= {val}"
    elif op == "LT":
        return f"TRY_CAST({col} AS DOUBLE) < {val}"
    elif op == "LTE":
        return f"TRY_CAST({col} AS DOUBLE) <= {val}"
    elif op == "IS_NULL":
        return f"({col} IS NULL OR TRIM(CAST({col} AS VARCHAR)) = '')"
    elif op == "NOT_NULL":
        return f"({col} IS NOT NULL AND TRIM(CAST({col} AS VARCHAR)) != '')"
    elif op == "IN":
        items = ", ".join(f"'{v}'" for v in val) if isinstance(val, list) else str(val)
        return f"{col} IN ({items})"
    elif op == "IS_WEEKEND":
        return f"dayofweek(TRY_CAST({col} AS DATE)) IN (0, 6)"
    elif op == "WEEKDAY_EQ":
        return f"dayofweek(TRY_CAST({col} AS DATE)) = {val}"
    return "1=1"


def compile_rule_group(group: RuleGroupDTO) -> str:
    """Compila recursivamente un grupo AST a expresión SQL con paréntesis."""
    parts = []
    for c in group.conditions:
        parts.append(_compile_condition(c))
    for sg in group.sub_groups:
        sub_sql = compile_rule_group(sg)
        if sub_sql:
            parts.append(f"({sub_sql})")

    if not parts:
        return ""
    joiner = f" {group.logical_operator.upper()} "
    return joiner.join(parts)


class SilverRuleEvaluatorEngine:
    """Compilador y Evaluador DuckDB de Reglas Condicionales No-Code."""

    def __init__(self, conn: duckdb.DuckDBPyConnection):
        self._conn = conn

    def build_case_expression(self, rule: ConditionalRuleDTO) -> str:
        """Construye la sentencia CASE WHEN en SQL soportando Árbol AST o plano."""
        where_clause = ""
        if rule.root_group:
            where_clause = compile_rule_group(rule.root_group)
        elif rule.conditions:
            compiled_conds = [_compile_condition(c) for c in rule.conditions]
            joiner = f" {rule.logical_operator.upper()} "
            where_clause = joiner.join(compiled_conds)

        if not where_clause:
            return f"'{rule.else_value or 'NORMAL'}'"

        else_clause = f"'{rule.else_value}'" if rule.else_value else "NULL"
        return f"CASE WHEN ({where_clause}) THEN '{rule.then_value}' ELSE {else_clause} END"

    def evaluate_rule_preview(
        self, parquet_path: str, rule: ConditionalRuleDTO
    ) -> RuleEvaluationResultDTO:
        """CU-10: Previsualización vectorizada de la regla sobre Parquet."""
        pq = _safe(Path(parquet_path))

        case_expr = self.build_case_expression(rule)
        col_name = rule.then_result_column

        count_query = f"""
            SELECT
                COUNT(*) AS total,
                COUNT(*) FILTER (WHERE ({case_expr}) = '{rule.then_value}') AS matches
            FROM read_parquet('{pq}')
        """
        row = self._conn.execute(count_query).fetchone()
        total, matches = int(row[0]), int(row[1])
        pct = round((matches / total) * 100, 2) if total > 0 else 0.0

        sample_query = f"""
            SELECT *, ({case_expr}) AS "{col_name}"
            FROM read_parquet('{pq}')
            WHERE ({case_expr}) = '{rule.then_value}'
            LIMIT 10
        """
        cursor = self._conn.execute(sample_query)
        col_names = [d[0] for d in cursor.description]
        raw_rows = cursor.fetchall()
        sample = [dict(zip(col_names, r)) for r in raw_rows]

        return RuleEvaluationResultDTO(
            rule_name=rule.rule_name,
            result_column=col_name,
            total_rows=total,
            matches_count=matches,
            matches_percentage=pct,
            sql_expression=case_expr,
            sample_rows=sample,
        )
