/**
 * DTOs para la Capa Plata (Silver).
 * Resultados de transformación y datos tabulares.
 */

export interface SilverTransformationResultDTO {
  status: string
  silver_row_count: number
  rows_cleaned: number
  nulls_removed: number
  rows_deduplicated: number
  traps_detected: number
}

export interface AtomicitySuggestionDTO {
  column_name: string
  suggestion: string
  confidence: number
}

// ─── Fase 1: Expresiones de Fecha (CU-01, CU-02, CU-03) ───

/** Par de columnas de fecha seleccionadas por el auditor. */
export interface DatePairDTO {
  date_column_a: string
  date_column_b: string
}

/** CU-01: % de coincidencia entre 2 columnas de fecha. */
export interface DateRedundancyResultDTO {
  date_column_a: string
  date_column_b: string
  total_rows: number
  matching_rows: number
  match_percentage: number
  are_identical: boolean
}

/** Bucket de histograma para distribución de deltas temporales. */
export interface HistogramBucketDTO {
  label: string
  count: number
}

/** CU-02: Estadísticas de DIFERENCIA_SEGUNDOS entre 2 fechas. */
export interface DateDeltaResultDTO {
  source_column_a: string
  source_column_b: string
  result_column_name: string
  total_rows: number
  min_delta_seconds: number
  max_delta_seconds: number
  avg_delta_seconds: number
  rapid_approvals_count: number
  histogram_buckets: HistogramBucketDTO[]
}

/** Bucket de distribución por día de la semana. */
export interface WeekdayBucketDTO {
  day: string
  count: number
}

/** CU-03: Distribución de día de semana + flag fin de semana. */
export interface WeekdayResultDTO {
  source_column: string
  total_rows: number
  weekend_count: number
  weekend_percentage: number
  weekday_distribution: WeekdayBucketDTO[]
}

// ─── Fase 1: Separador de Montos (CU-04) ───

/** CU-04: Resultado de separación de columna signada a CARGO/ABONO. */
export interface AmountSplitResultDTO {
  source_column: string
  cargo_column: string
  abono_column: string
  total_rows: number
  rows_with_cargo: number
  rows_with_abono: number
  total_cargo: number
  total_abono: number
// ─── Fase 2: Linaje y Trazabilidad (CU-07) ───

export interface LineageItemDTO {
  source_column: string
  target_column: string
  inferred_type: string
  target_type: string
  null_imputation: string
  is_included: boolean
  quality_status: string
}

export interface LineageMatrixDTO {
  project_id: string
  source_columns_count: number
  target_columns_count: number
  recipe_applied: boolean
  items: LineageItemDTO[]
}

// ─── Fase 3: Reglas Condicionales No-Code & Preview (CU-09, CU-10) ───

export interface RuleConditionDTO {
  column_name: string
  operator: string // "GT" | "LT" | "EQ" | "NEQ" | "IN" | "IS_NULL"
  value: unknown
}

export interface ConditionalRuleDTO {
  rule_name: string
  conditions: RuleConditionDTO[]
  logical_operator: string // "AND" | "OR"
  then_result_column: string
  then_value: string
  else_value?: string
}


export interface RuleEvaluationResultDTO {
  rule_name: string
  result_column: string
  total_rows: number
  matches_count: number
  matches_percentage: number
  sql_expression: string
  sample_rows: Array<Record<string, unknown>>
}

// ─── Motor Vectorial Forense de 5 Dimensiones ───

export interface ForensicVectorTemporalDTO {
  flag_fin_semana: boolean
  flag_horario_nocturno: boolean
  dias_diferencia_creacion_gl: number
}

export interface ForensicVectorSODDTO {
  flag_mismo_usuario: boolean
  delta_segundos_aprobacion?: number
  flag_aprobacion_flash: boolean
}

export interface ForensicVectorSemanticoDTO {
  score_entropia_glosa: number
  flag_glosa_sospechosa: boolean
  longitud_glosa: number
}

export interface ForensicVectorMatematicoDTO {
  flag_monto_redondo: boolean
  primer_digito: number
  flag_desviacion_benford: boolean
}

export interface ForensicVectorAcumuladoDTO {
  monto_acumulado_dia_usuario: number
  conteo_asientos_dia_usuario: number
  flag_posible_fraccionamiento: boolean
}

export interface ForensicVectorRecordDTO {
  folio_asiento: string
  vector_temporal: ForensicVectorTemporalDTO
  vector_sod: ForensicVectorSODDTO
  vector_semantico: ForensicVectorSemanticoDTO
  vector_matematico: ForensicVectorMatematicoDTO
  vector_acumulado: ForensicVectorAcumuladoDTO
  score_riesgo_preliminar: number
}

export interface ForensicAuditSummaryDTO {
  total_registros_evaluados: number
  total_alertas_temporales: number
  total_alertas_sod: number
  total_alertas_semanticas: number
  total_alertas_fraccionamiento: number
  total_asientos_alto_riesgo: number
}



