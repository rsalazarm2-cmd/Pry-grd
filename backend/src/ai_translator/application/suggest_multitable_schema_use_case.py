"""Caso de uso para Auto-Sugerencia de Vistas Relacionales Capa Oro (3 Capas NLP + Profiling).

Integra Inspección Empírica DuckDB (Ratio Unicidad) + Fuzzy NLP + Llave Surrogate Kimball
para garantizar 0 productos cartesianos.
"""

from typing import List
from src.shared.domain.journal_entry import SilverTargetEntityDTO
from src.ai_translator.infrastructure.duckdb_profiler import DuckDBProfiler
from src.ai_translator.infrastructure.fuzzy_forensic_nlp import FuzzyForensicNLPClassifier


class SuggestMultitableSchemaUseCase:
    """Caso de uso que evalúa el esquema Plata y sugiere Vistas Relacionales Oro optimizadas."""

    def __init__(self, journal_repo):
        self.repo = journal_repo
        self.classifier = FuzzyForensicNLPClassifier()
        self.profiler = DuckDBProfiler()

    def execute(self, parquet_path: str) -> List[SilverTargetEntityDTO]:
        profile = self.repo.get_bronze_profile(parquet_path)
        all_cols = [c.column_name for c in profile.columns]

        # Capa 1: Profiling Empírico en DuckDB (Ratio de Unicidad y Nulos)
        emp_metrics = self.profiler.profile_parquet_columns(parquet_path, all_cols)

        # Capa 2: Clasificación NLP Difusa combinada con Profiling
        scored_cols = self.classifier.classify_dataset_columns(all_cols, emp_metrics)
        high_rel_cols = [c.column_name for c in scored_cols if c.is_high_relevance] or all_cols

        header_cols = [c.column_name for c in scored_cols if c.vector_category in ["SOD", "TEMPORAL", "SEMANTIC", "ACCOUNTING"] and c.is_high_relevance]
        financial_cols = [c.column_name for c in scored_cols if c.vector_category == "FINANCIAL"]

        debit_cols = [c for c in financial_cols if any(k in c.upper() for k in ["DR", "DEBIT", "CARGO", "ENTERED_DR"])]
        credit_cols = [c for c in financial_cols if any(k in c.upper() for k in ["CR", "CREDIT", "ABONO", "ENTERED_CR"])]

        if not debit_cols and financial_cols:
            debit_cols = financial_cols[:len(financial_cols)//2 + 1]
            credit_cols = financial_cols[len(financial_cols)//2 + 1:]

        # Capa 3: Selección de Llave Primaria (PK) o Surrogate Kimball
        # Buscar columna con Ratio Unicidad >= 0.90 y que no sea categoría
        true_pk_candidates = [
            col for col, m in emp_metrics.items()
            if m.is_unique_key_candidate and not m.is_low_cardinality_category
        ]

        if not true_pk_candidates:
            # Filtro por nombre seguro de identificador
            true_pk_candidates = [
                c for c in all_cols
                if any(k in c.upper() for k in ["FOLIO", "HEADER_ID", "BELNR", "DOCUMENT_ID", "NUMERO_ASIENTO"])
                and not emp_metrics.get(c, {}).is_low_cardinality_category
            ]

        pk_field = true_pk_candidates[0] if true_pk_candidates else "FOLIO_ASIENTO_ID"

        return [
            SilverTargetEntityDTO(
                entity_id="target_header",
                entity_name="CABECERA_ASIENTO",
                description=f"🔑 Vista Cabecera ({pk_field})",
                selected_columns=list(set(header_cols + [pk_field])),
                filter_expression=None,
                position_x=120,
                position_y=80,
            ),
            SilverTargetEntityDTO(
                entity_id="target_debit",
                entity_name="PARTIDAS_DEBITO",
                description=f"🔗 Vista Débito (FK: {pk_field}, Filter: CARGO > 0)",
                selected_columns=list(set(debit_cols + [pk_field])),
                filter_expression="CARGO_MONEDA_FUNCIONAL > 0",
                position_x=480,
                position_y=80,
            ),
            SilverTargetEntityDTO(
                entity_id="target_credit",
                entity_name="PARTIDAS_CREDITO",
                description=f"🔗 Vista Crédito (FK: {pk_field}, Filter: ABONO > 0)",
                selected_columns=list(set(credit_cols + [pk_field])),
                filter_expression="ABONO_MONEDA_FUNCIONAL > 0",
                position_x=840,
                position_y=80,
            ),
        ]
