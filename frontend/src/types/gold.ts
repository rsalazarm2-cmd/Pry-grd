/**
 * DTOs genéricos de resultados tabulares y Capa Oro (Gold).
 * Usados por las vistas de Datamarts financieros.
 */

export interface TabularResultDTO {
  columns: string[]
  rows: Record<string, unknown>[]
  total_returned: number
}

// ─── Fase 4: Datamarts Oro e Integridad (CU-11 a CU-15) ───

export interface GoldIntegritySummaryDTO {
  total_debit: number
  total_credit: number
  global_imbalance: number
  is_globally_balanced: boolean
  imbalanced_entries_count: number
  imbalanced_entries_amount: number
  total_journals_count: number
}

export interface GoldDatamartResultDTO {
  status: string
  ledger_model_path: string
  account_model_path: string
  ledger_rows_count: number
  account_rows_count: number
  integrity: GoldIntegritySummaryDTO
  execution_time_seconds: number
}

// ─── Scoring Consolidado de Riesgo en Capa Oro (0-100) ───

export interface JournalRiskScoreDTO {
  folio_asiento: string
  score_global: number
  nivel_riesgo: string
  usuario_registrador: string
  monto_total: number
  factores_riesgo: string[]
}

export interface UserRiskDatamartItemDTO {
  usuario: string
  total_asientos: number
  asientos_alto_riesgo: number
  monto_total_registrado: number
  score_promedio_usuario: number
  casos_sod_count: number
  casos_fraccionamiento_count: number
}

export interface GoldExecutiveRiskDatamartDTO {
  total_asientos_analizados: number
  score_promedio_general: number
  total_asientos_criticos: number
  total_monto_en_riesgo: number
  top_asientos_criticos: JournalRiskScoreDTO[]
  top_usuarios_riesgosos: UserRiskDatamartItemDTO[]
}

