/**
 * Composable para la Capa Oro (BI & Balances Financieros CU-11 a CU-15).
 */

import { ref } from 'vue'
import type { Ref } from 'vue'
import type { TabularResultDTO, GoldIntegritySummaryDTO } from '@/types/gold'
import {
  fetchGoldBalances,
  fetchGoldAccountBalances,
  fetchIntegritySummary,
  generateGoldDatamarts,
  getExportExcelUrl,
} from '@/api/gold_api'

export function useGoldBalances() {
  const ledgerBalances: Ref<TabularResultDTO | null> = ref(null)
  const accountBalances: Ref<TabularResultDTO | null> = ref(null)
  const integrity: Ref<GoldIntegritySummaryDTO | null> = ref(null)
  const isLoading = ref(false)
  const isGenerating = ref(false)
  const error: Ref<string | null> = ref(null)

  async function loadData(): Promise<void> {
    isLoading.value = true
    error.value = null
    try {
      const [lRes, aRes, iRes] = await Promise.all([
        fetchGoldBalances(),
        fetchGoldAccountBalances(),
        fetchIntegritySummary(),
      ])
      ledgerBalances.value = lRes
      accountBalances.value = aRes
      integrity.value = iRes
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Error cargando Capa Oro'
    } finally {
      isLoading.value = false
    }
  }

  async function generateDatamarts(): Promise<boolean> {
    isGenerating.value = true
    error.value = null
    try {
      const res = await generateGoldDatamarts()
      if (res && res.status === 'success') {
        await loadData()
        return true
      }
      return false
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Error generando Capa Oro'
      return false
    } finally {
      isGenerating.value = false
    }
  }

  function downloadExcelReport(): void {
    const url = getExportExcelUrl()
    window.open(url, '_blank')
  }

  return {
    ledgerBalances,
    accountBalances,
    integrity,
    isLoading,
    isGenerating,
    error,
    loadData,
    generateDatamarts,
    downloadExcelReport,
  }
}
