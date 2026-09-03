"""Motor DuckDB Vectorizado de Auditoría Forense (CU-16, CU-17, CU-18, CU-19).

Ejecuta análisis de riesgos sobre Parquet de la Capa Plata:
- Violaciones de SoD y Aprobaciones Exprés (CU-16)
- Trampas Forenses: Medianoche, Montos Redondos y Fin de Semana (CU-17)
- Anomalías Cut-off y Backdating (CU-18)
- Financial Integrity Risk Score Ponderado (CU-19)
"""

import logging
from pathlib import Path
import duckdb

from src.audit.domain.forensic_dto import (
    SodViolationDTO, ForensicTrapAlertDTO, CutoffAnomalyDTO,
    IntegrityRiskScoreDTO, ForensicAuditMatrixDTO,
)

logger = logging.getLogger(__name__)

def _safe(path: Path) -> str:
    return str(path.resolve()).replace("'", "''")

def _get_cols(conn: duckdb.DuckDBPyConnection, pq: str) -> dict:
    schema = conn.execute(f"DESCRIBE SELECT * FROM read_parquet('{pq}')").fetchall()
    return {r[0].upper(): r[0] for r in schema}


class ForensicAuditEngine:
    """Motor DuckDB de Auditoría Forense Avanzada."""

    def __init__(self, conn: duckdb.DuckDBPyConnection):
        self._conn = conn

    def run_full_forensic_audit(self, silver_path: Path) -> ForensicAuditMatrixDTO:
        if not silver_path.exists():
            return ForensicAuditMatrixDTO()

        sod_list = self.analyze_sod_violations(silver_path)
        trap_list = self.analyze_forensic_traps(silver_path)
        cutoff_list = self.analyze_cutoff_anomalies(silver_path)

        total_journals = self._conn.execute(f"SELECT COUNT(*) FROM read_parquet('{_safe(silver_path)}')").fetchone()[0]

        # CU-19: Cálculo de Score Ponderado (100 = Cero Riesgo)
        penalty = (len(sod_list) * 25.0) + (len(trap_list) * 10.0) + (len(cutoff_list) * 15.0)
        score_val = max(0.0, round(100.0 - penalty, 2))

        risk_level = "BAJO"
        if score_val < 50.0: risk_level = "CRITICO"
        elif score_val < 75.0: risk_level = "ALTO"
        elif score_val < 90.0: risk_level = "MEDIO"

        score_dto = IntegrityRiskScoreDTO(
            total_asientos_analizados=total_journals,
            financial_integrity_score=score_val,
            nivel_riesgo_global=risk_level,
            sod_violations_count=len(sod_list),
            forensic_traps_count=len(trap_list),
            cutoff_anomalies_count=len(cutoff_list),
        )

        return ForensicAuditMatrixDTO(
            score=score_dto,
            sod_violations=sod_list,
            forensic_traps=trap_list,
            cutoff_anomalies=cutoff_list,
        )

    def analyze_sod_violations(self, silver_path: Path, limit: int = 100) -> list[SodViolationDTO]:
        pq = _safe(silver_path)
        cols = _get_cols(self._conn, pq)
        reg_c, app_c = cols.get("USUARIO_REGISTRADOR"), cols.get("USUARIO_APROBADOR")
        if not reg_c or not app_c: return []

        folio_c = cols.get("FOLIO_ASIENTO", "'SIN_FOLIO'")
        f_reg_c = cols.get("FECHA_REGISTRO_CONTABLE", "'N/A'")
        dr_c = cols.get("CARGO_MONEDA_FUNCIONAL", "0.0")

        q = f"""
            SELECT {folio_c}, {reg_c}, {app_c}, CAST({f_reg_c} AS VARCHAR), COALESCE(SUM(TRY_CAST({dr_c} AS DOUBLE)), 0.0)
            FROM read_parquet('{pq}')
            WHERE LOWER(TRIM(CAST({reg_c} AS VARCHAR))) = LOWER(TRIM(CAST({app_c} AS VARCHAR)))
              AND {reg_c} IS NOT NULL AND CAST({reg_c} AS VARCHAR) != ''
            GROUP BY {folio_c}, {reg_c}, {app_c}, {f_reg_c} LIMIT {limit}
        """
        rows = self._conn.execute(q).fetchall()
        return [SodViolationDTO(
            folio_asiento=str(r[0]), usuario_registrador=str(r[1]), usuario_aprobador=str(r[2]),
            fecha_registro=str(r[3]), monto_total=float(r[4]), tipo_violacion="MAKER_EQUAL_CHECKER", nivel_riesgo="ALTO"
        ) for r in rows]

    def analyze_forensic_traps(self, silver_path: Path, limit: int = 100) -> list[ForensicTrapAlertDTO]:
        pq = _safe(silver_path)
        cols = _get_cols(self._conn, pq)
        folio_c = cols.get("FOLIO_ASIENTO", "'SIN_FOLIO'")
        dr_c = cols.get("CARGO_MONEDA_FUNCIONAL", "0.0")
        f_reg_c = cols.get("FECHA_REGISTRO_CONTABLE")

        traps = []
        if f_reg_c:
            # 1. Trampa Medianoche 00:00:00
            q_mid = f"""
                SELECT {folio_c}, CAST({f_reg_c} AS VARCHAR), COALESCE(SUM(TRY_CAST({dr_c} AS DOUBLE)), 0.0)
                FROM read_parquet('{pq}')
                WHERE CAST({f_reg_c} AS VARCHAR) LIKE '%00:00:00%'
                GROUP BY {folio_c}, {f_reg_c} LIMIT {limit}
            """
            for r in self._conn.execute(q_mid).fetchall():
                traps.append(ForensicTrapAlertDTO(
                    folio_asiento=str(r[0]), tipo_trampa="MIDNIGHT_STAMP",
                    descripcion_trampa="Registro en horario exacto 00:00:00 (Posible Script Automatizado)",
                    fecha_registro=str(r[1]), monto=float(r[2]), nivel_riesgo="MEDIO"
                ))

            # 2. Registros en Fin de Semana (Sábado=6, Domingo=0)
            q_wknd = f"""
                SELECT {folio_c}, CAST({f_reg_c} AS VARCHAR), COALESCE(SUM(TRY_CAST({dr_c} AS DOUBLE)), 0.0)
                FROM read_parquet('{pq}')
                WHERE DAYOFWEEK(TRY_CAST({f_reg_c} AS TIMESTAMP)) IN (0, 6)
                GROUP BY {folio_c}, {f_reg_c} LIMIT {limit}
            """
            for r in self._conn.execute(q_wknd).fetchall():
                traps.append(ForensicTrapAlertDTO(
                    folio_asiento=str(r[0]), tipo_trampa="WEEKEND_REGISTRATION",
                    descripcion_trampa="Registro Contable realizado en Fin de Semana (Sábado / Domingo)",
                    fecha_registro=str(r[1]), monto=float(r[2]), nivel_riesgo="ALTO"
                ))

        # 3. Montos Redondos Sospechosos (> $100K múltiplos exactos)
        q_rnd = f"""
            SELECT {folio_c}, 'N/A', SUM(TRY_CAST({dr_c} AS DOUBLE)) AS m
            FROM read_parquet('{pq}')
            GROUP BY {folio_c}
            HAVING m >= 100000.0 AND m % 10000.0 = 0
            LIMIT {limit}
        """
        for r in self._conn.execute(q_rnd).fetchall():
            traps.append(ForensicTrapAlertDTO(
                folio_asiento=str(r[0]), tipo_trampa="ROUND_AMOUNT",
                descripcion_trampa="Monto redondo sospechoso mayor a $100,000",
                fecha_registro=str(r[1]), monto=float(r[2]), nivel_riesgo="ALTO"
            ))

        return traps[:limit]

    def analyze_cutoff_anomalies(self, silver_path: Path, limit: int = 100) -> list[CutoffAnomalyDTO]:
        pq = _safe(silver_path)
        cols = _get_cols(self._conn, pq)
        f_reg_c, f_cont_c = cols.get("FECHA_REGISTRO_CONTABLE"), cols.get("FECHA_CONTABILIZACION")
        if not f_reg_c or not f_cont_c: return []

        folio_c = cols.get("FOLIO_ASIENTO", "'SIN_FOLIO'")
        periodo_c = cols.get("PERIODO_CONTABLE", "'N/A'")

        q = f"""
            SELECT {folio_c}, CAST({periodo_c} AS VARCHAR), CAST({f_cont_c} AS VARCHAR), CAST({f_reg_c} AS VARCHAR),
                   ABS(DATEDIFF('day', TRY_CAST({f_reg_c} AS TIMESTAMP), TRY_CAST({f_cont_c} AS TIMESTAMP))) AS diff
            FROM read_parquet('{pq}')
            WHERE ABS(DATEDIFF('day', TRY_CAST({f_reg_c} AS TIMESTAMP), TRY_CAST({f_cont_c} AS TIMESTAMP))) > 30
            GROUP BY {folio_c}, {periodo_c}, {f_cont_c}, {f_reg_c} LIMIT {limit}
        """
        rows = self._conn.execute(q).fetchall()
        return [CutoffAnomalyDTO(
            folio_asiento=str(r[0]), periodo_contable=str(r[1]), fecha_contabilizacion=str(r[2]),
            fecha_registro=str(r[3]), diferencia_dias=int(r[4] or 0),
            descripcion=f"Descalce de corte temporal mayor a 30 días ({r[4]} días)", nivel_riesgo="ALTO"
        ) for r in rows]
