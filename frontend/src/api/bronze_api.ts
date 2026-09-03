/**
 * Endpoints de la Capa Bronce.
 * Ingesta, profiling, records, mapeo semántico y config.
 */

import { apiGet, apiPost } from './http_client'
import type { TabularResultDTO } from '@/types/gold'
import type { DatasetProfileDTO, ColumnProfileDTO } from '@/types/profiling'
import type {
  BronzeToSilverRulesDTO,
  SystemConfigOptionsDTO,
  IngestionResultDTO,
} from '@/types/bronze'

/** Obtiene registros brutos de la capa Bronce con paginación. */
export function fetchBronzeRecords(
  limit?: number,
  offset?: number,
): Promise<TabularResultDTO> {
  const params = new URLSearchParams()
  if (limit !== undefined) params.set('limit', String(limit))
  if (offset !== undefined) params.set('offset', String(offset))
  const qs = params.toString()
  return apiGet<TabularResultDTO>(`/bronze/records${qs ? `?${qs}` : ''}`)
}

/** Obtiene el perfil estadístico del dataset Bronce. */
export function fetchBronzeProfile(): Promise<DatasetProfileDTO> {
  return apiGet<DatasetProfileDTO>('/bronze/profile')
}

/** Obtiene la sugerencia de mapeo semántico (IA). */
export function fetchSuggestMapping(targetLang: string = 'es', force: boolean = false): Promise<BronzeToSilverRulesDTO> {
  return apiGet<BronzeToSilverRulesDTO>(`/bronze/suggest-mapping?target_lang=${encodeURIComponent(targetLang)}&force=${force}`)
}



/** Obtiene el detalle de perfil de una columna específica. */
export function fetchColumnDetail(columnName: string): Promise<ColumnProfileDTO> {
  return apiGet<ColumnProfileDTO>(`/bronze/column-detail/${encodeURIComponent(columnName)}`)
}

/** Obtiene las opciones de configuración del sistema. */
export function fetchConfigOptions(): Promise<SystemConfigOptionsDTO> {
  return apiGet<SystemConfigOptionsDTO>('/bronze/config-options')
}

/** Ingesta un archivo CSV al Data Lake Bronce. */
export function uploadIngest(formData: FormData, projectId?: string): Promise<IngestionResultDTO> {
  const url = projectId
    ? `/api/bronze/upload-ingest?project_id=${encodeURIComponent(projectId)}`
    : '/api/bronze/upload-ingest'
  return fetch(url, {
    method: 'POST',
    body: formData,
  }).then(async (res) => {
    if (!res.ok) throw new Error(await res.text())
    return res.json() as Promise<IngestionResultDTO>
  })
}

