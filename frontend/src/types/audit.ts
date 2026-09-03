/**
 * DTOs e Interfaces TypeScript para la Auditoría Forense (Fase 5).
 * Cubre CU-16 a CU-20: SoD, Trampas Forenses, Cut-off y Integrity Risk Score.
 */

export interface SodViolationDTO {
  folio_asiento: string
  usuario_registrador: string
  usuario_aprobador: string
  fecha_registro: string
  monto_total: number
  tipo_violacion: string
  diferencia_segundos?: number
  nivel_riesgo: string
}

export interface ForensicTrapAlertDTO {
  folio_asiento: string
  tipo_trampa: string
  descripcion_trampa: string
  fecha_registro: string
  monto: number
  nivel_riesgo: string
}

export interface CutoffAnomalyDTO {
  folio_asiento: string
  periodo_contable: string
  fecha_contabilizacion: string
  fecha_registro: string
  diferencia_dias: number
  descripcion: string
  nivel_riesgo: string
}

export interface IntegrityRiskScoreDTO {
  total_asientos_analizados: number
  financial_integrity_score: number
  nivel_riesgo_global: string
  sod_violations_count: number
  forensic_traps_count: number
  cutoff_anomalies_count: number
  imbalanced_entries_count: number
}

export interface ForensicAuditMatrixDTO {
  score: IntegrityRiskScoreDTO
  sod_violations: SodViolationDTO[]
  forensic_traps: ForensicTrapAlertDTO[]
  cutoff_anomalies: CutoffAnomalyDTO[]
}
