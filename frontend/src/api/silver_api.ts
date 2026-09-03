/**
 * Endpoints de la Capa Plata (Silver).
 * Transformación, records, sugerencias de atomicidad,
 * y motores de Fase 1 (Fecha + Amount Split).
 */

import { apiGet, apiPost } from './http_client'
import type { TabularResultDTO } from '@/types/gold'
import type { DatasetProfileDTO } from '@/types/profiling'
import type { BronzeToSilverRulesDTO } from '@/types/bronze'
import type {
  SilverTransformationResultDTO,
  DatePairDTO,
  DateRedundancyResultDTO,
  DateDeltaResultDTO,
  WeekdayResultDTO,
  AmountSplitResultDTO,
  LineageMatrixDTO,
  ConditionalRuleDTO,
  RuleEvaluationResultDTO,
} from '@/types/silver'


/** Ejecuta el pipeline de transformación Bronce → Plata. */
export function transformSilver(
  rules: BronzeToSilverRulesDTO,
): Promise<SilverTransformationResultDTO> {
  return apiPost<SilverTransformationResultDTO>('/silver/transform', rules)
}

/** Obtiene registros limpios de la capa Plata (CU-05: viewMode ALL, CARGOS, ABONOS). */
export function fetchSilverRecords(viewMode: string = 'ALL'): Promise<TabularResultDTO> {
  return apiGet<TabularResultDTO>(`/silver/records?view_mode=${encodeURIComponent(viewMode)}`)
}

/** Obtiene el perfil estadístico del dataset Plata. */
export function fetchSilverProfile(): Promise<DatasetProfileDTO> {
  return apiGet<DatasetProfileDTO>('/silver/profile')
}

// ─── Fase 2: Receta y Linaje (CU-07, CU-08) ───

/** CU-08: Carga en ~1 ms la receta contable guardada. */
export function fetchSavedRules(): Promise<BronzeToSilverRulesDTO | null> {
  return apiGet<BronzeToSilverRulesDTO | null>('/silver/saved-rules')
}

/** CU-07: Obtiene la matriz de linaje transparente Origen ➔ Plata. */
export function fetchLineageMatrix(): Promise<LineageMatrixDTO> {
  return apiGet<LineageMatrixDTO>('/silver/lineage')
}

// ─── Fase 3: Reglas Condicionales (CU-09, CU-10) ───

/** CU-09/CU-10: Compila y evalúa una regla condicional No-Code. */
export function evaluateConditionalRule(
  rule: ConditionalRuleDTO,
): Promise<RuleEvaluationResultDTO> {
  return apiPost<RuleEvaluationResultDTO>('/silver/evaluate-rule', rule)
}



// ─── Fase 1: Motor de Expresiones de Fecha (CU-01, CU-02, CU-03) ───

/** Lista columnas DATE/TIMESTAMP del Parquet activo. */
export function fetchDateColumns(): Promise<string[]> {
  return apiGet<string[]>('/silver/date-columns')
}

/** CU-01: Calcula % de coincidencia entre 2 columnas de fecha. */
export function computeDateRedundancy(
  pair: DatePairDTO,
): Promise<DateRedundancyResultDTO> {
  return apiPost<DateRedundancyResultDTO>('/silver/date-redundancy', pair)
}

/** CU-02: Genera estadísticas de DIFERENCIA_SEGUNDOS. */
export function computeDateDelta(pair: DatePairDTO): Promise<DateDeltaResultDTO> {
  return apiPost<DateDeltaResultDTO>('/silver/date-delta', pair)
}

/** CU-03: Distribución de día de semana + fin de semana. */
export function computeWeekdayDistribution(
  dateColumn: string,
): Promise<WeekdayResultDTO> {
  return apiGet<WeekdayResultDTO>(
    `/silver/weekday-distribution?date_column=${encodeURIComponent(dateColumn)}`,
  )
}

// ─── Fase 1: Motor de Separación de Montos (CU-04) ───

/** Lista columnas numéricas del Parquet activo. */
export function fetchNumericColumns(): Promise<string[]> {
  return apiGet<string[]>('/silver/numeric-columns')
}

/** CU-04: Preview de separación de columna signada a CARGO/ABONO. */
export function previewAmountSplit(
  sourceColumn: string,
): Promise<AmountSplitResultDTO> {
  return apiPost<AmountSplitResultDTO>(
    `/silver/amount-split-preview?source_column=${encodeURIComponent(sourceColumn)}`,
    {},
  )
}

// ─── Motor Vectorial Forense (Fase 1) ───

export function fetchForensicSummary(projectId?: string): Promise<import('@/types/silver').ForensicAuditSummaryDTO> {
  const q = projectId ? `?project_id=${encodeURIComponent(projectId)}` : ''
  return apiGet<import('@/types/silver').ForensicAuditSummaryDTO>(`/silver/forensic-summary${q}`)
}

export function fetchForensicHighRisk(projectId?: string, limit: number = 50): Promise<import('@/types/silver').ForensicVectorRecordDTO[]> {
  const params = new URLSearchParams({ limit: String(limit) })
  if (projectId) params.append('project_id', projectId)
  return apiGet<import('@/types/silver').ForensicVectorRecordDTO[]>(`/silver/forensic-high-risk?${params.toString()}`)
}

