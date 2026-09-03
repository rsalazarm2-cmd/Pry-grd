<script setup lang="ts">
/**
 * Componente Visual de la Ley de Benford (Fase 2).
 * Visualización comparativa de frecuencias reales vs. la norma logarítmica (log10).
 */
import { ref, computed, onMounted } from 'vue'
import { apiGet } from '@/api/http_client'

const props = defineProps<{ projectId?: string; columnName?: string }>()

interface BenfordDigit {
  digit: number
  expected_freq: number
  actual_freq: number
  actual_count: number
  deviation: number
  is_anomalous: boolean
}

interface BenfordResult {
  column_analyzed: string
  total_samples: number
  chi_square_stat: number
  mad_score: number
  mad_conformity_level: string
  is_distribution_suspicious: boolean
  first_digit_analysis: BenfordDigit[]
  anomalous_digits: number[]
}

const isLoading = ref(true)
const benfordData = ref<BenfordResult | null>(null)
const error = ref<string | null>(null)

const maxFreq = computed(() => {
  if (!benfordData.value?.first_digit_analysis) return 40
  const maxes = benfordData.value.first_digit_analysis.map(d => Math.max(d.actual_freq, d.expected_freq))
  return Math.max(...maxes, 35)
})

async function loadBenfordData() {
  isLoading.value = true
  error.value = null
  try {
    const q = props.projectId ? `?project_id=${encodeURIComponent(props.projectId)}` : ''
    benfordData.value = await apiGet<BenfordResult>(`/audit/benford${q}`)
  } catch (err) {
    error.value = err instanceof Error ? err.message : 'Error analizando Ley de Benford'
  } finally {
    isLoading.value = false
  }
}

onMounted(loadBenfordData)
</script>

<template>
  <div class="benford-card glass-card">
    <div class="card-header">
      <div>
        <h3 class="title">📐 Análisis Forense de la Ley de Benford (1er Dígito)</h3>
        <p class="subtitle">Verificación de patrones de estimación o manipulación en montos contables</p>
      </div>
      <button class="btn-refresh" :disabled="isLoading" @click="loadBenfordData">
        {{ isLoading ? 'Analizando...' : '🔄 Recalcular Benford' }}
      </button>
    </div>

    <div v-if="error" class="alert-error">⚠️ {{ error }}</div>

    <div v-if="benfordData" class="benford-body">
      <!-- Status Banner -->
      <div class="status-banner" :class="benfordData.is_distribution_suspicious ? 'banner-danger' : 'banner-success'">
        <span class="banner-icon">{{ benfordData.is_distribution_suspicious ? '⚠️' : '✅' }}</span>
        <div>
          <div class="banner-title">
            {{ benfordData.is_distribution_suspicious ? 'Distribución Anómala Detectada' : 'Distribución Conforme a la Ley de Benford' }}
          </div>
          <div class="banner-desc">
            Estándar Nigrini MAD: <strong>{{ benfordData.mad_score }}</strong> ({{ benfordData.mad_conformity_level }}) | Chi-cuadrado (χ²): <strong>{{ benfordData.chi_square_stat }}</strong> | Muestras: <strong>{{ benfordData.total_samples }}</strong>
          </div>
        </div>
      </div>

      <!-- Histogram Chart -->
      <div class="chart-container">
        <div v-for="d in benfordData.first_digit_analysis" :key="d.digit" class="bar-col">
          <div class="bar-top-label" :class="{ 'text-alert': d.is_anomalous }">
            {{ d.actual_freq }}%
          </div>
          <div
            class="bar-wrapper"
            :title="`Dígito ${d.digit} | Real: ${d.actual_freq}% (${d.actual_count} casos) | Teórico: ${d.expected_freq}% | Desviación: ${d.deviation}%`"
          >
            <!-- Expected Freq Bar (Ghost Line) -->
            <div class="bar-expected" :style="{ height: `${(d.expected_freq / maxFreq) * 100}%` }" />
            <!-- Actual Freq Bar -->
            <div class="bar-actual" :class="d.is_anomalous ? 'bar-alert' : 'bar-normal'" :style="{ height: `${(d.actual_freq / maxFreq) * 100}%` }" />
          </div>
          <div class="digit-label" :class="{ 'digit-alert': d.is_anomalous }">Dígito {{ d.digit }}</div>
        </div>
      </div>

      <div class="legend-row">
        <span class="legend-item"><span class="box-legend box-blue" /> Frecuencia Real</span>
        <span class="legend-item"><span class="box-legend box-ghost" /> Teórica de Benford (log₁₀)</span>
        <span class="legend-item"><span class="box-legend box-red" /> Anomalía (&gt; 5% Desviación)</span>
      </div>
    </div>
  </div>
