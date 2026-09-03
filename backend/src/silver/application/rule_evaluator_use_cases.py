"""Caso de Uso para Evaluación de Reglas Condicionales No-Code (CU-09/CU-10).

Orquesta la compilación y vista previa de reglas condicionales delegando
en el motor SilverRuleEvaluatorEngine con la conexión DuckDB compartida.
"""

from src.silver.domain.rule_expression_dto import (
    ConditionalRuleDTO,
    RuleEvaluationResultDTO,
)
from src.silver.infrastructure.silver_rule_evaluator_engine import (
    SilverRuleEvaluatorEngine,
)
from src.shared.api.dependencies import get_repository


class EvaluateConditionalRuleUseCase:
    """CU-09 / CU-10: Previsualiza la aplicación de una regla condicional."""

    def execute(
        self, parquet_path: str, rule: ConditionalRuleDTO
    ) -> RuleEvaluationResultDTO:
        """Compila la regla a CASE WHEN y devuelve estadísticas y muestra de coincidencias."""
        conn = get_repository().conn
        engine = SilverRuleEvaluatorEngine(conn)
        return engine.evaluate_rule_preview(parquet_path, rule)
