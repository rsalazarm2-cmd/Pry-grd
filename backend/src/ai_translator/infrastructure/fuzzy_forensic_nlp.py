"""Clasificador NLP por Similitud Difusa (Fuzzy Matching) con Métricas Empíricas de Profiling.

Combina Similitud Difusa de Tokens con Ratios de Unicidad de DuckDB para vetar categorías.
"""

from difflib import SequenceMatcher
from typing import Dict, List, Optional, Tuple
from pydantic import BaseModel, Field
from src.ai_translator.infrastructure.duckdb_profiler import ColumnMetricsDTO


class FuzzyScoreDTO(BaseModel):
    """Resultado de clasificación difusa semántica y empírica por columna."""

    column_name: str = Field(description="Nombre original de la columna.")
    relevance_score: float = Field(description="Score de relevancia forense (0.0 a 1.0).")
    vector_category: str = Field(description="SOD, TEMPORAL, FINANCIAL, SEMANTIC, ACCOUNTING, TECHNICAL.")
    is_high_relevance: bool = Field(description="Verdadero si el score es >= 0.70.")
    similarity_confidence: float = Field(description="Grado de confianza de similitud difusa (0.0 a 1.0).")
    rationale: str = Field(description="Justificación semántica generada por la IA.")


class FuzzyForensicNLPClassifier:
    """Motor de Inferencia NLP Difuso + Empírico para Auditoría Forense."""

    AUDIT_CONCEPTS: Dict[str, Tuple[List[str], float, str]] = {
        "SOD": (
            ["usuario", "user", "creator", "approver", "author", "registrador", "aprobador", "creador", "autor", "usr", "createdby"],
            0.95, "Trazabilidad de Segregación de Funciones Maker/Checker (SoD)",
        ),
        "TEMPORAL": (
            ["fecha", "date", "periodo", "period", "time", "creation", "accounting", "posted", "registro", "contabilizacion"],
            0.90, "Vectores de Corte Temporal, Backdating y Registros Nocturnos",
        ),
        "FINANCIAL": (
            ["cargo", "abono", "debit", "credit", "entered", "accounted", "monto", "amount", "importe", "valor", "dr", "cr", "amt"],
            0.95, "Partida Doble, Verificación de Montos y Ley de Benford",
        ),
        "SEMANTIC": (
            ["glosa", "description", "descripcion", "concepto", "category", "categoria", "origen", "source", "memo", "notes"],
            0.85, "Entropía Semántica y Detección de Glosas Evasivas/Sospechosas",
        ),
        "ACCOUNTING": (
            ["folio", "asiento", "header", "batch", "cuenta", "account", "moneda", "currency", "libro", "ledger", "belnr", "doc"],
            0.80, "Llaves Primarias y Estructura del Libro Mayor Contable",
        ),
    }

    TECHNICAL_TOKENS: List[str] = [
        "org_id", "ledger_id", "set_of_books", "last_update", "login", "attribute", "context",
        "object_version", "run_id", "chart_of_accounts", "status_code", "flag_temp",
    ]

    def _fuzzy_similarity(self, text_a: str, text_b: str) -> float:
        return SequenceMatcher(None, text_a.lower(), text_b.lower()).ratio()

    def classify_column(self, col_name: str, metrics: Optional[ColumnMetricsDTO] = None) -> FuzzyScoreDTO:
        col_clean = (col_name or "").strip().lower()

        # Veto de atributos de sistema
        for tech in self.TECHNICAL_TOKENS:
            if self._fuzzy_similarity(col_clean, tech) > 0.75 or tech in col_clean:
                return FuzzyScoreDTO(
                    column_name=col_name,
                    relevance_score=0.20,
                    vector_category="TECHNICAL",
                    is_high_relevance=False,
                    similarity_confidence=0.90,
                    rationale="Atributo técnico de sistema ERP de bajo valor auditara.",
                )

        best_category = "GENERIC"
        best_score = 0.40
        best_confidence = 0.0
        best_rationale = "Atributo secundario no crítico para vectores forenses."
        tokens = col_clean.replace("_", " ").split()

        for cat, (keywords, concept_weight, rationale) in self.AUDIT_CONCEPTS.items():
            for kw in keywords:
                for token in tokens:
                    sim = self._fuzzy_similarity(token, kw)
                    if sim > best_confidence:
                        best_confidence = sim
                        if sim >= 0.65:
                            best_category = cat
                            best_score = concept_weight
                            best_rationale = rationale

        # Veto Empírico: Si DuckDB reporta que es una categoría de baja cardinalidad (< 5% distintas),
        # NUNCA clasificarla como ACCOUNTING PK para evitar productos cartesianos.
        if metrics and metrics.is_low_cardinality_category:
            if best_category == "ACCOUNTING":
                best_category = "SEMANTIC"
                best_score = 0.60
            best_rationale += f" (Veto Empírico DuckDB: {col_name} es una dimensión/categoría con {round(metrics.uniqueness_ratio*100, 2)}% distintas. Descartada como PK)."

        return FuzzyScoreDTO(
            column_name=col_name,
            relevance_score=best_score,
            vector_category=best_category,
            is_high_relevance=best_score >= 0.70,
            similarity_confidence=round(best_confidence, 2),
            rationale=best_rationale,
        )

    def classify_dataset_columns(
        self, column_list: List[str], metrics_map: Optional[Dict[str, ColumnMetricsDTO]] = None
    ) -> List[FuzzyScoreDTO]:
        scores = [
            self.classify_column(col, metrics_map.get(col) if metrics_map else None)
            for col in column_list
        ]
        return sorted(scores, key=lambda x: x.relevance_score, reverse=True)
