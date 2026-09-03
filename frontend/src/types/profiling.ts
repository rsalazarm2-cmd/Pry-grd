/**
 * DTOs para el Profiling Estadístico de datasets.
 * Mapeo desde ColumnProfileDTO y DatasetProfileDTO del Backend.
 */

export interface TopFrequencyItem {
  value: string
  count: number
  percentage: number
}

export interface ColumnProfileDTO {
  column_name: string
  domain_category: string
  data_type: string
  null_count: number
  total_rows: number
  null_percentage: number
  unique_count: number
  uniqueness_ratio: number
  min_value: string | null
  max_value: string | null
  mean_value: number | null
  stddev_value: number | null
  sum_value: number | null
  min_length: number | null
  max_length: number | null
  top_frequencies: TopFrequencyItem[]
  sample_values: string[]
  contains_dots: boolean
  contains_commas: boolean
  status_label: string
  status_color: string
}

export interface AnomalyMatrixDTO {
  a1_header_imbalances?: number
  a2_exchange_rate_errors?: number
  a3_timeline_incoherences?: number
  a4_malformed_flexfields?: number
  a5_user_mismatches?: number
  a6_zero_movement_rows?: number
}

export interface DatasetProfileDTO {
  file_path: string
  total_rows: number
  total_columns: number
  file_size_bytes: number
  data_health_score?: number
  constant_columns_count: number
  null_columns_count: number
  perfect_columns_count: number
  columns: ColumnProfileDTO[]
  anomaly_matrix?: AnomalyMatrixDTO
  domain_summary: Record<string, number>
  created_at: string
}
