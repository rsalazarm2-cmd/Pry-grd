"""Motor de Scoring Consolidado de Riesgo en DuckDB (Capa Oro).

Aplica la matriz de ponderación (0-100 Puntos) sobre los 5 vectores forenses
y genera los Data Marts Ejecutivos para priorización de investigación.
"""

from typing import List
import duckdb
from src.silver.infrastructure.forensic_vector_engine import ForensicVectorEngine
from src.gold.domain.risk_scoring_dto import (
    GoldExecutiveRiskDatamartDTO,
    JournalRiskScoreDTO,
    UserRiskDatamartItemDTO,
)


class GoldRiskScoringEngine:
    """Motor analítico de ponderación de riesgo y generación de Data Marts Oro."""

    def __init__(self, conn: duckdb.DuckDBPyConnection) -> None:
        """Inicializa el motor con la conexión DuckDB.

        Args:
            conn: Conexión DuckDB activa.
        """
        self._conn = conn
        self._forensic_engine = ForensicVectorEngine(conn)

    def build_risk_datamart_query(self, table_name: str) -> str:
        """Genera la consulta SQL que asigna el Score Consolidado (0-100)."""
        base_sql = self._forensic_engine.build_forensic_vector_query(table_name)
        return f"""
        WITH Vectorized AS ({base_sql})
        SELECT
            FOLIO_ASIENTO,
            CARGO_MONEDA_FUNCIONAL AS monto_total,
            USUARIO_REGISTRADOR,
            USUARIO_APROBADOR,
            GLOSA,
            (
                (CASE WHEN flag_mismo_usuario THEN 30.0 ELSE 0.0 END) +
                (CASE WHEN flag_posible_fraccionamiento THEN 25.0 ELSE 0.0 END) +
                (CASE WHEN flag_fin_semana THEN 15.0 WHEN flag_horario_nocturno THEN 10.0 ELSE 0.0 END) +
                (CASE WHEN flag_glosa_sospechosa THEN 15.0 ELSE 0.0 END) +
                (CASE WHEN flag_monto_redondo THEN 10.0 ELSE 0.0 END)
            ) AS score_global,
            CASE
                WHEN (
                    (CASE WHEN flag_mismo_usuario THEN 30.0 ELSE 0.0 END) +
                    (CASE WHEN flag_posible_fraccionamiento THEN 25.0 ELSE 0.0 END) +
                    (CASE WHEN flag_fin_semana THEN 15.0 WHEN flag_horario_nocturno THEN 10.0 ELSE 0.0 END) +
                    (CASE WHEN flag_glosa_sospechosa THEN 15.0 ELSE 0.0 END) +
                    (CASE WHEN flag_monto_redondo THEN 10.0 ELSE 0.0 END)
                ) >= 70.0 THEN 'CRITICO'
                WHEN (
                    (CASE WHEN flag_mismo_usuario THEN 30.0 ELSE 0.0 END) +
                    (CASE WHEN flag_posible_fraccionamiento THEN 25.0 ELSE 0.0 END) +
                    (CASE WHEN flag_fin_semana THEN 15.0 WHEN flag_horario_nocturno THEN 10.0 ELSE 0.0 END) +
                    (CASE WHEN flag_glosa_sospechosa THEN 15.0 ELSE 0.0 END) +
                    (CASE WHEN flag_monto_redondo THEN 10.0 ELSE 0.0 END)
                ) >= 45.0 THEN 'ALTO'
                WHEN (
                    (CASE WHEN flag_mismo_usuario THEN 30.0 ELSE 0.0 END) +
                    (CASE WHEN flag_posible_fraccionamiento THEN 25.0 ELSE 0.0 END) +
                    (CASE WHEN flag_fin_semana THEN 15.0 WHEN flag_horario_nocturno THEN 10.0 ELSE 0.0 END) +
                    (CASE WHEN flag_glosa_sospechosa THEN 15.0 ELSE 0.0 END) +
                    (CASE WHEN flag_monto_redondo THEN 10.0 ELSE 0.0 END)
                ) >= 25.0 THEN 'MEDIO'
                ELSE 'BAJO'
            END AS nivel_riesgo,
            flag_mismo_usuario,
            flag_posible_fraccionamiento,
            flag_fin_semana,
            flag_horario_nocturno,
            flag_glosa_sospechosa,
            flag_monto_redondo
        FROM Vectorized
        """

    def generate_executive_datamart(self, table_name: str) -> GoldExecutiveRiskDatamartDTO:
        """Construye el Data Mart Ejecutivo de Riesgo en Oro.

        Args:
            table_name: Nombre de la tabla o vista Silver.

        Returns:
            Objeto GoldExecutiveRiskDatamartDTO con tops de asientos y usuarios.
        """
        sql = self.build_risk_datamart_query(table_name)
        agg_sql = f"""
            WITH Scored AS ({sql})
            SELECT
                COUNT(*) AS total,
                COALESCE(AVG(score_global), 0.0) AS avg_score,
                SUM(CASE WHEN nivel_riesgo IN ('ALTO', 'CRITICO') THEN 1 ELSE 0 END) AS critical_count,
                SUM(CASE WHEN nivel_riesgo IN ('ALTO', 'CRITICO') THEN COALESCE(monto_total, 0.0) ELSE 0.0 END) AS risk_amount
            FROM Scored
        """
        row = self._conn.execute(agg_sql).fetchone()
        total, avg_score, critical_cnt, risk_amt = row if row else (0, 0.0, 0, 0.0)

        # Top 10 Asientos Críticos
        top_sql = f"""
            WITH Scored AS ({sql})
            SELECT FOLIO_ASIENTO, score_global, nivel_riesgo, USUARIO_REGISTRADOR, COALESCE(monto_total, 0.0),
                   flag_mismo_usuario, flag_posible_fraccionamiento, flag_fin_semana, flag_glosa_sospechosa
            FROM Scored
            ORDER BY score_global DESC, monto_total DESC
            LIMIT 10
        """
        top_rows = self._conn.execute(top_sql).fetchall()
        top_journals: List[JournalRiskScoreDTO] = []
        for r in top_rows:
            factors = []
            if r[5]: factors.append("Violación SOD (Maker=Checker)")
            if r[6]: factors.append("Posible Fraccionamiento (Split)")
            if r[7]: factors.append("Registro en Fin de Semana")
            if r[8]: factors.append("Glosa Sospechosa/Vacía")

            top_journals.append(
                JournalRiskScoreDTO(
                    folio_asiento=str(r[0]),
                    score_global=round(float(r[1] or 0.0), 1),
                    nivel_riesgo=str(r[2]),
                    usuario_registrador=str(r[3] or "ANON"),
                    monto_total=round(float(r[4] or 0.0), 2),
                    factores_riesgo=factors,
                )
            )

        # Top Usuarios Riesgosos
        usr_sql = f"""
            WITH Scored AS ({sql})
            SELECT
                USUARIO_REGISTRADOR,
                COUNT(*) AS total_j,
                SUM(CASE WHEN nivel_riesgo IN ('ALTO', 'CRITICO') THEN 1 ELSE 0 END) AS crit_j,
                SUM(COALESCE(monto_total, 0.0)) AS total_amt,
                AVG(score_global) AS avg_s,
                SUM(CASE WHEN flag_mismo_usuario THEN 1 ELSE 0 END) AS sod_cnt,
                SUM(CASE WHEN flag_posible_fraccionamiento THEN 1 ELSE 0 END) AS split_cnt
            FROM Scored
            GROUP BY USUARIO_REGISTRADOR
            ORDER BY crit_j DESC, avg_s DESC
            LIMIT 5
        """
        usr_rows = self._conn.execute(usr_sql).fetchall()
        top_users: List[UserRiskDatamartItemDTO] = []
        for u in usr_rows:
            top_users.append(
                UserRiskDatamartItemDTO(
                    usuario=str(u[0] or "ANON"),
                    total_asientos=int(u[1] or 0),
                    asientos_alto_riesgo=int(u[2] or 0),
                    monto_total_registrado=round(float(u[3] or 0.0), 2),
                    score_promedio_usuario=round(float(u[4] or 0.0), 1),
                    casos_sod_count=int(u[5] or 0),
                    casos_fraccionamiento_count=int(u[6] or 0),
                )
            )

        return GoldExecutiveRiskDatamartDTO(
            total_asientos_analizados=int(total or 0),
            score_promedio_general=round(float(avg_score or 0.0), 1),
            total_asientos_criticos=int(critical_cnt or 0),
            total_monto_en_riesgo=round(float(risk_amt or 0.0), 2),
            top_asientos_criticos=top_journals,
            top_usuarios_riesgosos=top_users,
        )
