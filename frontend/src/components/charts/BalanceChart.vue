<script setup lang="ts">
/**
 * Gráfico Plotly: Balance por Libro Contable.
 * Renderiza un bar chart horizontal con los saldos por libro.
 */
import { ref, watch, onMounted } from 'vue'
import Plotly from 'plotly.js-dist-min'
import type { TabularResultDTO } from '@/types/gold'

const props = defineProps<{
  data: TabularResultDTO
}>()

const chartEl = ref<HTMLDivElement | null>(null)

function renderChart(): void {
  if (!chartEl.value || !props.data.rows.length) return

  const labels = props.data.rows.map((r) => String(r['LIBRO_CONTABLE'] ?? ''))
  const debits = props.data.rows.map((r) => Number(r['TOTAL_CARGOS'] ?? 0))
  const credits = props.data.rows.map((r) => Number(r['TOTAL_ABONOS'] ?? 0))

  const traces = [
    {
      name: 'Cargos (Debe)',
      x: debits,
      y: labels,
      type: 'bar' as const,
      orientation: 'h' as const,
      marker: { color: '#6366f1' },
    },
    {
      name: 'Abonos (Haber)',
      x: credits,
      y: labels,
      type: 'bar' as const,
      orientation: 'h' as const,
      marker: { color: '#10b981' },
    },
  ]

  const layout = {
    barmode: 'group' as const,
    paper_bgcolor: 'transparent',
    plot_bgcolor: 'transparent',
    font: { family: 'Plus Jakarta Sans', color: '#94a3b8', size: 12 },
    margin: { l: 160, r: 30, t: 10, b: 40 },
    legend: { orientation: 'h' as const, y: -0.15 },
    xaxis: { gridcolor: 'rgba(255,255,255,0.06)' },
    yaxis: { gridcolor: 'rgba(255,255,255,0.06)' },
  }

  Plotly.newPlot(chartEl.value, traces, layout, { responsive: true })
}

onMounted(renderChart)
watch(() => props.data, renderChart)
</script>

<template>
  <div class="chart-container glass-card">
    <h4 class="chart-title">📊 Balance por Libro Contable</h4>
    <div ref="chartEl" class="chart-plot"></div>
  </div>
</template>

<style scoped>
.chart-container { padding: 1.25rem; }
.chart-title { font-size: 1rem; font-weight: 700; color: var(--text-main); margin: 0 0 0.75rem 0; }
.chart-plot { width: 100%; min-height: 350px; }
</style>
