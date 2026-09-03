/**
 * Composable para ejecutar la transformación Bronce → Plata.
 * Mutation pattern: ejecuta POST y maneja loading/error/resultado.
 */

import { ref } from 'vue'
import type { BronzeToSilverRulesDTO } from '@/types/bronze'
import type { SilverTransformationResultDTO } from '@/types/silver'
import { transformSilver } from '@/api/silver_api'

export function useSilverTransform() {
  const result = ref<SilverTransformationResultDTO | null>(null)
  const isProcessing = ref(false)
  const error = ref<string | null>(null)

  async function execute(rules: BronzeToSilverRulesDTO): Promise<void> {
    isProcessing.value = true
    error.value = null
    result.value = null
    try {
      result.value = await transformSilver(rules)
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Error del motor DuckDB'
    } finally {
      isProcessing.value = false
    }
  }

  return { result, isProcessing, error, execute }
}
