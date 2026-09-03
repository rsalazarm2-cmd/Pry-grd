"""Clasificador Semántico NLP para Auditoría Forense de Asientos Manuales.

Evalúa y puntúa la relevancia de columnas contables (Oracle EBS, SAP, NIIF)
e identifica la estrategia de Llave Primaria (Llave Natural ERP vs. Llave Sustituta Determinista).
"""

from typing import Dict, List, Tuple, Optional
from pydantic import BaseModel, Field


class ForensicColumnScoreDTO(BaseModel):
    """Evaluación semántica de relevancia forense por columna."""

    column_name: str = Field(description="Nombre original de la columna.")
    relevance_score: float = Field(description="Score de relevancia auditara (0.0 a 1.0).")
    vector_category: str = Field(description="SOD, TEMPORAL, FINANCIAL, SEMANTIC, ACCOUNTING, TECHNICAL.")
    is_high_relevance: bool = Field(description="Verdadero si score >= 0.70.")
    rationale: str = Field(description="Explicación semántica del score asignado.")


class ForensicNLPClassifier:
    """Clasificador Semántico y Detector de Llaves Primarias de Auditoría Forense."""

    HEADER_KEY_CANDIDATES: List[str] = [
        "FOLIO_ASIENTO", "FOLIO_ASIENTO_ID", "JE_HEADER_ID", "HEADER_ID",
        "BELNR", "NUMERO_DOCUMENTO", "ASIENTO_ID", "HEADER_NAME", "BATCH_ID",
    ]

    KEYWORDS_TAXONOMY: Dict[str, Tuple[List[str], float, str]] = {
        "SOD": (
            ["USUARIO", "CREATED_BY", "APPROVED_BY", "USER", "REGISTRADOR", "APROBADOR", "CREADOR", "AUTOR"],
            0.95, "Trazabilidad de Funciones Maker/Checker (Segregación SoD)",
        ),
        "TEMPORAL": (
            ["FECHA", "DATE", "PERIODO", "PERIOD", "CREATION_DATE", "ACCOUNTING_DATE", "CONTABILIZACION", "REGISTRO"],
            0.90, "Prueba de Corte Temporal, Backdating y Registros Nocturnos/Fin de Semana",
        ),
        "FINANCIAL": (
            ["CARGO", "ABONO", "DEBIT", "CREDIT", "DR", "CR", "ENTERED", "ACCOUNTED", "MONTO", "AMOUNT", "IMPORTE"],
            0.95, "Imputación Financiera de Partida Doble y Análisis de Ley de Benford",
        ),
        "SEMANTIC": (
            ["GLOSA", "DESCRIPTION", "DESCRIPCION", "CATEGORIA", "CATEGORY", "ORIGEN", "SOURCE", "CONCEPTO"],
            0.85, "Entropía Semántica y Detección de Glosas Evasivas/Patrones Sospechosos",
        ),
        "ACCOUNTING": (
            ["FOLIO", "ASIENTO", "HEADER", "BATCH", "CUENTA", "ACCOUNT", "MONEDA", "CURRENCY", "LIBRO", "LEDGER"],
            0.80, "Trazabilidad de Llaves Primarias y Estructura del Libro Mayor",
        ),
    }

    TECHNICAL_EXCLUSIONS: List[str] = [
        "ORG_ID", "LEDGER_ID", "SET_OF_BOOKS", "LAST_UPDATE", "LOGIN", "ATTRIBUTE", "CONTEXT",
        "OBJECT_VERSION", "RUN_ID", "CHART_OF_ACCOUNTS", "STATUS_CODE", "FLAG_TEMP",
    ]

    def detect_header_pk_strategy(self, column_list: List[str]) -> Tuple[str, str, str]:
        """Identifica la estrategia de Llave Primaria (Llave Natural ERP vs. Llave Sustituta Determinista).

        Returns:
            Tuple[strategy_type, key_column_or_sql_expr, description]
        """
        cols_upper = {c.upper(): c for c in column_list}

        # 1. Búsqueda de Llave Natural nativa del ERP
        for cand in self.HEADER_KEY_CANDIDATES:
            if cand in cols_upper:
                orig_name = cols_upper[cand]
                return (
                    "NATURAL_KEY",
                    orig_name,
                    f"🔑 Llave Natural ERP Detectada: {orig_name} (Sin parches sintéticos)",
                )

        # 2. Si no hay llave nativa, genera Llave Sustituta Determinista (DENSE_RANK)
        return (
            "DENSE_RANK_SURROGATE",
            "DENSE_RANK() OVER (ORDER BY FECHA_CONTABILIZACION, USUARIO_REGISTRADOR, GLOSA_ASIENTO)",
            "🛡️ Llave Sustituta Determinista: DENSE_RANK sobre Atributos Transaccionales (Estándar Kimball)",
        )

    def classify_column(self, col_name: str) -> ForensicColumnScoreDTO:
        """Calcula el score de relevancia forense (0.0 a 1.0) para una columna."""
        col_upper = (col_name or "").upper()

        if any(tech in col_upper for tech in self.TECHNICAL_EXCLUSIONS):
            return ForensicColumnScoreDTO(
                column_name=col_name,
                relevance_score=0.20,
                vector_category="TECHNICAL",
                is_high_relevance=False,
                rationale="Campo técnico de sistema ERP de bajo valor para auditoría forense.",
            )

        for cat, (keywords, score, rationale) in self.KEYWORDS_TAXONOMY.items():
            if any(kw in col_upper for kw in keywords):
                return ForensicColumnScoreDTO(
                    column_name=col_name,
                    relevance_score=score,
                    vector_category=cat,
                    is_high_relevance=score >= 0.70,
                    rationale=rationale,
                )

        return ForensicColumnScoreDTO(
            column_name=col_name,
            relevance_score=0.40,
            vector_category="GENERIC",
            is_high_relevance=False,
            rationale="Atributo secundario no crítico para vectores de riesgo forense.",
        )

    def classify_dataset_columns(self, column_list: List[str]) -> List[ForensicColumnScoreDTO]:
        """Clasifica todas las columnas del dataset y las retorna ordenadas por relevancia."""
        scores = [self.classify_column(col) for col in column_list]
        return sorted(scores, key=lambda x: x.relevance_score, reverse=True)