</template>

<style scoped>
.benford-card { padding: 1.25rem; display: flex; flex-direction: column; gap: 1rem; }
.card-header { display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid rgba(255,255,255,0.08); pb: 0.75rem; }
.title { font-size: 1.1rem; font-weight: 700; color: #f8fafc; margin: 0; }
.subtitle { font-size: 0.8rem; color: #94a3b8; margin-top: 0.2rem; }
.btn-refresh { background: linear-gradient(135deg, #10b981, #059669); color: #fff; font-weight: 600; padding: 0.4rem 0.85rem; border-radius: 6px; border: none; cursor: pointer; font-size: 0.8rem; }
.status-banner { display: flex; align-items: center; gap: 0.75rem; padding: 0.75rem 1rem; border-radius: 6px; border: 1px solid transparent; }
.banner-success { background: rgba(16, 185, 129, 0.1); border-color: rgba(16, 185, 129, 0.3); color: #34d399; }
.banner-danger { background: rgba(239, 68, 68, 0.1); border-color: rgba(239, 68, 68, 0.3); color: #f87171; }
.banner-title { font-weight: 700; font-size: 0.9rem; }
.banner-desc { font-size: 0.75rem; opacity: 0.9; margin-top: 0.1rem; }
.chart-container { display: grid; grid-template-columns: repeat(9, 1fr); gap: 0.5rem; height: 180px; align-items: end; padding: 0.75rem 0.5rem 0.5rem; background: rgba(0,0,0,0.3); border-radius: 6px; }
.bar-col { display: flex; flex-direction: column; align-items: center; height: 100%; justify-content: flex-end; }
.bar-top-label { font-size: 0.7rem; font-weight: 800; color: #60a5fa; margin-bottom: 0.25rem; }
.text-alert { color: #f43f5e !important; }
.bar-wrapper { position: relative; width: 100%; max-width: 32px; height: 130px; display: flex; align-items: flex-end; justify-content: center; cursor: pointer; }
.bar-expected { position: absolute; bottom: 0; width: 100%; border: 2px dashed #94a3b8; border-bottom: none; border-radius: 4px 4px 0 0; background: rgba(255,255,255,0.05); }
.bar-actual { width: 65%; border-radius: 4px 4px 0 0; z-index: 1; transition: height 0.3s ease; }
.bar-normal { background: linear-gradient(180deg, #3b82f6, #1d4ed8); }
.bar-alert { background: linear-gradient(180deg, #f43f5e, #be123c); }
.digit-label { font-size: 0.75rem; color: #94a3b8; font-weight: 600; margin-top: 0.4rem; }
.digit-alert { color: #f43f5e; font-weight: 800; }
.legend-row { display: flex; gap: 1.25rem; font-size: 0.75rem; color: #94a3b8; justify-content: center; margin-top: 0.25rem; }
.legend-item { display: flex; align-items: center; gap: 0.4rem; }
.box-legend { width: 12px; height: 12px; border-radius: 2px; }
.box-blue { background: #3b82f6; } .box-ghost { border: 2px dashed #94a3b8; } .box-red { background: #f43f5e; }
.alert-error { padding: 0.5rem; background: rgba(239, 68, 68, 0.1); color: #f87171; border-radius: 4px; font-size: 0.85rem; }
</style>
