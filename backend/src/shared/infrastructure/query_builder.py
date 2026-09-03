"""
Utilidad compartida para construir cláusulas SQL WHERE seguras con DuckDB.

Resuelve:
- SEC-6 (SQL Injection): Parámetros posicionales en vez de f-strings para valores de usuario.
- Hallazgo 6 (DRY): Un único punto de mantenimiento para las 4 capas de query.

Nota: DuckDB soporta `?` placeholders para VALORES, pero NO para identificadores
(nombres de columna/tabla). Los identificadores se validan contra una whitelist
del esquema real del Parquet antes de interpolarlos.
"""

import json
from typing import Any


class QueryBuilder:
    """Construye SQL seguro con parámetros posicionales para DuckDB."""

    @staticmethod
    def validate_column(column_name: str, valid_columns: list[str]) -> str | None:
        """Valida que un nombre de columna pertenezca al esquema real.

        Retorna el nombre exacto del esquema (con capitalización original)
        o None si no es válido.
        """
        col_map = {c.upper(): c for c in valid_columns}
        return col_map.get(column_name.upper())

    @staticmethod
    def build_where(
        columns: list[str],
        search_term: str | None = None,
        column_name: str | None = None,
        filters_json: str | None = None,
    ) -> tuple[str, list[Any]]:
        """Construye (where_sql, params) seguros para DuckDB.

        Args:
            columns: Lista de nombres de columna válidos del esquema del Parquet.
            search_term: Término de búsqueda libre del usuario.
            column_name: Columna específica donde buscar (o None para todas).
            filters_json: JSON string con filtros multi-valor {"COL": ["val1", "val2"]}.

        Returns:
            Tupla (where_sql, params) donde where_sql es "" o "WHERE ..." y
            params es una lista de valores posicionales para `conn.execute(sql, params)`.
        """
        where_clauses: list[str] = []
        params: list[Any] = []

        # Búsqueda libre con ILIKE
        if search_term and search_term.strip():
            term = search_term.strip()
            validated_col = None
            if column_name and column_name.upper() != "TODOS":
                validated_col = QueryBuilder.validate_column(column_name, columns)

            if validated_col:
                where_clauses.append(f'CAST("{validated_col}" AS VARCHAR) ILIKE ?')
                params.append(f"%{term}%")
            else:
                or_parts = []
                for col in columns:
                    or_parts.append(f'CAST("{col}" AS VARCHAR) ILIKE ?')
                    params.append(f"%{term}%")
                where_clauses.append(f"({' OR '.join(or_parts)})")

        # Filtros multi-valor tipo Excel
        if filters_json and filters_json.strip():
            try:
                filters_dict = json.loads(filters_json)
                for col, val_list in filters_dict.items():
                    validated = QueryBuilder.validate_column(col, columns)
                    if validated and isinstance(val_list, list) and len(val_list) > 0:
                        placeholders = ", ".join(["?"] * len(val_list))
                        where_clauses.append(
                            f'CAST("{validated}" AS VARCHAR) IN ({placeholders})'
                        )
                        params.extend(str(v) for v in val_list)
            except (json.JSONDecodeError, TypeError):
                pass

        if not where_clauses:
            return "", []

        where_sql = f"WHERE {' AND '.join(where_clauses)}"
        return where_sql, params

    @staticmethod
    def build_quality_filter(quality_status: str | None = None) -> tuple[str, list[Any]]:
        """Construye filtro WHERE para QUALITY_STATUS de la capa Plata."""
        if quality_status and quality_status.upper() != "TODOS":
            return '"QUALITY_STATUS" = ?', [quality_status.upper()]
        return "", []
