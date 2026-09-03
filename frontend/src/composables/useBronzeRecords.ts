/**
 * Composable para obtener registros de la capa Bronce (raw data).
 * Mantiene sincronización automática con el proyecto activo de Pinia.
 */

import { ref, onMounted, watch } from 'vue'
import type { TabularResultDTO } from '@/types/gold'
import { fetchBronzeRecords } from '@/api/bronze_api'
import { useProjectStore } from '@/stores/project_store'

export function useBronzeRecords(limit = 500) {
  const store = useProjectStore()
  const records = ref<TabularResultDTO | null>(null)
  const isLoading = ref(false)
  const error = ref<string | null>(null)

  async function load(): Promise<void> {
    isLoading.value = true
    error.value = null
    try {
      records.value = await fetchBronzeRecords(limit)
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Error desconocido'
    } finally {
      isLoading.value = false
    }
  }

  onMounted(load)

  watch(
    () => store.projectId,
    () => {
      load()
    }
  )

  return { records, isLoading, error, reload: load }
}
