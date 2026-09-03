import logging
from pathlib import Path
from typing import List
import duckdb

from src.silver.domain.atomicity import AtomicitySuggestionDTO, ColumnSplitRuleDTO
from src.silver.domain.atomicity_analyzer import AtomicityAnalyzer

logger = logging.getLogger(__name__)


class AtomicityDuckDBService:
    """Servicio de Infraestructura DuckDB para muestrear celdas y ejecutar split_part en la Capa Plata."""

    def __init__(self, conn: duckdb.DuckDBPyConnection):
        self.conn = conn

    def get_atomicity_suggestions(self, bronze_parquet_path: str) -> List[AtomicitySuggestionDTO]:
        target_path = Path(bronze_parquet_path).resolve()
        if not target_path.exists():
            return []

        schema_info = self.conn.execute(f"DESCRIBE SELECT * FROM read_parquet('{target_path}')").fetchall()
        columns = [r[0] for r in schema_info]

        suggestions: List[AtomicitySuggestionDTO] = []

        for col in columns:
            try:
                samples_res = self.conn.execute(f"""
                    SELECT DISTINCT CAST("{col}" AS VARCHAR)
                    FROM read_parquet('{target_path}')
                    WHERE "{col}" IS NOT NULL AND length(trim(CAST("{col}" AS VARCHAR))) > 0
                    LIMIT 20
                """).fetchall()
                samples = [r[0] for r in samples_res if r[0]]

                suggestion = AtomicityAnalyzer.analyze_column(col, samples)
                if suggestion:
                    suggestions.append(suggestion)
            except Exception as e:
                logger.warning("Error analizando atomización para columna %s: %s", col, e)

        return suggestions

    @staticmethod
    def build_split_expressions(rule: ColumnSplitRuleDTO) -> List[str]:
        """Genera las expresiones SQL vectorizadas `split_part` para DuckDB."""
        if not rule.enabled or not rule.segments:
            return []

        expressions: List[str] = []
        col_name = rule.column_name
        delim = rule.delimiter

        for seg in rule.segments:
            alias = seg.suggested_alias.strip().upper()
            idx = seg.index + 1
            expr = f"trim(split_part(\"{col_name}\", '{delim}', {idx})) AS \"{alias}\""
            expressions.append(expr)

        return expressions
