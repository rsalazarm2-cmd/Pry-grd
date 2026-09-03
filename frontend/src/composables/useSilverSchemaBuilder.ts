/**
 * Composable para la gestión interactiva del Schema Canvas (CU-06),
 * linaje transparente (CU-07) y recarga de la receta contable (CU-08).
 */

import { ref, computed } from 'vue'
import type { Ref } from 'vue'
import type { BronzeToSilverRulesDTO } from '@/types/bronze'
import type { LineageMatrixDTO } from '@/types/silver'
import { fetchSavedRules, fetchLineageMatrix, transformSilver } from '@/api/silver_api'
import { useProjectStore } from '@/stores/project_store'

export function useSilverSchemaBuilder() {
  const rules: Ref<BronzeToSilverRulesDTO | null> = ref(null)
  const lineage: Ref<LineageMatrixDTO | null> = ref(null)
  const isRecipeSaved = ref(false)
  const isLoading = ref(false)
  const error: Ref<string | null> = ref(null)

  const activeColumns = computed(() => {
    if (!rules.value) return []
    return Object.entries(rules.value.column_rules).map(([src, rule]) => ({
      source_name: src,
      target_name: rule.new_column_name || src,
      include: rule.include_in_silver,
      target_type: rule.target_data_type || 'VARCHAR',
      null_imputation: rule.null_imputation || 'DEFAULT',
    }))
  })

  async function loadRules(): Promise<void> {
    isLoading.value = true
    error.value = null
    try {
      const saved = await fetchSavedRules()
      if (saved && Object.keys(saved.column_rules).length > 0) {
        rules.value = saved
        isRecipeSaved.value = true
      } else {
        const store = useProjectStore()
        if (store.rules && Object.keys(store.rules.column_rules).length > 0) {
          rules.value = store.rules
        }
      }
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Error cargando receta'
    } finally {
      isLoading.value = false
    }
  }

  async function loadLineage(): Promise<void> {
    try {
      lineage.value = await fetchLineageMatrix()
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Error cargando linaje'
    }
  }

  function toggleColumnInclude(colName: string): void {
    if (!rules.value || !rules.value.column_rules[colName]) return
    rules.value.column_rules[colName].include_in_silver =
      !rules.value.column_rules[colName].include_in_silver
  }

  function updateColumnTarget(colName: string, newTarget: string): void {
    if (!rules.value || !rules.value.column_rules[colName]) return
    rules.value.column_rules[colName].new_column_name = newTarget
  }

  async function compileSchema(): Promise<boolean> {
    if (!rules.value) return false
    isLoading.value = true
    error.value = null
    try {
      await transformSilver(rules.value)
      isRecipeSaved.value = true
      await loadLineage()
      return true
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Error al compilar esquema Plata'
      return false
    } finally {
      isLoading.value = false
    }
  }

  return {
    rules,
    lineage,
    isRecipeSaved,
    isLoading,
    error,
    activeColumns,
    loadRules,
    loadLineage,
    toggleColumnInclude,
    updateColumnTarget,
    compileSchema,
  }
}
