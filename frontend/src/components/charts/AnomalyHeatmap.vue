<script setup lang="ts">
/**
 * Gráfico Plotly: Heatmap de Anomalías.
 * Visualiza la matriz de anomalías del profiling como heatmap.
 */
import { ref, watch, onMounted } from 'vue'
import Plotly from 'plotly.js-dist-min'
import type { AnomalyMatrixDTO } from '@/types/profiling'

const props = defineProps<{
  matrix: AnomalyMatrixDTO
}>()

const chartEl = ref<HTMLDivElement | null>(null)

const ANOMALY_LABELS = [
  'Descuadres Cabecera',
  'Errores Tipo Cambio',
  'Incoherencias Temporal',
  'Flexfields Malformados',
  'Discrepancias Usuario',
  'Movimiento Cero',
]

function renderChart(): void {
  if (!chartEl.value) return

  const m = props.matrix
  const values = [[
    m.a1_header_imbalances,
    m.a2_exchange_rate_errors,
    m.a3_timeline_incoherences,
    m.a4_malformed_flexfields,
    m.a5_user_mismatches,
    m.a6_zero_movement_rows,
  ]]

  const trace = {
    z: values,
    x: ANOMALY_LABELS,
    y: ['Anomalías'],
    type: 'heatmap' as const,
    colorscale: [[0, '#10b981'], [0.5, '#f59e0b'], [1, '#f43f5e']],
    showscale: true,
  }

  const layout = {
    paper_bgcolor: 'transparent',
    plot_bgcolor: 'transparent',
    font: { family: 'Plus Jakarta Sans', color: '#94a3b8', size: 11 },
    margin: { l: 80, r: 30, t: 10, b: 100 },
    xaxis: { tickangle: -35 },
    height: 180,
  }

  Plotly.newPlot(chartEl.value, [trace], layout, { responsive: true })
}

onMounted(renderChart)
watch(() => props.matrix, renderChart)
</script>

<template>
  <div class="chart-container glass-card">
    <h4 class="chart-title">🔥 Heatmap de Anomalías</h4>
    <div ref="chartEl" class="chart-plot"></div>
  </div>
</template>

<style scoped>
.chart-container { padding: 1.25rem; }
.chart-title { font-size: 1rem; font-weight: 700; color: var(--text-main); margin: 0 0 0.75rem 0; }
.chart-plot { width: 100%; }
</style>
