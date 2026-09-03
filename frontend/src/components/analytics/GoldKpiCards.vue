<script setup lang="ts">
/**
 * CU-15: Componente de Tarjetas Ejecutivas KPI para la Capa Oro.
 * Muestra Débitos Totales, Créditos Totales, Estado de Cuadre y Asientos Descuadrados.
 */
import type { GoldIntegritySummaryDTO } from '@/types/gold'

defineProps<{
  integrity: GoldIntegritySummaryDTO | null
}>()
</script>

<template>
  <div class="kpi-grid">
    <div class="kpi-card">
      <span class="kpi-label">📥 Total Débitos (Cargos)</span>
      <span class="kpi-value">${{ integrity ? integrity.total_debit.toLocaleString('es-ES', { minimumFractionDigits: 2 }) : '0.00' }}</span>
    </div>

    <div class="kpi-card">
      <span class="kpi-label">📤 Total Créditos (Abonos)</span>
      <span class="kpi-value">${{ integrity ? integrity.total_credit.toLocaleString('es-ES', { minimumFractionDigits: 2 }) : '0.00' }}</span>
    </div>

    <div class="kpi-card" :class="integrity?.is_globally_balanced ? 'card-ok' : 'card-warn'">
      <span class="kpi-label">⚖️ Estado de Ecuación Contable</span>
      <span class="kpi-value">{{ integrity?.is_globally_balanced ? 'CUADRADO ✅' : 'DESCUADRADO ⚠️' }}</span>
      <span class="kpi-sub">Dif. Global: ${{ integrity ? integrity.global_imbalance.toFixed(2) : '0.00' }}</span>
    </div>

    <div class="kpi-card">
      <span class="kpi-label">🚨 Asientos Descuadrados</span>
      <span class="kpi-value">{{ integrity ? integrity.imbalanced_entries_count : 0 }}</span>
      <span class="kpi-sub">Monto: ${{ integrity ? integrity.imbalanced_entries_amount.toFixed(2) : '0.00' }}</span>
    </div>
  </div>
</template>

<style scoped>
.kpi-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 1rem; }
.kpi-card { background: rgba(255, 255, 255, 0.04); border: 1px solid rgba(255, 255, 255, 0.1); border-radius: 10px; padding: 1rem; display: flex; flex-direction: column; gap: 0.25rem; }
.kpi-label { font-size: 0.75rem; color: var(--text-muted); font-weight: 600; }
.kpi-value { font-size: 1.3rem; font-weight: 700; color: var(--text-main); font-family: monospace; }
.kpi-sub { font-size: 0.75rem; color: var(--text-muted); }
.card-ok { border-color: rgba(16, 185, 129, 0.4); background: rgba(16, 185, 129, 0.05); }
.card-warn { border-color: rgba(239, 68, 68, 0.4); background: rgba(239, 68, 68, 0.05); }
</style>
