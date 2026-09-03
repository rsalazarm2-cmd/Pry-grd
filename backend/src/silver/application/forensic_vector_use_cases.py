"""Casos de Uso para la Evaluación y Auditoría Forense de Asientos Manuales.

Orquesta la ejecución del Motor Vectorial en la Capa Plata y aplica
las reglas de análisis forense empresarial.
"""

from typing import List, Optional
import duckdb
from src.silver.domain.forensic_vector_dto import (
    ForensicAuditSummaryDTO,
    ForensicVectorRecordDTO,
    ForensicVectorTemporalDTO,
    ForensicVectorSODDTO,
    ForensicVectorSemanticoDTO,
    ForensicVectorMatematicoDTO,
    ForensicVectorAcumuladoDTO,
)
from src.silver.infrastructure.forensic_vector_engine import ForensicVectorEngine


class ForensicVectorUseCases:
    """Caso de Uso principal para el Motor Vectorial Forense."""

    def __init__(self, conn: duckdb.DuckDBPyConnection) -> None:
        """Inicializa los casos de uso con la conexión DuckDB.

        Args:
            conn: Conexión activa a DuckDB.
        """
        self._conn = conn
        self._engine = ForensicVectorEngine(conn)

    def run_forensic_summary(self, table_name: str = "silver_journals") -> ForensicAuditSummaryDTO:
        """Ejecuta la evaluación vectorial completa sobre la tabla Plata.

        Args:
            table_name: Tabla de origen en DuckDB.

        Returns:
            Resumen estadístico de las 5 dimensiones forenses.
        """
        return self._engine.execute_forensic_audit(table_name)

    def fetch_high_risk_records(
        self, table_name: str = "silver_journals", limit: int = 50
    ) -> List[ForensicVectorRecordDTO]:
        """Obtiene la lista de registros clasificados con mayor riesgo forense.

        Args:
            table_name: Tabla de origen.
            limit: Número máximo de registros a retornar.

        Returns:
            Lista de DTOs consolidados por asiento contable.
        """
        sql = self._engine.build_forensic_vector_query(table_name)
        top_sql = f"""
            WITH Analyzed AS ({sql})
            SELECT * FROM Analyzed
            ORDER BY score_preliminar DESC, CARGO_MONEDA_FUNCIONAL DESC
            LIMIT {limit}
        """
        rows = self._conn.execute(top_sql).fetchall()
        cols = [desc[0] for desc in self._conn.description]
        records: List[ForensicVectorRecordDTO] = []

        for r in rows:
            d = dict(zip(cols, r))
            rec = ForensicVectorRecordDTO(
                folio_asiento=str(d.get("FOLIO_ASIENTO", "N/A")),
                vector_temporal=ForensicVectorTemporalDTO(
                    flag_fin_semana=bool(d.get("flag_fin_semana", False)),
                    flag_horario_nocturno=bool(d.get("flag_horario_nocturno", False)),
                    dias_diferencia_creacion_gl=int(d.get("dias_diferencia", 0) or 0),
                ),
                vector_sod=ForensicVectorSODDTO(
                    flag_mismo_usuario=bool(d.get("flag_mismo_usuario", False)),
                    flag_aprobacion_flash=False,
                ),
                vector_semantico=ForensicVectorSemanticoDTO(
                    flag_glosa_sospechosa=bool(d.get("flag_glosa_sospechosa", False)),
                    longitud_glosa=int(d.get("longitud_glosa", 0) or 0),
                ),
                vector_matematico=ForensicVectorMatematicoDTO(
                    flag_monto_redondo=bool(d.get("flag_monto_redondo", False)),
                    primer_digito=int(d.get("primer_digito", 0) or 0),
                ),
                vector_acumulado=ForensicVectorAcumuladoDTO(
                    monto_acumulado_dia_usuario=float(d.get("monto_acumulado_dia", 0.0) or 0.0),
                    conteo_asientos_dia_usuario=int(d.get("conteo_asientos_dia", 0) or 0),
                    flag_posible_fraccionamiento=bool(d.get("flag_posible_fraccionamiento", False)),
                ),
                score_riesgo_preliminar=float(d.get("score_preliminar", 0.0) or 0.0),
            )
            records.append(rec)

        return records
