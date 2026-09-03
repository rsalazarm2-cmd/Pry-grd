/**
 * Composable reactivo para los 4 CU de Fase 1:
 * - CU-01: Redundancia de Fechas (% Match)
 * - CU-02: Delta Fechas → DIFERENCIA_SEGUNDOS
 * - CU-03: Día de Semana + Fin de Semana
 * - CU-04: Preview de Split Cargo/Abono
 *
 * Gestiona loading/error/resultado de cada análisis de forma atómica.
 */

import { ref } from 'vue'
import type { Ref } from 'vue'
import type {
  DateRedundancyResultDTO,
  DateDeltaResultDTO,
  WeekdayResultDTO,
  AmountSplitResultDTO,
} from '@/types/silver'
import {
  fetchDateColumns,
  fetchNumericColumns,
  computeDateRedundancy,
  computeDateDelta,
  computeWeekdayDistribution,
  previewAmountSplit,
} from '@/api/silver_api'

export function useDateExpressions() {
  const dateColumns: Ref<string[]> = ref([])
  const numericColumns: Ref<string[]> = ref([])
  const redundancyResult: Ref<DateRedundancyResultDTO | null> = ref(null)
  const deltaResult: Ref<DateDeltaResultDTO | null> = ref(null)
  const weekdayResult: Ref<WeekdayResultDTO | null> = ref(null)
  const splitResult: Ref<AmountSplitResultDTO | null> = ref(null)
  const isLoading = ref(false)
  const error: Ref<string | null> = ref(null)

  async function loadDateColumns(): Promise<void> {
    try {
      dateColumns.value = await fetchDateColumns()
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Error cargando columnas de fecha'
    }
  }

  async function loadNumericColumns(): Promise<void> {
    try {
      numericColumns.value = await fetchNumericColumns()
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Error cargando columnas numéricas'
    }
  }

  async function analyzeRedundancy(colA: string, colB: string): Promise<void> {
    isLoading.value = true
    error.value = null
    try {
      redundancyResult.value = await computeDateRedundancy({
        date_column_a: colA,
        date_column_b: colB,
      })
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Error en análisis de redundancia'
    } finally {
      isLoading.value = false
    }
  }

  async function analyzeDelta(colA: string, colB: string): Promise<void> {
    isLoading.value = true
    error.value = null
    try {
      deltaResult.value = await computeDateDelta({
        date_column_a: colA,
        date_column_b: colB,
      })
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Error en cálculo de delta'
    } finally {
      isLoading.value = false
    }
  }

  async function analyzeWeekday(dateCol: string): Promise<void> {
    isLoading.value = true
    error.value = null
    try {
      weekdayResult.value = await computeWeekdayDistribution(dateCol)
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Error en distribución de días'
    } finally {
      isLoading.value = false
    }
  }

  async function previewSplit(numericCol: string): Promise<void> {
    isLoading.value = true
    error.value = null
    try {
      splitResult.value = await previewAmountSplit(numericCol)
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Error en preview de split'
    } finally {
      isLoading.value = false
    }
  }

  return {
    dateColumns,
    numericColumns,
    redundancyResult,
    deltaResult,
    weekdayResult,
    splitResult,
    isLoading,
    error,
    loadDateColumns,
    loadNumericColumns,
    analyzeRedundancy,
    analyzeDelta,
    analyzeWeekday,
    previewSplit,
  }
}
