from typing import List, Dict, Type
from src.cleaning.domain.cleaning_ast import CleaningColumnNode
from src.cleaning.domain.cleaning_strategies import CleaningStrategy
from src.cleaning.infrastructure.duckdb_cleaning_queries import DuckDbCleaningQueries

class CleanDatasetUseCase:
    """
    Orquesta la aplicación de estrategias de limpieza.
    Puede ser consumido por Bronce, Plata u Oro.
    """
    
    def execute_for_column(self, column_name: str, strategies: List[CleaningStrategy], target_alias: str = None) -> str:
        """
        Applies a chain of cleaning strategies to a single column and returns the generated SQL expression.
        """
        node = CleaningColumnNode(column_name)
        
        for strategy in strategies:
            node = strategy.apply(node)
            
        sql_expr = DuckDbCleaningQueries.build_cleaning_expression(node)
        
        alias = target_alias or column_name
        return f'{sql_expr} AS "{alias}"'

    def execute_for_schema(self, schema_rules: Dict[str, List[CleaningStrategy]]) -> List[str]:
        """
        Applies cleaning strategies for multiple columns based on a schema rules dictionary.
        """
        expressions = []
        for col_name, strategies in schema_rules.items():
            expressions.append(self.execute_for_column(col_name, strategies))
        return expressions
