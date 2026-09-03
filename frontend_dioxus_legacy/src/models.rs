use serde::{Deserialize, Serialize};

#[derive(Debug, Clone, Serialize, Deserialize, PartialEq)]
pub struct ConfigOptionDTO {
    pub id: String,
    pub label: String,
}

#[derive(Debug, Clone, Serialize, Deserialize, PartialEq, Default)]
pub struct SystemConfigOptionsDTO {
    #[serde(default)]
    pub available_data_types: Vec<ConfigOptionDTO>,
    #[serde(default)]
    pub null_imputation_strategies: Vec<ConfigOptionDTO>,
    #[serde(default)]
    pub duplicate_action_modes: Vec<ConfigOptionDTO>,
}

/// Estructura de auditoría contable mapeada desde la capa Plata.
/// Cumple con la regla de campos financieros y SRP.
#[derive(Debug, Clone, Serialize, Deserialize, PartialEq)]
pub struct AsientoContable {
    pub folio_asiento: String,
    pub usuario_registrador: String,
    pub total_cargos_cabecera: f64,
    pub suma_cargos_detalle: f64,
    pub diferencia: f64,
    pub fecha_contabilizacion: String,
}

use std::collections::HashMap;

#[derive(Debug, Clone, Serialize, Deserialize, PartialEq)]
pub struct ColumnCleaningRuleDTO {
    pub include_in_silver: bool,
    pub new_column_name: Option<String>,
    pub target_data_type: Option<String>,
    pub clean_special_chars: Option<bool>,
    pub clean_dots: Option<bool>,
    pub clean_commas: Option<bool>,
    pub null_imputation: String,
    pub convert_to_category: bool,
    pub group_by_columns: Vec<String>,
    pub category_mapping: std::collections::HashMap<String, String>,
    #[serde(default)]
    pub has_commas: bool,
    #[serde(default)]
    pub has_dots: bool,
    #[serde(default)]
    pub has_nulls: bool,
    #[serde(default)]
    pub is_constant: bool,
}

impl Default for ColumnCleaningRuleDTO {
    fn default() -> Self {
        Self {
            include_in_silver: true,
            new_column_name: None,
            target_data_type: None,
            clean_special_chars: None,
            clean_dots: None,
            clean_commas: None,
            null_imputation: "DEFAULT".to_string(),
            convert_to_category: false,
            group_by_columns: Vec::new(),
            category_mapping: std::collections::HashMap::new(),
            has_commas: false,
            has_dots: false,
            has_nulls: false,
            is_constant: false,
        }
    }
}

#[derive(Debug, Clone, Serialize, Deserialize, PartialEq)]
pub struct BronzeToSilverRulesDTO {
    pub global_trim_spaces: bool,
    pub global_clean_special_chars: bool,
    pub global_clean_accents_and_n: bool,
    pub global_clean_colons: bool,
    pub global_clean_dots: bool,
    pub global_clean_commas: bool,
    pub null_strategy: String,
    pub column_rules: HashMap<String, ColumnCleaningRuleDTO>,
    pub flag_missing_headers: bool,
    pub flag_zero_amounts: bool,
    pub enable_forensic_trap_detection: bool,
    pub duplicate_action_mode: String,
}

impl Default for BronzeToSilverRulesDTO {
    fn default() -> Self {
        Self {
            global_trim_spaces: true,
            global_clean_special_chars: false,
            global_clean_accents_and_n: false,
            global_clean_colons: false,
            global_clean_dots: false,
            global_clean_commas: false,
            null_strategy: "IMPUTE".to_string(),
            column_rules: HashMap::new(),
            flag_missing_headers: true,
            flag_zero_amounts: true,
            enable_forensic_trap_detection: true,
            duplicate_action_mode: "FLAG_QUARANTINE".to_string(),
        }
    }
}

#[derive(Debug, Clone, Serialize, Deserialize, PartialEq, Default)]
pub struct SilverTransformationResultDTO {
    pub status: String,
    pub silver_row_count: usize,
    pub rows_cleaned: usize,
    pub nulls_removed: usize,
    pub rows_deduplicated: usize,
    pub traps_detected: usize,
}

#[derive(Debug, Clone, Serialize, Deserialize, PartialEq)]
pub struct TopFrequencyItem {
    pub value: String,
    pub count: usize,
    pub percentage: f64,
}

#[derive(Debug, Clone, Serialize, Deserialize, PartialEq)]
pub struct ColumnProfileDTO {
    pub column_name: String,
    pub domain_category: String,
    pub data_type: String,
    pub null_count: usize,
    pub total_rows: usize,
    pub null_percentage: f64,
    pub unique_count: usize,
    pub uniqueness_ratio: f64,
    pub min_value: Option<String>,
    pub max_value: Option<String>,
    pub mean_value: Option<f64>,
    pub stddev_value: Option<f64>,
    pub sum_value: Option<f64>,
    pub min_length: Option<usize>,
    pub max_length: Option<usize>,
    #[serde(default)]
    pub top_frequencies: Vec<TopFrequencyItem>,
    #[serde(default)]
    pub sample_values: Vec<String>,
    pub contains_dots: bool,
    pub contains_commas: bool,
    #[serde(default)]
    pub status_label: String,
    #[serde(default)]
    pub status_color: String,
}

#[derive(Debug, Clone, Serialize, Deserialize, PartialEq)]
pub struct AnomalyMatrixDTO {
    pub a1_header_imbalances: usize,
    pub a2_exchange_rate_errors: usize,
    pub a3_timeline_incoherences: usize,
    pub a4_malformed_flexfields: usize,
    pub a5_user_mismatches: usize,
    pub a6_zero_movement_rows: usize,
}

#[derive(Clone, PartialEq, Default, Debug, Serialize, Deserialize)]
pub struct DistinctValueDTO {
    pub value: String,
    pub count: usize,
}

#[derive(Debug, Clone, Serialize, Deserialize, PartialEq)]
pub struct DatasetProfileDTO {
    pub file_path: String,
    pub total_rows: usize,
    pub total_columns: usize,
    pub file_size_bytes: usize,
    #[serde(default)]
    pub constant_columns_count: usize,
    #[serde(default)]
    pub null_columns_count: usize,
    #[serde(default)]
    pub perfect_columns_count: usize,
    #[serde(default)]
    pub columns: Vec<ColumnProfileDTO>,
    pub anomaly_matrix: AnomalyMatrixDTO,
    #[serde(default)]
    pub domain_summary: std::collections::HashMap<String, usize>,
    pub created_at: String,
}

#[derive(Debug, Clone, Serialize, Deserialize, PartialEq)]
pub struct TabularResultDTO {
    pub columns: Vec<String>,
    pub rows: Vec<std::collections::HashMap<String, serde_json::Value>>,
    pub total_returned: usize,
}
