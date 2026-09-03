import duckdb
from decimal import Decimal
from typing import List
from audit_system.backend.domain.interfaces import IAuditRepository
from audit_system.backend.domain.entities import (
    AlertaDescuadreDTO,
    SegregacionFuncionesDTO,
    InformeIntegridadAuditoriaDTO,
)

def _get_parquet_cols(conn: duckdb.DuckDBPyConnection, parquet_path: str) -> list[str]:
    try:
        rows = conn.execute(f"DESCRIBE SELECT * FROM read_parquet('{parquet_path}')").fetchall()
        return [r[0] for r in rows]
    except Exception:
        return []

def _col_expr(cols: list[str], col_name: str, fallback_sql: str) -> str:
    return f'"{col_name}"' if col_name in cols else fallback_sql

class DuckDBAuditRepository(IAuditRepository):
    """
    Implementación del Repositorio de Auditoría Forense utilizando el motor vectorial DuckDB Nativo.
    Ejecuta SQL SIMD directo sobre archivos Parquet de la Capa Plata tolerante a esquemas dinámicos.
    """

    def consultar_descuadres_partida_doble(
        self, parquet_path: str, limite: int = 100
    ) -> List[AlertaDescuadreDTO]:
        conn = duckdb.connect(database=":memory:")
        cols = _get_parquet_cols(conn, parquet_path)
        
        folio_expr = _col_expr(cols, "FOLIO_ASIENTO", "'SIN_FOLIO'")
        libro_expr = _col_expr(cols, "NOMBRE_LIBRO_MAYOR", "'GL'")
        f_cont_expr = _col_expr(cols, "FECHA_CONTABILIZACION", "'N/A'")
        cargo_expr = _col_expr(cols, "CARGO_MONEDA_FUNCIONAL", "0.0")
        abono_expr = _col_expr(cols, "ABONO_MONEDA_FUNCIONAL", "0.0")
        cabecera_expr = _col_expr(cols, "TOTAL_ABONOS_CABECERA", cargo_expr)

        query = f"""
            SELECT 
                {folio_expr} AS FOLIO_ASIENTO,
                COALESCE(FIRST({libro_expr}), 'GL') AS LIBRO_CONTABLE,
                COALESCE(FIRST(CAST({f_cont_expr} AS VARCHAR)), 'N/A') AS PERIODO_CONTABLE,
                COALESCE(SUM(TRY_CAST({cargo_expr} AS DECIMAL(18,2))), 0.0) AS TOTAL_CARGOS,
                COALESCE(SUM(TRY_CAST({abono_expr} AS DECIMAL(18,2))), 0.0) AS TOTAL_ABONOS,
                COALESCE(FIRST(TRY_CAST({cabecera_expr} AS DECIMAL(18,2))), COALESCE(SUM(TRY_CAST({cargo_expr} AS DECIMAL(18,2))), 0.0)) AS TOTAL_CABECERA,
                ABS(COALESCE(SUM(TRY_CAST({cargo_expr} AS DECIMAL(18,2))), 0.0) - COALESCE(SUM(TRY_CAST({abono_expr} AS DECIMAL(18,2))), 0.0)) AS DIFERENCIA
            FROM read_parquet('{parquet_path}')
            GROUP BY {folio_expr}
            HAVING ABS(COALESCE(SUM(TRY_CAST({cargo_expr} AS DECIMAL(18,2))), 0.0) - COALESCE(SUM(TRY_CAST({abono_expr} AS DECIMAL(18,2))), 0.0)) > 0.01
            LIMIT {limite}
        """
        rows = conn.execute(query).fetchall()
        conn.close()

        return [
            AlertaDescuadreDTO(
                FOLIO_ASIENTO=str(r[0]),
                LIBRO_CONTABLE=str(r[1]),
                PERIODO_CONTABLE=str(r[2]),
                TOTAL_CARGOS_CALCULADO=Decimal(str(r[3])),
                TOTAL_ABONOS_CALCULADO=Decimal(str(r[4])),
                TOTAL_CARGOS_CABECERA=Decimal(str(r[5])),
                DIFERENCIA_DESCUADRE=Decimal(str(r[6])),
            )
            for r in rows
        ]

    def consultar_violaciones_segregacion_funciones(
        self, parquet_path: str, limite: int = 100
    ) -> List[SegregacionFuncionesDTO]:
        conn = duckdb.connect(database=":memory:")
        cols = _get_parquet_cols(conn, parquet_path)

        if "USUARIO_REGISTRADOR" not in cols or "USUARIO_APROBADOR" not in cols:
            conn.close()
            return []

        folio_expr = _col_expr(cols, "FOLIO_ASIENTO", "'SIN_FOLIO'")
        f_reg_expr = _col_expr(cols, "FECHA_REGISTRO_CONTABLE", "'N/A'")
        cargo_expr = _col_expr(cols, "CARGO_MONEDA_FUNCIONAL", "0.0")

        query = f"""
            SELECT DISTINCT
                {folio_expr} AS FOLIO_ASIENTO,
                "USUARIO_REGISTRADOR",
                "USUARIO_APROBADOR",
                COALESCE(FIRST(CAST({f_reg_expr} AS VARCHAR)), 'N/A') AS FECHA_REGISTRO,
                COALESCE(SUM(TRY_CAST({cargo_expr} AS DECIMAL(18,2))), 0.0) AS MONTO_TOTAL
            FROM read_parquet('{parquet_path}')
            WHERE LOWER(TRIM(CAST("USUARIO_REGISTRADOR" AS VARCHAR))) = LOWER(TRIM(CAST("USUARIO_APROBADOR" AS VARCHAR)))
              AND "USUARIO_REGISTRADOR" IS NOT NULL AND CAST("USUARIO_REGISTRADOR" AS VARCHAR) != ''
            GROUP BY {folio_expr}, "USUARIO_REGISTRADOR", "USUARIO_APROBADOR"
            LIMIT {limite}
        """
        rows = conn.execute(query).fetchall()
        conn.close()

        return [
            SegregacionFuncionesDTO(
                FOLIO_ASIENTO=str(r[0]),
                USUARIO_REGISTRADOR=str(r[1]),
                USUARIO_APROBADOR=str(r[2]),
                FECHA_REGISTRO=str(r[3]),
                MONTO_TOTAL_ASIENTO=Decimal(str(r[4])),
            )
            for r in rows
        ]

    def generar_informe_integridad_completo(
        self, parquet_path: str
    ) -> InformeIntegridadAuditoriaDTO:
        descuadres = self.consultar_descuadres_partida_doble(parquet_path)
        sod_violations = self.consultar_violaciones_segregacion_funciones(parquet_path)
        
        monto_descuadrado = sum((d.DIFERENCIA_DESCUADRE for d in descuadres), Decimal("0.00"))
        
        conn = duckdb.connect(database=":memory:")
        cols = _get_parquet_cols(conn, parquet_path)
        folio_expr = _col_expr(cols, "FOLIO_ASIENTO", "*")
        
        total_asientos = conn.execute(
            f"SELECT COUNT(DISTINCT {folio_expr}) FROM read_parquet('{parquet_path}')"
        ).fetchone()[0]
        conn.close()

        return InformeIntegridadAuditoriaDTO(
            total_asientos_analizados=total_asientos,
            total_descuadres_detectados=len(descuadres),
            total_violaciones_sod=len(sod_violations),
            monto_total_descuadrado=monto_descuadrado,
            alertas_descuadre=descuadres,
            alertas_sod=sod_violations,
        )
