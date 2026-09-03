"""Analizador Forense Universal de la Ley de Benford en DuckDB (Estándar Nigrini Enterprise).

Librería de nivel producción inmune a SQL Injection, con extracción por matemática
vectorial SIMD pura (C++ Speed) y conteo independiente de muestras para el 2º dígito.
"""

import math
import re
from typing import List, Dict, Tuple
import duckdb
from src.audit.domain.benford_dto import BenfordDigitDTO, BenfordAnalysisResultDTO


class BenfordAnalyzer:
    """Motor analítico de auditoría forense universal de la Ley de Benford."""

    def __init__(self, conn: duckdb.DuckDBPyConnection) -> None:
        self._conn = conn

    @staticmethod
    def sanitize_identifier(identifier: str) -> str:
        """Previene inyección SQL sanitizando identificadores de tabla y columna."""
        clean = re.sub(r"[^a-zA-Z0-9_.]", "", identifier or "")
        return clean if clean else "table_target"

    @staticmethod
    def get_expected_first_digit_freq(digit: int) -> float:
        """Porcentaje teórico Benford para el 1er dígito (1-9)."""
        return math.log10(1.0 + 1.0 / digit) * 100.0 if 1 <= digit <= 9 else 0.0

    @staticmethod
    def get_expected_second_digit_freq(digit: int) -> float:
        """Porcentaje teórico Benford para el 2º dígito (0-9)."""
        if digit < 0 or digit > 9:
            return 0.0
        return sum(math.log10(1.0 + 1.0 / (10 * d1 + digit)) for d1 in range(1, 10)) * 100.0

    @staticmethod
    def get_expected_two_digits_freq(d12: int) -> float:
        """Porcentaje teórico Benford para los 2 primeros dígitos (10-99)."""
        return math.log10(1.0 + 1.0 / d12) * 100.0 if 10 <= d12 <= 99 else 0.0

    def get_analyzable_numeric_columns(self, table_name: str) -> List[str]:
        """Descubre automáticamente todas las columnas numéricas auditables en la tabla."""
        clean_tbl = self.sanitize_identifier(table_name)
        try:
            res = self._conn.execute(f"SELECT * FROM {clean_tbl} LIMIT 0")
            num_types = ["DOUBLE", "FLOAT", "BIGINT", "INTEGER", "DECIMAL", "HUGEINT", "REAL"]
            return [col[0] for col in res.description if any(t in str(col[1]).upper() for t in num_types)]
        except Exception:
            return []

    def _resolve_target_column(self, table_name: str, requested_col: str) -> Tuple[str, List[str]]:
        cols = self.get_analyzable_numeric_columns(table_name)
        if not cols:
            try:
                res = self._conn.execute(f"SELECT * FROM {self.sanitize_identifier(table_name)} LIMIT 0")
                cols = [c[0] for c in res.description]
            except Exception:
                cols = [self.sanitize_identifier(requested_col)]

        cols_upper = {c.upper(): c for c in cols}
        clean_req = self.sanitize_identifier(requested_col).upper()
        if clean_req in cols_upper:
            return cols_upper[clean_req], cols

        for cand in ["CARGO_MONEDA_FUNCIONAL", "CARGO", "MONTO", "TOTAL_CARGOS_CABECERA", "ENTERED_DR"]:
            if cand in cols_upper:
                return cols_upper[cand], cols
        return cols[0], cols

    def analyze_column(self, table_name: str, column_name: str = "CARGO_MONEDA_FUNCIONAL") -> BenfordAnalysisResultDTO:
        """Ejecuta el análisis forense Benford con optimización vectorial matemática SIMD."""
        clean_tbl = self.sanitize_identifier(table_name)
        target_col, analyzable_cols = self._resolve_target_column(clean_tbl, column_name)
        clean_col = self.sanitize_identifier(target_col)

        # Extracción matemática pura: LOG10 + FLOOR + POWER (Velocidad C++ SIMD)
        sql = f"""
            WITH ValidAmounts AS (
                SELECT ABS(TRY_CAST("{clean_col}" AS DOUBLE)) AS val
                FROM {clean_tbl}
                WHERE "{clean_col}" IS NOT NULL AND TRY_CAST("{clean_col}" AS DOUBLE) > 0
            ),
            MathDigits AS (
                SELECT
                    CAST(FLOOR(ROUND(val / POWER(10, FLOOR(LOG10(val))), 6)) AS INT) AS d1,
                    CAST(FLOOR(ROUND(val / POWER(10, FLOOR(LOG10(val)) - 1), 6)) AS INT) % 10 AS d2,
                    CAST(FLOOR(ROUND(val / POWER(10, FLOOR(LOG10(val)) - 1), 6)) AS INT) AS d12
                FROM ValidAmounts
            )
            SELECT d1, d2, d12, COUNT(*) FROM MathDigits WHERE d1 BETWEEN 1 AND 9 GROUP BY d1, d2, d12
        """
        try:
            rows = self._conn.execute(sql).fetchall()
        except Exception:
            return BenfordAnalysisResultDTO(column_analyzed=clean_col, analyzable_columns=analyzable_cols)

        if not rows:
            return BenfordAnalysisResultDTO(column_analyzed=clean_col, analyzable_columns=analyzable_cols)

        d1_counts: Dict[int, int] = {i: 0 for i in range(1, 10)}
        d2_counts: Dict[int, int] = {i: 0 for i in range(0, 10)}
        d12_counts: Dict[int, int] = {}
        total_d1_samples, total_d2_samples = 0, 0

        for d1, d2, d12, cnt in rows:
            if d1 and 1 <= d1 <= 9:
                d1_counts[d1] += cnt
                total_d1_samples += cnt
            if d2 is not None and 0 <= d2 <= 9:
                d2_counts[d2] += cnt
                total_d2_samples += cnt
            if d12 and 10 <= d12 <= 99:
                d12_counts[d12] = d12_counts.get(d12, 0) + cnt

        if total_d1_samples == 0:
            return BenfordAnalysisResultDTO(column_analyzed=clean_col, analyzable_columns=analyzable_cols)

        first_digit_list, anomalous_digits = [], []
        chi_square_accum, mad_accum = 0.0, 0.0

        for d in range(1, 10):
            cnt = d1_counts[d]
            act_freq = (cnt / total_d1_samples) * 100.0
            exp_freq = self.get_expected_first_digit_freq(d)
            dev = abs(act_freq - exp_freq)
            mad_accum += abs((act_freq / 100.0) - (exp_freq / 100.0))
            is_anom = dev > 5.0
            if is_anom:
                anomalous_digits.append(d)
            exp_cnt = (exp_freq / 100.0) * total_d1_samples
            if exp_cnt > 0:
                chi_square_accum += ((cnt - exp_cnt) ** 2) / exp_cnt
            first_digit_list.append(
                BenfordDigitDTO(
                    digit=d, expected_freq=round(exp_freq, 2), actual_freq=round(act_freq, 2),
                    actual_count=cnt, deviation=round(dev, 2), is_anomalous=is_anom,
                )
            )

        mad_score = round(mad_accum / 9.0, 4)
        conformity = (
            "CONFORMIDAD_ESTRECHA" if mad_score <= 0.006
            else "CONFORMIDAD_ACEPTABLE" if mad_score <= 0.012
            else "CONFORMIDAD_MARGINAL" if mad_score <= 0.015
            else "NO_CONFORME_ANOMALO"
        )

        d2_denom = total_d2_samples if total_d2_samples > 0 else total_d1_samples
        second_digit_list = [
            BenfordDigitDTO(
                digit=d, expected_freq=round(self.get_expected_second_digit_freq(d), 2),
                actual_freq=round((d2_counts[d] / d2_denom) * 100.0, 2), actual_count=d2_counts[d],
                deviation=round(abs(((d2_counts[d] / d2_denom) * 100.0) - self.get_expected_second_digit_freq(d)), 2),
                is_anomalous=abs(((d2_counts[d] / d2_denom) * 100.0) - self.get_expected_second_digit_freq(d)) > 5.0,
            ) for d in range(0, 10)
        ]

        top_two_digits = []
        for d12, cnt in sorted(d12_counts.items(), key=lambda x: x[1], reverse=True)[:5]:
            act_f = (cnt / total_d1_samples) * 100.0
            exp_f = self.get_expected_two_digits_freq(d12)
            top_two_digits.append(
                BenfordDigitDTO(
                    digit=d12, expected_freq=round(exp_f, 2), actual_freq=round(act_f, 2),
                    actual_count=cnt, deviation=round(abs(act_f - exp_f), 2), is_anomalous=abs(act_f - exp_f) > 2.0,
                )
            )

        return BenfordAnalysisResultDTO(
            column_analyzed=clean_col, total_samples=total_d1_samples, chi_square_stat=round(chi_square_accum, 2),
            mad_score=mad_score, mad_conformity_level=conformity,
            is_distribution_suspicious=conformity == "NO_CONFORME_ANOMALO" or chi_square_accum > 15.51,
            first_digit_analysis=first_digit_list, second_digit_analysis=second_digit_list,
            top_two_digits_anomalies=top_two_digits, anomalous_digits=anomalous_digits,
            analyzable_columns=analyzable_cols,
        )
