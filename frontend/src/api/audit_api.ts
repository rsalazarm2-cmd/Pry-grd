/**
 * Cliente HTTP API para Auditoría Forense (Fase 5).
 */

import { apiGet } from './http_client'
import type {
  ForensicAuditMatrixDTO,
  ForensicTrapAlertDTO,
  CutoffAnomalyDTO,
  SodViolationDTO,
} from '@/types/audit'

/** Obtiene la matriz completa de auditoría forense y Financial Integrity Score (CU-19). */
export function fetchForensicMatrix(): Promise<ForensicAuditMatrixDTO> {
  return apiGet<ForensicAuditMatrixDTO>('/audit/forensic-matrix')
}

/** Obtiene violaciones de segregación de funciones SoD (CU-16). */
export function fetchSodViolations(): Promise<SodViolationDTO[]> {
  return apiGet<SodViolationDTO[]>('/audit/sod-violations')
}

/** Obtiene alertas de trampas forenses (CU-17). */
export function fetchForensicTraps(): Promise<ForensicTrapAlertDTO[]> {
  return apiGet<ForensicTrapAlertDTO[]>('/audit/traps')
}

/** Obtiene descalces de corte temporal Cut-off (CU-18). */
export function fetchCutoffAnomalies(): Promise<CutoffAnomalyDTO[]> {
  return apiGet<CutoffAnomalyDTO[]>('/audit/cutoff-anomalies')
}
