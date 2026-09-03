/**
 * Composable para obtener registros limpios de la capa Plata.
 * Mantiene reactividad automática con el proyecto activo.
 */
import { ref, onMounted, watch } from 'vue'
import type { TabularResultDTO } from '@/types/gold'
import { fetchSilverRecords } from '@/api/silver_api'
import { useProjectStore } from '@/stores/project_store'

export function useSilverRecords() {
  const store = useProjectStore()
  const records = ref<TabularResultDTO | null>(null)
  const currentViewMode = ref('ALL')
  const isLoading = ref(false)
  const error = ref<string | null>(null)

  async function load(viewMode: string = 'ALL'): Promise<void> {
    currentViewMode.value = viewMode
    isLoading.value = true
    error.value = null
    try {
      const res = await fetchSilverRecords(viewMode)
      records.value = res
      if (res && res.total_returned > 0) {
        store.setSilverStatus(true, res.total_returned)
      } else {
        store.setSilverStatus(false, 0)
      }
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Error desconocido'
      store.setSilverStatus(false, 0)
    } finally {
      isLoading.value = false
    }
  }

  onMounted(() => load('ALL'))

  watch(
    () => store.projectId,
    () => {
      load('ALL')
    }
  )

  return { records, currentViewMode, isLoading, error, reload: load }
}
