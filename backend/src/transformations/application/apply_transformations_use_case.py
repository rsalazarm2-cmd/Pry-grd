from typing import List, Dict, Type
from src.transformations.domain.transformation_strategies import TransformationStrategy
from src.transformations.infrastructure.duckdb_transformation_queries import DuckDbTransformationQueries

class ApplyTransformationsUseCase:
    """
    Orquesta la aplicación de estrategias de transformación (enriquecimiento).
    Normalmente consumido por la Capa Plata.
    """
    
    def execute_for_column(self, strategy: TransformationStrategy, target_alias: str) -> str:
        """
        Applies a transformation strategy to generate a new derived column's SQL expression.
        """
        node = strategy.apply()
        sql_expr = DuckDbTransformationQueries.build_transformation_expression(node)
        return f'{sql_expr} AS "{target_alias}"'

    def execute_for_schema(self, schema_transformations: Dict[str, TransformationStrategy]) -> List[str]:
        """
        Generates SQL expressions for multiple derived columns.
        schema_transformations: { "NEW_COLUMN_ALIAS": TransformationStrategy }
        """
        expressions = []
        for alias, strategy in schema_transformations.items():
            expressions.append(self.execute_for_column(strategy, alias))
        return expressions
