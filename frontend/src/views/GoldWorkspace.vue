<script setup lang="ts">
/**
 * Workspace de la Capa Oro (Gold): BI, Datamarts Financieros, Integridad y Excel Export.
 * Integra CU-11 (Ledger), CU-12 (Account PyG), CU-13 (Integridad), CU-14 (Excel) y CU-15 (BI Dashboard).
 */
import { ref, onMounted } from 'vue'
import { useGoldBalances } from '@/composables/useGoldBalances'
import DataTable from '@/components/tables/DataTable.vue'
import GoldKpiCards from '@/components/analytics/GoldKpiCards.vue'
import GoldRiskDashboard from '@/components/analytics/GoldRiskDashboard.vue'

const activeTab = ref<'risk' | 'ledger' | 'account'>('risk')
const {
  ledgerBalances, accountBalances, integrity, isLoading, isGenerating, error,
  loadData, generateDatamarts, downloadExcelReport,
} = useGoldBalances()

onMounted(loadData)
</script>

<template>
  <div class="workspace">
    <!-- Header & Action Buttons -->
    <div class="workspace-header">
      <div>
        <h2 class="workspace-title">🥇 Capa Oro: Datamarts Financieros & BI</h2>
        <span class="workspace-sub">Visualización de Balances, Integridad Ecuación Contable y Reportes</span>
      </div>

      <div class="actions">
        <button class="btn-gen" :disabled="isGenerating" @click="generateDatamarts">
          {{ isGenerating ? 'Generando...' : '⚡ Generar Datamarts Oro' }}
        </button>
        <button class="btn-excel" @click="downloadExcelReport">
          📊 Exportar Informe Excel (.xlsx)
        </button>
      </div>
    </div>

    <!-- Error Alert -->
    <div v-if="error" class="alert-error">⚠️ {{ error }}</div>

    <!-- CU-15 & CU-13: Executive KPI Cards -->
    <GoldKpiCards :integrity="integrity" />

    <!-- Tabs Header -->
    <div class="tabs-bar">
      <button
        class="tab-btn"
        :class="{ active: activeTab === 'risk' }"
        @click="activeTab = 'risk'"
      >
        🎯 Scoring Consolidado de Riesgo (0-100)
      </button>
      <button
        class="tab-btn"
        :class="{ active: activeTab === 'ledger' }"
        @click="activeTab = 'ledger'"
      >
        📚 Balance por Libro (Ledger)
      </button>
      <button
        class="tab-btn"
        :class="{ active: activeTab === 'account' }"
        @click="activeTab = 'account'"
      >
        📑 Balance por Cuenta PyG
      </button>
    </div>

    <!-- TAB 0: Scoring Consolidado de Riesgo (0-100) -->
    <GoldRiskDashboard v-if="activeTab === 'risk'" />

    <!-- Content Table: CU-11 Ledger Balance -->
    <div v-else-if="activeTab === 'ledger'" class="glass-card">
      <div class="table-header">
        <span class="table-label">gold_balance_by_ledger.parquet</span>
        <span v-if="ledgerBalances" class="table-count">{{ ledgerBalances.total_returned }} libros</span>
      </div>
      <div v-if="isLoading" class="loading-indicator">Cargando balance por libro...</div>
      <DataTable v-else-if="ledgerBalances && ledgerBalances.rows.length" :data="ledgerBalances" max-height="450px" />
      <div v-else class="empty-state">No hay datos en el datamart por libro. Haz clic en 'Generar Datamarts Oro'.</div>
    </div>

    <!-- Content Table: CU-12 Account Balance -->
    <div v-else-if="activeTab === 'account'" class="glass-card">
      <div class="table-header">
        <span class="table-label">gold_balance_by_account.parquet</span>
        <span v-if="accountBalances" class="table-count">{{ accountBalances.total_returned }} cuentas</span>
      </div>
      <div v-if="isLoading" class="loading-indicator">Cargando balance por cuenta...</div>
      <DataTable v-else-if="accountBalances && accountBalances.rows.length" :data="accountBalances" max-height="450px" />
      <div v-else class="empty-state">No hay datos en el datamart por cuenta. Haz clic en 'Generar Datamarts Oro'.</div>
    </div>
  </div>
</template>

<style scoped>
.workspace { display: flex; flex-direction: column; gap: 1.25rem; padding: 1.5rem; }
.workspace-header { display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 1rem; }
.workspace-title { font-size: 1.4rem; font-weight: 700; color: var(--text-main); margin: 0; }
.workspace-sub { font-size: 0.8rem; color: var(--text-muted); }
.actions { display: flex; gap: 0.5rem; }
.btn-gen { background: linear-gradient(135deg, #f59e0b, #d97706); color: #000; font-weight: 700; padding: 0.45rem 1rem; border-radius: 6px; border: none; cursor: pointer; }
.btn-gen:disabled { opacity: 0.5; cursor: not-allowed; }
.btn-excel { background: linear-gradient(135deg, #10b981, #059669); color: #fff; font-weight: 600; padding: 0.45rem 1rem; border-radius: 6px; border: none; cursor: pointer; }
.tabs-bar { display: flex; gap: 0.5rem; background: rgba(0,0,0,0.3); padding: 0.25rem; border-radius: 8px; width: fit-content; }
.tab-btn { background: transparent; border: none; color: var(--text-muted); padding: 0.4rem 0.85rem; border-radius: 6px; font-weight: 600; cursor: pointer; font-size: 0.85rem; }
.tab-btn.active { background: var(--accent-amber); color: #000; }
.table-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem; }
.table-label { font-size: 0.95rem; font-weight: 600; color: var(--text-main); }
.table-count { font-size: 0.85rem; color: var(--text-muted); }
.loading-indicator, .empty-state { padding: 2rem; text-align: center; color: var(--text-muted); font-style: italic; }
.alert-error { padding: 0.75rem; background: rgba(239, 68, 68, 0.1); border: 1px solid var(--accent-rose); border-radius: 6px; color: var(--accent-rose); }
</style>
