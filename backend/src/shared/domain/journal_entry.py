from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class ConfigOptionDTO(BaseModel):
    id: str
    label: str

class SystemConfigOptionsDTO(BaseModel):
    available_data_types: List[ConfigOptionDTO] = Field(default_factory=list)
    null_imputation_strategies: List[ConfigOptionDTO] = Field(default_factory=list)
    duplicate_action_modes: List[ConfigOptionDTO] = Field(default_factory=list)

class ColumnCleaningRuleDTO(BaseModel):
    include_in_silver: bool = Field(default=True)
    new_column_name: Optional[str] = Field(default=None)
    target_data_type: Optional[str] = Field(default=None)
    clean_special_chars: Optional[bool] = Field(default=None)
    clean_dots: Optional[bool] = Field(default=None)
    clean_commas: Optional[bool] = Field(default=None)
    null_imputation: str = Field(default="DEFAULT")
    convert_to_category: bool = Field(default=False)
    convert_uppercase: bool = Field(default=True)
    group_by_columns: List[str] = Field(default_factory=list)
    category_mapping: Dict[str, str] = Field(default_factory=dict)
    has_commas: bool = Field(default=False)
    has_dots: bool = Field(default=False)
    has_nulls: bool = Field(default=False)
    is_constant: bool = Field(default=False)

class ColumnCombineRuleDTO(BaseModel):
    """Regla para combinar/fusionar dos o más columnas."""
    enabled: bool = Field(default=True)
    columns: List[str] = Field(default_factory=list)
    operation: str = Field(default="SUBTRACT")
    result_column: str = Field(default="RESULTADO")
    separator: str = Field(default=" ")
    drop_originals: bool = Field(default=False)

class CalculatedFieldRuleDTO(BaseModel):
    """Regla para crear un campo calculado derivado."""
    enabled: bool = Field(default=True)
    function_name: str = Field(default="DAYS_BETWEEN")
    source_columns: List[str] = Field(default_factory=list)
    result_column: str = Field(default="CAMPO_CALCULADO")
    result_type: str = Field(default="INTEGER")

class SilverTargetEntityDTO(BaseModel):
    """Entidad/Tabla de destino en la Capa Plata para modelado multitabla."""
    entity_id: str
    entity_name: str
    description: Optional[str] = Field(default="")
    selected_columns: List[str] = Field(default_factory=list)
    filter_expression: Optional[str] = Field(default=None)
    position_x: int = Field(default=400)
    position_y: int = Field(default=100)

class BronzeToSilverRulesDTO(BaseModel):
    """Reglas exclusivas para limpiar y tipar datos (Capa Bronce -> Plata)."""
    global_trim_spaces: bool = Field(default=True)
    global_convert_uppercase: bool = Field(default=True)
    global_clean_special_chars: bool = Field(default=False)

    global_clean_accents_and_n: bool = Field(default=False)
    global_clean_colons: bool = Field(default=False)
    global_clean_dots: bool = Field(default=False)
    global_clean_commas: bool = Field(default=False)
    null_strategy: str = Field(default="IMPUTE")
    column_rules: Dict[str, ColumnCleaningRuleDTO] = Field(default_factory=dict)
    target_entities: List[SilverTargetEntityDTO] = Field(default_factory=list)
    flag_missing_headers: bool = Field(default=True)
    flag_zero_amounts: bool = Field(default=True)
    enable_forensic_trap_detection: bool = Field(default=True)
    duplicate_action_mode: str = Field(default="FLAG_QUARANTINE", description="Opciones: FLAG_QUARANTINE, PREFIX_DUP, PURGE_DELETE")
    duplicate_prefix: str = Field(default="DUP_")
    duplicate_keys: List[str] = Field(default_factory=list)

    @property
    def global_trim(self) -> bool:
        return self.global_trim_spaces

    @property
    def global_clean_accents_and_symbols(self) -> bool:
        return self.global_clean_special_chars

    @property
    def columns(self) -> Dict[str, ColumnCleaningRuleDTO]:
        return self.column_rules

class SemanticMappingDTO(BaseModel):
    """Mapeo dinámico de nombres de columnas del usuario a roles semánticos del negocio."""
    entered_dr_col: Optional[str] = Field(default=None)
    entered_cr_col: Optional[str] = Field(default=None)
    accounted_dr_col: Optional[str] = Field(default=None)
    accounted_cr_col: Optional[str] = Field(default=None)
    account_col: Optional[str] = Field(default=None)
    ledger_col: Optional[str] = Field(default=None)
    date_col: Optional[str] = Field(default=None)
    category_col: Optional[str] = Field(default=None)

