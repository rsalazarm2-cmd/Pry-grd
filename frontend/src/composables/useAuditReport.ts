/**
 * Composable para el informe de auditoría forense.
 * Obtiene descuadres de partida doble y violaciones SoD.
 */

import { ref, onMounted } from 'vue'
import type { InformeIntegridadAuditoriaDTO } from '@/types/audit'
import { fetchAuditReport } from '@/api/audit_api'

export function useAuditReport(parquetPath: string) {
  const report = ref<InformeIntegridadAuditoriaDTO | null>(null)
  const isLoading = ref(false)
  const error = ref<string | null>(null)

  async function load(): Promise<void> {
    if (!parquetPath) return
    isLoading.value = true
    error.value = null
    try {
      report.value = await fetchAuditReport(parquetPath)
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Error desconocido'
    } finally {
      isLoading.value = false
    }
  }

  onMounted(load)

  return { report, isLoading, error, reload: load }
}
