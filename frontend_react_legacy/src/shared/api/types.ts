export interface TopFrequencyItem {
  value: string;
  count: number;
  percentage: number;
}

export interface ColumnProfile {
  column_name: string;
  domain_category: string;
  data_type: string;
  null_count: number;
  total_rows: number;
  null_percentage: number;
  unique_count: number;
  uniqueness_ratio: number;
  min_value?: string;
  max_value?: string;
  mean_value?: number;
  stddev_value?: number;
  sum_value?: number;
  min_length?: number;
  max_length?: number;
  top_frequencies: TopFrequencyItem[];
  sample_values: string[];
}

export interface AnomalyMatrix {
  a1_header_imbalances: number;
  a2_exchange_rate_errors: number;
  a3_timeline_incoherences: number;
  a4_malformed_flexfields: number;
  a5_user_mismatches: number;
  a6_zero_movement_rows: number;
}

export interface DatasetProfile {
  file_path: string;
  total_rows: number;
  total_columns: number;
  file_size_bytes: number;
  columns: ColumnProfile[];
  anomaly_matrix: AnomalyMatrix;
  domain_summary: Record<string, number>;
  created_at: string;
}

export interface ColumnCleaningRule {
  include_in_silver: boolean;
  new_column_name?: string;
  target_data_type?: string;
  clean_special_chars?: boolean | null;
  clean_dots?: boolean | null;
  clean_commas?: boolean | null;
  to_uppercase?: boolean | null;
  null_imputation: string;
  convert_to_category: boolean;
  group_by_columns?: string[];
  category_mapping?: Record<string, string>;
}

export interface TransformationRules {
  columns?: Record<string, ColumnCleaningRule>;
  column_rules?: Record<string, ColumnCleaningRule>;
  global_trim?: boolean;
  global_trim_spaces?: boolean;
  global_uppercase?: boolean;
  global_clean_special_chars?: boolean;
  global_clean_accents_and_symbols?: boolean;
  global_clean_accents_and_n?: boolean;
  global_clean_colons?: boolean;
  global_clean_dots?: boolean;
  global_clean_commas?: boolean;
  split_rules?: any[];
  combine_rules?: ColumnCombineRule[];
  calculated_field_rules?: CalculatedFieldRule[];
  semantic_mapping?: SemanticMapping;
  gold_dimensions?: string[];
}

export interface Project {
  id: string;
  name: string;
  description?: string;
  domain: string;
  created_at: string;
  storage_path: string;
  has_recipe: boolean;
}

export interface CreateProjectPayload {
  name: string;
  description?: string;
  domain?: string;
}

export interface BronzeResult {
  bronze_path: string;
  row_count: number;
  column_count: number;
  file_size_bytes: number;
  file_hash: string;
  is_duplicate: boolean;
  audit_message: string;
  execution_time_seconds: number;
}

export interface SilverResult {
  silver_path: string;
  original_row_count: number;
  silver_row_count: number;
  columns_transformed: number;
  quality_summary: Record<string, number>;
  execution_time_seconds: number;
}

export interface GoldResult {
  ledger_model_path: string;
  account_model_path: string;
  ledger_rows: number;
  account_rows: number;
  execution_time_seconds: number;
}

export interface TabularResult {
  total_count: number;
  returned_count: number;
  columns: string[];
  rows: Record<string, any>[];
}

export interface GoldBalanceItem {
  LEDGER_NAME: string;
  CURRENCY: string;
  TOTAL_JOURNAL_LINES: number;
  TOTAL_ENTERED_DR: number;
  TOTAL_ENTERED_CR: number;
  NET_ACCOUNTED_BALANCE: number;
}

export interface ColumnCombineRule {
  enabled: boolean;
  columns: string[];
  operation: 'SUM' | 'SUBTRACT' | 'MULTIPLY' | 'DIVIDE' | 'CONCAT';
  result_column: string;
  separator: string;
  drop_originals: boolean;
}

export interface CalculatedFieldRule {
  enabled: boolean;
  function_name: 'DAYS_BETWEEN' | 'DAY_OF_WEEK' | 'MONTH_NAME' | 'YEAR_EXTRACT' | 'CONCAT_FIELDS';
  source_columns: string[];
  result_column: string;
  result_type: string;
}

export interface SemanticMapping {
  entered_dr_col?: string;
  entered_cr_col?: string;
  accounted_dr_col?: string;
  accounted_cr_col?: string;
  account_col?: string;
  ledger_col?: string;
  date_col?: string;
  category_col?: string;
}

export interface SilverToGoldRules {
  semantic_mapping?: SemanticMapping;
  split_rules: any[];
  combine_rules: ColumnCombineRule[];
  calculated_field_rules: CalculatedFieldRule[];
  gold_dimensions?: string[];
}
