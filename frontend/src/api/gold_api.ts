/**
 * Endpoints de la Capa Oro (Gold).
 * Datamarts financieros: balances por libro contable y por cuenta.
 */

import { apiGet, apiPost } from './http_client'
import type { TabularResultDTO, GoldIntegritySummaryDTO, GoldDatamartResultDTO } from '@/types/gold'

/** Obtiene el balance general por libro contable (CU-11). */
export function fetchGoldBalances(): Promise<TabularResultDTO> {
  return apiGet<TabularResultDTO>('/gold/balances')
}

/** Obtiene el balance detallado por cuenta contable PyG (CU-12). */
export function fetchGoldAccountBalances(): Promise<TabularResultDTO> {
  return apiGet<TabularResultDTO>('/gold/account-balances')
}

/** Genera los datamarts de la Capa Oro. */
export function generateGoldDatamarts(): Promise<GoldDatamartResultDTO> {
  return apiPost<GoldDatamartResultDTO>('/gold/generate', {})
}

/** Obtiene resumen de integridad contable (CU-13). */
export function fetchIntegritySummary(): Promise<GoldIntegritySummaryDTO> {
  return apiGet<GoldIntegritySummaryDTO>('/gold/integrity-summary')
}

/** URL directa para descargar informe Excel (CU-14). */
export function getExportExcelUrl(): string {
  return '/api/gold/export-excel'
}

