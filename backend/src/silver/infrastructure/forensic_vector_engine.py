"""Motor Vectorial Forense en DuckDB para la Capa Plata.

Ejecuta el enriquecimiento analítico de los 5 vectores de riesgo mediante
consultas vectorizadas dinámicas sobre tablas o Parquet en DuckDB.
"""

from typing import List, Dict, Any, Optional
import duckdb
from src.silver.domain.forensic_vector_dto import ForensicAuditSummaryDTO


class ForensicVectorEngine:
    """Motor de cálculo vectorial forense dinámico con API nativa de DuckDB."""

    def __init__(self, conn: duckdb.DuckDBPyConnection) -> None:
        """Inicializa el motor con una conexión activa a DuckDB.

        Args:
            conn: Conexión DuckDB configurada.
        """
        self._conn = conn

    def _resolve_col(self, available_cols: List[str], candidates: List[str], default_expr: str) -> str:
        """Resuelve dinámicamente el nombre de columna presente en el dataset."""
        cols_upper = {c.upper(): c for c in available_cols}
        for cand in candidates:
            if cand.upper() in cols_upper:
                return f'"{cols_upper[cand.upper()]}"'
        return default_expr

    def _get_table_columns(self, table_name: str) -> List[str]:
        """Obtiene la lista de nombres de columnas de una tabla o vista."""
        try:
            res = self._conn.execute(f"SELECT * FROM {table_name} LIMIT 0")
            return [desc[0] for desc in res.description]
        except Exception:
            return []

    def build_forensic_vector_query(self, table_name: str, split_threshold: float = 10000.0) -> str:
        """Genera la consulta SQL vectorizada adaptándose al esquema dinámico.

        Args:
            table_name: Nombre de la tabla o vista Silver en DuckDB.
            split_threshold: Umbral financiero para alerta de fraccionamiento.

        Returns:
            Sentencia SQL DuckDB optimizada.
        """
        cols = self._get_table_columns(table_name)
        folio_col = self._resolve_col(cols, ["FOLIO_ASIENTO", "NUMERO_ASIENTO", "HEADER_ID", "ASIENTO"], "ROW_NUMBER() OVER()")
        cargo_col = self._resolve_col(cols, ["CARGO_MONEDA_FUNCIONAL", "CARGO", "MONTO", "ENTERED_DR", "TOTAL_CARGOS_CABECERA"], "0.0")
        u_reg_col = self._resolve_col(cols, ["USUARIO_REGISTRADOR", "CREATED_BY", "USUARIO_CREACION", "USUARIO_REGISTRO", "USUARIO"], "'ANON'")
        u_apr_col = self._resolve_col(cols, ["USUARIO_APROBADOR", "APPROVED_BY", "USUARIO_APROBACION", "APROBADOR"], "'ANON'")
        glosa_col = self._resolve_col(cols, ["GLOSA_ASIENTO", "GLOSA", "DESCRIPCION", "CONCEPTO", "HEADER_DESCRIPTION"], "'N/A'")
        f_gl_col = self._resolve_col(cols, ["FECHA_CONTABILIZACION", "GL_DATE", "FECHA_GL", "FECHA_CONTABLE"], "CURRENT_DATE")
        f_reg_col = self._resolve_col(cols, ["FECHA_REGISTRO_CONTABLE", "CREATION_DATE", "FECHA_CREACION", "FECHA_REGISTRO"], "CURRENT_TIMESTAMP")

        return f"""
        WITH BaseEnriquecida AS (
            SELECT
                COALESCE(CAST({folio_col} AS VARCHAR), 'N/A') AS FOLIO_ASIENTO,
                TRY_CAST({cargo_col} AS DOUBLE) AS CARGO_MONEDA_FUNCIONAL,
                CAST({u_reg_col} AS VARCHAR) AS USUARIO_REGISTRADOR,
                CAST({u_apr_col} AS VARCHAR) AS USUARIO_APROBADOR,
                CAST({glosa_col} AS VARCHAR) AS GLOSA,
                TRY_CAST({f_gl_col} AS DATE) AS FECHA_CONTABILIZACION,
                TRY_CAST({f_reg_col} AS TIMESTAMP) AS FECHA_REGISTRO_CONTABLE,

                -- 1. Vector Temporal
                (DAYOFWEEK(TRY_CAST({f_gl_col} AS DATE)) IN (0, 6)) AS flag_fin_semana,
                (EXTRACT(HOUR FROM TRY_CAST({f_reg_col} AS TIMESTAMP)) NOT BETWEEN 7 AND 19) AS flag_horario_nocturno,
                ABS(DATEDIFF('day', TRY_CAST({f_reg_col} AS DATE), TRY_CAST({f_gl_col} AS DATE))) AS dias_diferencia,

                -- 2. Vector SOD
                (LOWER(TRIM(COALESCE(CAST({u_reg_col} AS VARCHAR), ''))) = LOWER(TRIM(COALESCE(CAST({u_apr_col} AS VARCHAR), '')))) AS flag_mismo_usuario,

                -- 3. Vector Semántico
                ({glosa_col} IS NULL OR LENGTH(TRIM(CAST({glosa_col} AS VARCHAR))) < 3 OR LOWER(CAST({glosa_col} AS VARCHAR)) SIMILAR TO '.*(ajuste|reclasif|corr|\\.|temp).*') AS flag_glosa_sospechosa,
                LENGTH(TRIM(COALESCE(CAST({glosa_col} AS VARCHAR), ''))) AS longitud_glosa,

                -- 4. Vector Matemático
                (TRY_CAST({cargo_col} AS DOUBLE) > 0 AND (TRY_CAST({cargo_col} AS DOUBLE) % 1000 = 0)) AS flag_monto_redondo,
                TRY_CAST(SUBSTR(CAST(ABS(TRY_CAST({cargo_col} AS DOUBLE)) AS VARCHAR), 1, 1) AS INT) AS primer_digito,

                -- 5. Vector Acumulado / Fraccionamiento
                SUM(COALESCE(TRY_CAST({cargo_col} AS DOUBLE), 0)) OVER (
                    PARTITION BY COALESCE(CAST({u_reg_col} AS VARCHAR), 'ANON'), TRY_CAST({f_reg_col} AS DATE)
                ) AS monto_acumulado_dia,
                COUNT(*) OVER (
                    PARTITION BY COALESCE(CAST({u_reg_col} AS VARCHAR), 'ANON'), TRY_CAST({f_reg_col} AS DATE)
                ) AS conteo_asientos_dia
            FROM {table_name}
        )
        SELECT
            *,
            (conteo_asientos_dia > 1 AND monto_acumulado_dia >= {split_threshold} AND CARGO_MONEDA_FUNCIONAL < {split_threshold}) AS flag_posible_fraccionamiento,
            (
                (CASE WHEN flag_fin_semana THEN 25 ELSE 0 END) +
                (CASE WHEN flag_horario_nocturno THEN 15 ELSE 0 END) +
                (CASE WHEN flag_mismo_usuario THEN 30 ELSE 0 END) +
                (CASE WHEN flag_glosa_sospechosa THEN 15 ELSE 0 END) +
                (CASE WHEN flag_monto_redondo THEN 15 ELSE 0 END)
            ) AS score_preliminar
        FROM BaseEnriquecida
        """

    def execute_forensic_audit(self, table_name: str) -> ForensicAuditSummaryDTO:
        """Ejecuta la auditoría vectorial y retorna el resumen ejecutivo.

        Args:
            table_name: Nombre de la tabla de Plata en DuckDB.

        Returns:
            Objeto ForensicAuditSummaryDTO con métricas agregadas.
        """
        sql = self.build_forensic_vector_query(table_name)
        agg_sql = f"""
            WITH Metrics AS ({sql})
            SELECT
                COUNT(*) AS total,
                SUM(CASE WHEN flag_fin_semana OR flag_horario_nocturno THEN 1 ELSE 0 END) AS temp_alerts,
                SUM(CASE WHEN flag_mismo_usuario THEN 1 ELSE 0 END) AS sod_alerts,
                SUM(CASE WHEN flag_glosa_sospechosa THEN 1 ELSE 0 END) AS sem_alerts,
                SUM(CASE WHEN flag_posible_fraccionamiento THEN 1 ELSE 0 END) AS split_alerts,
                SUM(CASE WHEN score_preliminar >= 40 THEN 1 ELSE 0 END) AS high_risk
            FROM Metrics
        """
        res = self._conn.execute(agg_sql).fetchone()
        if not res:
            return ForensicAuditSummaryDTO()

        return ForensicAuditSummaryDTO(
            total_registros_evaluados=res[0] or 0,
            total_alertas_temporales=res[1] or 0,
            total_alertas_sod=res[2] or 0,
            total_alertas_semanticas=res[3] or 0,
            total_alertas_fraccionamiento=res[4] or 0,
            total_asientos_alto_riesgo=res[5] or 0,
        )
