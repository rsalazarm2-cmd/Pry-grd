<script setup lang="ts">
/**
 * Componente de Visualización del Motor Vectorial Forense de 5 Dimensiones (Fase 1).
 * Muestra KPIs analíticos de los 5 vectores y el ranking de asientos de alto riesgo.
 */
import { ref, onMounted } from 'vue'
import { fetchForensicSummary, fetchForensicHighRisk } from '@/api/silver_api'
import type { ForensicAuditSummaryDTO, ForensicVectorRecordDTO } from '@/types/silver'
import BenfordChart from '@/components/analytics/BenfordChart.vue'

const props = defineProps<{ projectId?: string }>()

const isLoading = ref(true)
const summary = ref<ForensicAuditSummaryDTO | null>(null)
const highRiskRecords = ref<ForensicVectorRecordDTO[]>([])
const error = ref<string | null>(null)

async function loadForensicData() {
  isLoading.value = true
  error.value = null
  try {
    const [sumData, recData] = await Promise.all([
      fetchForensicSummary(props.projectId),
      fetchForensicHighRisk(props.projectId, 25),
    ])
    summary.value = sumData
    highRiskRecords.value = recData
  } catch (err) {
    error.value = err instanceof Error ? err.message : 'Error cargando vectores forenses'
  } finally {
    isLoading.value = false
  }
}

onMounted(loadForensicData)
</script>

<template>
  <div class="forensic-studio glass-card">
    <div class="studio-header">
      <div>
        <h3 class="title">🛡️ Motor Vectorial de Auditoría Forense (5D)</h3>
        <p class="subtitle">Evaluación de patrones multidimensionales en DuckDB (Fase 1)</p>
      </div>
      <button class="btn-refresh" :disabled="isLoading" @click="loadForensicData">
        {{ isLoading ? 'Analizando...' : '🔄 Recalcular Vectores' }}
      </button>
    </div>

    <div v-if="error" class="alert-error">⚠️ {{ error }}</div>

    <!-- Executive Summary KPIs (5 Dimensions) -->
    <div v-if="summary" class="kpi-grid">
      <div class="kpi-card border-temporal">
        <div class="kpi-val">{{ summary.total_alertas_temporales }}</div>
        <div class="kpi-lbl">📅 R. Temporal (Fin de Semana / Nocturno)</div>
      </div>
      <div class="kpi-card border-sod">
        <div class="kpi-val">{{ summary.total_alertas_sod }}</div>
        <div class="kpi-lbl">👤 Violación SOD (Maker = Checker)</div>
      </div>
      <div class="kpi-card border-nlp">
        <div class="kpi-val">{{ summary.total_alertas_semanticas }}</div>
        <div class="kpi-lbl">📝 Semántica NLP (Glosas Sospechosas)</div>
      </div>
      <div class="kpi-card border-split">
        <div class="kpi-val">{{ summary.total_alertas_fraccionamiento }}</div>
        <div class="kpi-lbl">⚡ Fraccionamiento (Split Window Sum)</div>
      </div>
      <div class="kpi-card border-risk">
        <div class="kpi-val text-alert">{{ summary.total_asientos_alto_riesgo }}</div>
        <div class="kpi-lbl">🔴 Asientos de Alto Riesgo (Score &ge; 40)</div>
      </div>
    </div>

    <!-- Benford's Law Forensic Chart (Fase 2) -->
    <BenfordChart :project-id="props.projectId" />

    <!-- High Risk Journal Table -->
    <div class="table-container">
      <h4 class="table-title">🔥 Ranking de Asientos con Mayor Vector de Riesgo</h4>
      <table class="forensic-table">
        <thead>
          <tr>
            <th>Folio</th>
            <th>Score Riesgo</th>
            <th>V1 Temporal</th>
            <th>V2 SOD</th>
            <th>V3 Semántica NLP</th>
            <th>V5 Fraccionamiento</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="rec in highRiskRecords" :key="rec.folio_asiento">
            <td class="font-mono bold">{{ rec.folio_asiento }}</td>
            <td>
              <span class="score-badge" :class="rec.score_riesgo_preliminar >= 40 ? 'badge-high' : 'badge-mid'">
                {{ rec.score_riesgo_preliminar }} pts
              </span>
            </td>
            <td>
              <span v-if="rec.vector_temporal.flag_fin_semana" class="tag tag-red">Fin de Semana</span>
              <span v-else-if="rec.vector_temporal.flag_horario_nocturno" class="tag tag-amber">Nocturno</span>
              <span v-else class="tag tag-gray">Normal</span>
            </td>
            <td>
              <span v-if="rec.vector_sod.flag_mismo_usuario" class="tag tag-red">Maker=Checker</span>
              <span v-else class="tag tag-gray">OK</span>
            </td>
            <td>
              <span v-if="rec.vector_semantico.flag_glosa_sospechosa" class="tag tag-amber">Glosa Anómala</span>
              <span v-else class="tag tag-gray">Normal</span>
            </td>
            <td>
              <span v-if="rec.vector_acumulado.flag_posible_fraccionamiento" class="tag tag-purple">
                Posible Split (${{ rec.vector_acumulado.monto_acumulado_dia_usuario.toLocaleString() }})
              </span>
              <span v-else class="tag tag-gray">Normal</span>
            </td>
          </tr>
          <tr v-if="highRiskRecords.length === 0">
            <td colspan="6" class="text-center">No se detectaron asientos anómalos.</td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<style scoped>
