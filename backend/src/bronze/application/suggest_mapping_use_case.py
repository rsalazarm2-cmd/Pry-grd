from pathlib import Path
from src.shared.domain.journal_entry import BronzeToSilverRulesDTO, ColumnCleaningRuleDTO
from src.shared.domain.journal_entry_repository import JournalEntryRepository
from src.bronze.application.profile_dataset_use_case import ProfileDatasetUseCase
from src.bronze.infrastructure.bronze_profiler import get_nlp_classifier
from src.ai_translator.domain.models import TargetSchemaDefinitionDTO
from src.bronze.infrastructure.mapping_rules_persistence_service import MappingRulesPersistenceService

class SuggestMappingUseCase:
    """
    Caso de Uso para analizar el perfil del dataset en la Capa Bronce,
    ejecutar el clasificador NLP y generar reglas sugeridas de tipado y limpieza.
    """

    def __init__(self, repository: JournalEntryRepository):
        self.repository = repository
        self.profile_use_case = ProfileDatasetUseCase(repository)

    def execute(self, bronze_parquet_path: str, target_lang: str = "es", force: bool = False) -> BronzeToSilverRulesDTO:
        parquet_path = Path(bronze_parquet_path).resolve()
        rules_file = MappingRulesPersistenceService.get_rules_path(parquet_path)
        
        # 1. Si no es forzado y ya existen reglas guardadas en disco, las recupera
        if not force and rules_file.exists():
            try:
                return MappingRulesPersistenceService.load_saved_rules(parquet_path)
            except Exception:
                pass

        # 2. Análisis Dinámico del Perfil Físico y NLP Multilingüe
        profile = self.profile_use_case.execute(bronze_parquet_path)
        translator = get_nlp_classifier()
        source_cols = [c.column_name for c in profile.columns]
        
        from src.ai_translator.domain.domain_classifier import OFFICIAL_SPANISH_SCHEMA, OFFICIAL_ENGLISH_SCHEMA
        target_schema_dict = OFFICIAL_ENGLISH_SCHEMA if target_lang.lower() == "en" else OFFICIAL_SPANISH_SCHEMA
        
        mapping_res = translator.translate_columns(
            source_cols,
            TargetSchemaDefinitionDTO(schema_map=target_schema_dict),
            threshold=0.30,
            target_lang=target_lang
        )
        suggested_map = mapping_res.suggested_mapping


        suggested_rules = BronzeToSilverRulesDTO()

        for col_profile in profile.columns:
            col_name = col_profile.column_name
            rule = ColumnCleaningRuleDTO()
            
            # Nombre destino traducido por NLP o fallback dinámico a español en mayúsculas
            if col_name in suggested_map:
                rule.new_column_name = suggested_map[col_name]
            elif target_lang.lower() == "es":
                from src.ai_translator.domain.domain_classifier import translate_raw_column_name_to_spanish
                rule.new_column_name = translate_raw_column_name_to_spanish(col_name)
            else:
                rule.new_column_name = col_name.strip().upper()


            rule.target_data_type = col_profile.data_type
            rule.has_commas = col_profile.contains_commas
            rule.has_dots = col_profile.contains_dots
            rule.clean_commas = col_profile.contains_commas
            rule.clean_dots = col_profile.contains_dots if col_profile.data_type not in ("DOUBLE", "FLOAT", "DECIMAL") else False

                
            if col_profile.unique_count <= 1 or col_profile.null_percentage >= 99.9:
                rule.include_in_silver = False
                rule.is_constant = True
            else:
                rule.include_in_silver = True
                rule.is_constant = False
                
            if 1 < col_profile.unique_count <= 50:
                rule.convert_to_category = True
                
            if col_profile.null_count > 0:
                rule.has_nulls = True


            # Detección dinámica de tipos de datos
            dt = col_profile.data_type.strip().upper() if col_profile.data_type else ""
            if "DATE" in dt or "TIME" in dt:
                rule.target_data_type = "TIMESTAMP" if "TIME" in dt else "DATE"
            elif dt in ("DOUBLE", "BIGINT", "INTEGER", "FLOAT", "DECIMAL", "NUMERIC"):
                rule.null_imputation = "ZERO"
                rule.clean_dots = False
                if col_profile.contains_commas:
                    rule.clean_commas = True
            elif dt in ("VARCHAR", "TEXT", "STRING"):
                max_len = getattr(col_profile, "max_length", None)
                if max_len is not None and max_len <= 3:
                    rule.target_data_type = "CHAR(3)"
                else:
                    rule.target_data_type = "VARCHAR"
                rule.null_imputation = "UNKNOWN"


            suggested_rules.column_rules[col_name] = rule

        # Persiste la receta dinámica en disco
        MappingRulesPersistenceService.save_rules(parquet_path, suggested_rules)
        return suggested_rules
