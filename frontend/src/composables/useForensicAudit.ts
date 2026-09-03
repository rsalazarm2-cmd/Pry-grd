/**
 * Composable para Auditoría Forense y Detección de Riesgos (CU-16 a CU-20).
 */

import { ref } from 'vue'
import type { Ref } from 'vue'
import type { ForensicAuditMatrixDTO } from '@/types/audit'
import { fetchForensicMatrix } from '@/api/audit_api'

export function useForensicAudit() {
  const matrix: Ref<ForensicAuditMatrixDTO | null> = ref(null)
  const isLoading = ref(false)
  const error: Ref<string | null> = ref(null)

  async function loadMatrix(): Promise<void> {
    isLoading.value = true
    error.value = null
    try {
      matrix.value = await fetchForensicMatrix()
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Error cargando auditoría forense'
    } finally {
      isLoading.value = false
    }
  }

  return {
    matrix,
    isLoading,
    error,
    loadMatrix,
  }
}