.forensic-studio { padding: 1.25rem; display: flex; flex-direction: column; gap: 1.25rem; }
.studio-header { display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid rgba(255,255,255,0.08); pb: 0.75rem; }
.title { font-size: 1.1rem; font-weight: 700; color: #f8fafc; margin: 0; }
.subtitle { font-size: 0.8rem; color: #94a3b8; margin-top: 0.2rem; }
.btn-refresh { background: linear-gradient(135deg, #6366f1, #4f46e5); color: #fff; font-weight: 600; padding: 0.4rem 0.9rem; border-radius: 6px; border: none; cursor: pointer; font-size: 0.8rem; }
.kpi-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(160px, 1fr)); gap: 0.75rem; }
.kpi-card { background: #090d16; padding: 0.75rem; border-radius: 8px; border-left: 4px solid #3b82f6; display: flex; flex-direction: column; }
.border-temporal { border-left-color: #f59e0b; } .border-sod { border-left-color: #ef4444; } .border-nlp { border-left-color: #8b5cf6; } .border-split { border-left-color: #ec4899; } .border-risk { border-left-color: #e11d48; }
.kpi-val { font-size: 1.4rem; font-weight: 800; color: #f8fafc; } .text-alert { color: #f43f5e; }
.kpi-lbl { font-size: 0.7rem; color: #94a3b8; font-weight: 600; margin-top: 0.25rem; }
.table-container { display: flex; flex-direction: column; gap: 0.5rem; background: rgba(0,0,0,0.2); padding: 0.75rem; border-radius: 6px; }
.table-title { font-size: 0.9rem; font-weight: 700; color: #f8fafc; margin: 0; }
.forensic-table { width: 100%; border-collapse: collapse; font-size: 0.8rem; text-align: left; }
.forensic-table th { padding: 0.4rem 0.6rem; color: #94a3b8; border-bottom: 1px solid rgba(255,255,255,0.1); }
.forensic-table td { padding: 0.45rem 0.6rem; border-bottom: 1px solid rgba(255,255,255,0.05); color: #f8fafc; }
.score-badge { padding: 0.15rem 0.4rem; border-radius: 4px; font-weight: 700; font-size: 0.75rem; }
.badge-high { background: rgba(225, 29, 72, 0.2); color: #fda4af; border: 1px solid #e11d48; }
.badge-mid { background: rgba(245, 158, 11, 0.2); color: #fcd34d; border: 1px solid #f59e0b; }
.tag { padding: 0.1rem 0.35rem; border-radius: 3px; font-size: 0.7rem; font-weight: 600; }
.tag-red { background: rgba(239, 68, 68, 0.2); color: #f87171; }
.tag-amber { background: rgba(245, 158, 11, 0.2); color: #fbbf24; }
.tag-purple { background: rgba(168, 85, 247, 0.2); color: #c084fc; }
.tag-gray { background: rgba(255,255,255,0.05); color: #64748b; }
.alert-error { padding: 0.5rem; background: rgba(239, 68, 68, 0.1); color: #f87171; border-radius: 4px; font-size: 0.85rem; }
.font-mono { font-family: monospace; } .bold { font-weight: 700; } .text-center { text-align: center; }
</style>
