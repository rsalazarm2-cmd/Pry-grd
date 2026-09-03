"""Profiler Especializado de Calidad Contable para la Capa Plata.

Calcula métricas de calidad y anomalías financieras ($)
exclusivamente sobre datos Parquet Plata limpios y estandarizados (33 campos).
"""
import duckdb
from pathlib import Path
from pydantic import BaseModel, Field


class SilverQualitySummaryDTO(BaseModel):
    total_silver_rows: int = 0
    total_debit_amount: float = 0.0
    total_credit_amount: float = 0.0
    sod_mismatches_count: int = 0
    sod_mismatches_amount: float = 0.0
    sod_rapid_approval_count: int = 0
    sod_rapid_approval_amount: float = 0.0
    round_amounts_count: int = 0
    round_amounts_amount: float = 0.0
    weekend_entries_count: int = 0
    weekend_entries_amount: float = 0.0
    imbalances_count: int = 0
    imbalances_amount: float = 0.0
    manual_entries_count: int = 0
    automatic_entries_count: int = 0


def compute_silver_quality_profile(conn: duckdb.DuckDBPyConnection, silver_parquet_path: Path) -> SilverQualitySummaryDTO:
    """Calcula el perfil de calidad contable sobre la Capa Plata."""
    safe_path_str = str(silver_parquet_path.resolve()).replace("'", "''")
    if not silver_parquet_path.exists():
        return SilverQualitySummaryDTO()

    try:
        schema_rows = conn.execute(f"DESCRIBE SELECT * FROM read_parquet('{safe_path_str}')").fetchall()
        cols = [r[0].upper() for r in schema_rows]

        has_col = lambda c: c in cols

        dr = '"CARGO_MONEDA_FUNCIONAL"' if has_col("CARGO_MONEDA_FUNCIONAL") else '0.0'
        cr = '"ABONO_MONEDA_FUNCIONAL"' if has_col("ABONO_MONEDA_FUNCIONAL") else '0.0'
        folio = '"FOLIO_ASIENTO"' if has_col("FOLIO_ASIENTO") else 'NULL'
        maker = '"USUARIO_REGISTRADOR"' if has_col("USUARIO_REGISTRADOR") else 'NULL'
        checker = '"USUARIO_APROBADOR"' if has_col("USUARIO_APROBADOR") else 'NULL'
        pdate = '"FECHA_CONTABILIZACION"' if has_col("FECHA_CONTABILIZACION") else 'NULL'
        cdate = '"FECHA_REGISTRO_CONTABLE"' if has_col("FECHA_REGISTRO_CONTABLE") else 'NULL'
        origen = '"TIPO_RIESGO_ORIGEN"' if has_col("TIPO_RIESGO_ORIGEN") else 'NULL'

        total_rows = conn.execute(f"SELECT COUNT(*) FROM read_parquet('{safe_path_str}')").fetchone()[0]

        # 1. Totales Financieros
        tot_query = f"SELECT SUM(COALESCE(TRY_CAST({dr} AS DOUBLE), 0)), SUM(COALESCE(TRY_CAST({cr} AS DOUBLE), 0)) FROM read_parquet('{safe_path_str}')"
        row_tot = conn.execute(tot_query).fetchone()
        tot_dr, tot_cr = float(row_tot[0] or 0.0), float(row_tot[1] or 0.0)

        # 2. Descuadres
        a1_count, a1_amt = 0, 0.0
        if has_col("FOLIO_ASIENTO") and has_col("CARGO_MONEDA_FUNCIONAL"):
            imb_q = f"SELECT COUNT(*), COALESCE(SUM(diff), 0.0) FROM (SELECT {folio}, ABS(SUM(COALESCE(TRY_CAST({dr} AS DOUBLE), 0)) - SUM(COALESCE(TRY_CAST({cr} AS DOUBLE), 0))) AS diff FROM read_parquet('{safe_path_str}') GROUP BY {folio} HAVING diff > 0.01)"
            row_imb = conn.execute(imb_q).fetchone()
            a1_count, a1_amt = int(row_imb[0] or 0), float(row_imb[1] or 0.0)

        # 3. SoD Creador = Aprobador
        sod_c, sod_a = 0, 0.0
        if has_col("USUARIO_REGISTRADOR") and has_col("USUARIO_APROBADOR"):
            sod_q = f"SELECT COUNT(*), COALESCE(SUM(TRY_CAST({dr} AS DOUBLE)), 0.0) FROM read_parquet('{safe_path_str}') WHERE LOWER(TRIM(CAST({maker} AS VARCHAR))) = LOWER(TRIM(CAST({checker} AS VARCHAR))) AND {maker} IS NOT NULL AND CAST({maker} AS VARCHAR) != ''"
            row_sod = conn.execute(sod_q).fetchone()
            sod_c, sod_a = int(row_sod[0] or 0), float(row_sod[1] or 0.0)

        # 4. Aprobación Rápida < 60s
        rap_c, rap_a = 0, 0.0
        if has_col("FECHA_CONTABILIZACION") and has_col("FECHA_REGISTRO_CONTABLE"):
            rap_q = f"SELECT COUNT(*), COALESCE(SUM(TRY_CAST({dr} AS DOUBLE)), 0.0) FROM read_parquet('{safe_path_str}') WHERE ABS(EPOCH(TRY_CAST({pdate} AS TIMESTAMP)) - EPOCH(TRY_CAST({cdate} AS TIMESTAMP))) < 60 AND {pdate} IS NOT NULL AND {cdate} IS NOT NULL"
            row_rap = conn.execute(rap_q).fetchone()
            rap_c, rap_a = int(row_rap[0] or 0), float(row_rap[1] or 0.0)

        # 5. Montos Redondos
        rnd_c, rnd_a = 0, 0.0
        if has_col("CARGO_MONEDA_FUNCIONAL"):
            rnd_q = f"SELECT COUNT(*), COALESCE(SUM(TRY_CAST({dr} AS DOUBLE)), 0.0) FROM read_parquet('{safe_path_str}') WHERE COALESCE(TRY_CAST({dr} AS DOUBLE), 0) > 100000 AND (TRY_CAST({dr} AS DOUBLE) % 100000 = 0)"
            row_rnd = conn.execute(rnd_q).fetchone()
            rnd_c, rnd_a = int(row_rnd[0] or 0), float(row_rnd[1] or 0.0)

        # 6. Fines de Semana
        wnd_c, wnd_a = 0, 0.0
        if has_col("FECHA_REGISTRO_CONTABLE"):
            wnd_q = f"SELECT COUNT(*), COALESCE(SUM(TRY_CAST({dr} AS DOUBLE)), 0.0) FROM read_parquet('{safe_path_str}') WHERE DAYOFWEEK(TRY_CAST({cdate} AS TIMESTAMP)) IN (0, 6)"
            row_wnd = conn.execute(wnd_q).fetchone()
            wnd_c, wnd_a = int(row_wnd[0] or 0), float(row_wnd[1] or 0.0)

        # 7. Distribución Manual vs Automático
        man_c, aut_c = 0, 0
        if has_col("TIPO_RIESGO_ORIGEN"):
            row_org = conn.execute(f"SELECT SUM(CASE WHEN {origen} = 'MANUAL' THEN 1 ELSE 0 END), SUM(CASE WHEN {origen} = 'AUTOMATICO' THEN 1 ELSE 0 END) FROM read_parquet('{safe_path_str}')").fetchone()
            man_c, aut_c = int(row_org[0] or 0), int(row_org[1] or 0)

        return SilverQualitySummaryDTO(
            total_silver_rows=total_rows,
            total_debit_amount=tot_dr,
            total_credit_amount=tot_cr,
            sod_mismatches_count=sod_c,
            sod_mismatches_amount=sod_a,
            sod_rapid_approval_count=rap_c,
            sod_rapid_approval_amount=rap_a,
            round_amounts_count=rnd_c,
            round_amounts_amount=rnd_a,
            weekend_entries_count=wnd_c,
            weekend_entries_amount=wnd_a,
            imbalances_count=a1_count,
            imbalances_amount=a1_amt,
            manual_entries_count=man_c,
            automatic_entries_count=aut_c,
        )
    except Exception:
        return SilverQualitySummaryDTO()
