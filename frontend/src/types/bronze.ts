/**
 * DTOs para la Capa Bronce.
 * Mapeo directo desde models.rs (Rust) a interfaces TypeScript.
 */

export interface ConfigOptionDTO {
  id: string
  label: string
}

export interface SystemConfigOptionsDTO {
  available_data_types: ConfigOptionDTO[]
  null_imputation_strategies: ConfigOptionDTO[]
  duplicate_action_modes: ConfigOptionDTO[]
}

export interface ColumnCleaningRuleDTO {
  include_in_silver: boolean
  new_column_name: string | null
  target_data_type: string | null
  clean_special_chars: boolean | null
  clean_dots: boolean | null
  clean_commas: boolean | null
  null_imputation: string
  convert_to_category: boolean
  group_by_columns: string[]
  category_mapping: Record<string, string>
  has_commas: boolean
  has_dots: boolean
  has_nulls: boolean
  is_constant: boolean
}

export interface BronzeToSilverRulesDTO {
  global_trim_spaces: boolean
  global_clean_special_chars: boolean
  global_clean_accents_and_n: boolean
  global_clean_colons: boolean
  global_clean_dots: boolean
  global_clean_commas: boolean
  null_strategy: string
  column_rules: Record<string, ColumnCleaningRuleDTO>
  flag_missing_headers: boolean
  flag_zero_amounts: boolean
  enable_forensic_trap_detection: boolean
  duplicate_action_mode: string
}

export function createDefaultRules(): BronzeToSilverRulesDTO {
  return {
    global_trim_spaces: true,
    global_clean_special_chars: false,
    global_clean_accents_and_n: false,
    global_clean_colons: false,
    global_clean_dots: false,
    global_clean_commas: false,
    null_strategy: 'IMPUTE',
    column_rules: {},
    flag_missing_headers: true,
    flag_zero_amounts: true,
    enable_forensic_trap_detection: true,
    duplicate_action_mode: 'FLAG_QUARANTINE',
  }
}

export interface IngestionResultDTO {
  status: string
  rows_ingested: number
  file_hash: string
}

export interface BronzeIngestionResultDTO {
  status: string
  rows_ingested: number
}