class SilverToGoldRulesDTO(BaseModel):
    """Reglas exclusivas para enriquecimiento y agregación (Capa Plata -> Oro)."""
    semantic_mapping: Optional[SemanticMappingDTO] = Field(default_factory=SemanticMappingDTO)
    split_rules: List[Any] = Field(default_factory=list)
    combine_rules: List[Any] = Field(default_factory=list)
    calculated_field_rules: List[Any] = Field(default_factory=list)
    gold_dimensions: Optional[List[str]] = Field(default=None)

class TransformationRulesDTO(BronzeToSilverRulesDTO, SilverToGoldRulesDTO):
    pass

class GoldCustomFilterDTO(BaseModel):
    selected_ledgers: List[str] = Field(default_factory=list)
    selected_categories: List[str] = Field(default_factory=list)
    selected_columns: List[str] = Field(
        default_factory=lambda: [
            "JE_HEADER_ID", "LEDGER_NAME", "JE_CATEGORY", "CODE_COMBINATION",
            "ENTERED_DR", "ENTERED_CR", "ACCOUNTED_DR", "ACCOUNTED_CR", "QUALITY_STATUS"
        ]
    )
    only_imbalanced: bool = Field(default=False)

from src.shared.domain.dataset_profile import (
    TopFrequencyItem, ColumnProfileDTO, DatasetProfileDTO
)

class BronzeIngestionResultDTO(BaseModel):
    status: str
    source_csv_path: str
    target_parquet_path: str
    rows_ingested: int
    columns_count: int
    file_size_bytes: int
    execution_time_seconds: float
    is_incremental: bool = False
    previous_rows: int = 0
    file_hash: Optional[str] = None
    message: Optional[str] = None

class TabularResultDTO(BaseModel):
    columns: List[str] = Field(default_factory=list)
    rows: List[Dict[str, Any]] = Field(default_factory=list)
    total_returned: int = Field(default=0)

class SilverTransformationResultDTO(BaseModel):
    status: str = Field(default="success")
    source_bronze_path: Optional[str] = Field(default=None)
    target_silver_path: Optional[str] = Field(default=None)
    silver_path: str = Field(default="")
    original_row_count: int = Field(default=0)
    silver_row_count: int = Field(default=0)
    rows_processed: int = Field(default=0)
    rows_cleaned: int = Field(default=0)
    nulls_removed: int = Field(default=0)
    rows_deduplicated: int = Field(default=0)
    traps_detected: int = Field(default=0)
    quarantine_path: Optional[str] = Field(default=None)
    columns_transformed: int = Field(default=0)
    strategy_applied: str = Field(default="Recipe-based Transformation")
    quality_summary: Dict[str, int] = Field(default_factory=dict)
    execution_time_seconds: float = Field(default=0.0)

class GoldModelsResultDTO(BaseModel):
    status: str = Field(default="success")
    source_silver_path: Optional[str] = Field(default=None)
    target_gold_dir: Optional[str] = Field(default=None)
    ledger_model_path: str = Field(default="")
    account_model_path: str = Field(default="")
    ledger_rows: int = Field(default=0)
    account_rows: int = Field(default=0)
    summary_tables_generated: List[str] = Field(default_factory=list)
    total_debit: float = Field(default=0.0)
    total_credit: float = Field(default=0.0)
    is_balanced: bool = Field(default=True)
    imbalance_amount: float = Field(default=0.0)
    execution_time_seconds: float = Field(default=0.0)

class JournalEntryDTO(BaseModel):
    je_header_id: Optional[str] = None
    je_category: Optional[str] = None
    je_source: Optional[str] = None
    posted_by_gl: Optional[str] = None
    code_combination: Optional[str] = None
    ledger_name: Optional[str] = None
    currency: Optional[str] = None
    entered_dr: Optional[float] = 0.0
    entered_cr: Optional[float] = 0.0
    accounted_dr: Optional[float] = 0.0
    accounted_cr: Optional[float] = 0.0
    accounting_period: Optional[str] = None
    je_effective_date: Optional[str] = None
