<script setup lang="ts">
/**
 * Componente Ejecutivo de Scoring Consolidado de Riesgo (0-100) - Capa Oro (Fase 3).
 * Muestra métricas consolidadas, ranking de usuarios dondé se concentra el riesgo
 * y matriz priorizada de asientos contables.
 */
import { ref, onMounted } from 'vue'
import { apiGet } from '@/api/http_client'
import type { GoldExecutiveRiskDatamartDTO } from '@/types/gold'

const props = defineProps<{ projectId?: string }>()

const isLoading = ref(true)
const riskDatamart = ref<GoldExecutiveRiskDatamartDTO | null>(null)
const error = ref<string | null>(null)

async function loadRiskDatamart() {
  isLoading.value = true
  error.value = null
  try {
    const q = props.projectId ? `?project_id=${encodeURIComponent(props.projectId)}` : ''
    riskDatamart.value = await apiGet<GoldExecutiveRiskDatamartDTO>(`/gold/risk-datamart${q}`)
  } catch (err) {
    error.value = err instanceof Error ? err.message : 'Error cargando Data Mart de Riesgo'
  } finally {
    isLoading.value = false
  }
}

onMounted(loadRiskDatamart)
</script>

<template>
  <div class="gold-risk-dashboard glass-card">
    <div class="dashboard-header">
      <div>
        <h3 class="title">🥇 Capa Oro: Data Mart Ejecutivo & Scoring de Riesgo (0-100)</h3>
        <p class="subtitle">Consolidación ejecutable de vectores forenses para toma de decisiones y auditoría</p>
      </div>
      <button class="btn-refresh" :disabled="isLoading" @click="loadRiskDatamart">
        {{ isLoading ? 'Procesando...' : '🔄 Generar Data Mart Oro' }}
      </button>
    </div>

    <div v-if="error" class="alert-error">⚠️ {{ error }}</div>

    <div v-if="riskDatamart" class="dashboard-body">
      <!-- Executive KPIs -->
      <div class="kpi-row">
        <div class="kpi-box border-blue">
          <div class="kpi-num">{{ riskDatamart.total_asientos_analizados }}</div>
          <div class="kpi-title">Total Asientos Evaluados</div>
        </div>
        <div class="kpi-box border-amber">
          <div class="kpi-num">{{ riskDatamart.score_promedio_general }} pts</div>
          <div class="kpi-title">Score Promedio de Riesgo</div>
        </div>
        <div class="kpi-box border-rose">
          <div class="kpi-num text-danger">{{ riskDatamart.total_asientos_criticos }}</div>
          <div class="kpi-title">Asientos Críticos (&ge; 70 pts)</div>
        </div>
        <div class="kpi-box border-purple">
          <div class="kpi-num">${{ riskDatamart.total_monto_en_riesgo.toLocaleString() }}</div>
          <div class="kpi-title">Monto Total en Riesgo Alto</div>
        </div>
      </div>

      <!-- Top Users with Risk Grid -->
      <div class="grid-two-cols">
        <!-- User Risk Matrix -->
        <div class="panel-box">
          <h4 class="panel-title">👥 Concentración de Riesgo por Usuario Registrador</h4>
          <table class="data-table">
            <thead>
              <tr>
                <th>Usuario</th>
                <th>Score Prom.</th>
                <th>Asientos Críticos</th>
                <th>Casos SOD</th>
                <th>Monto Total</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="u in riskDatamart.top_usuarios_riesgosos" :key="u.usuario">
                <td class="bold">{{ u.usuario }}</td>
                <td><span class="score-pill" :class="u.score_promedio_usuario >= 50 ? 'pill-red' : 'pill-amber'">{{ u.score_promedio_usuario }}</span></td>
                <td class="text-center font-mono bold text-danger">{{ u.asientos_alto_riesgo }}</td>
                <td class="text-center">{{ u.casos_sod_count }}</td>
                <td class="font-mono">${{ u.monto_total_registrado.toLocaleString() }}</td>
              </tr>
              <tr v-if="riskDatamart.top_usuarios_riesgosos.length === 0">
                <td colspan="5" class="text-center">No hay registros de usuarios.</td>
              </tr>
            </tbody>
          </table>
        </div>

        <!-- Top Critical Journals Matrix -->
        <div class="panel-box">
          <h4 class="panel-title">🚨 Asientos Críticos Priorizados para Auditoría</h4>
          <table class="data-table">
            <thead>
              <tr>
                <th>Folio</th>
                <th>Score</th>
                <th>Monto</th>
                <th>Factores de Riesgo</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="j in riskDatamart.top_asientos_criticos" :key="j.folio_asiento">
                <td class="font-mono bold">{{ j.folio_asiento }}</td>
                <td><span class="score-pill pill-red">{{ j.score_global }} pts</span></td>
                <td class="font-mono">${{ j.monto_total.toLocaleString() }}</td>
                <td>
                  <div class="factors-wrap">
                    <span v-for="(f, fIdx) in j.factores_riesgo" :key="fIdx" class="factor-badge">{{ f }}</span>
                  </div>
                </td>
              </tr>
              <tr v-if="riskDatamart.top_asientos_criticos.length === 0">
                <td colspan="4" class="text-center">Cero asientos críticos detectados.</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.gold-risk-dashboard { padding: 1.25rem; display: flex; flex-direction: column; gap: 1.25rem; }
.dashboard-header { display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid rgba(255,255,255,0.08); pb: 0.75rem; }
.title { font-size: 1.1rem; font-weight: 700; color: #f8fafc; margin: 0; } .subtitle { font-size: 0.8rem; color: #94a3b8; margin-top: 0.2rem; }
.btn-refresh { background: linear-gradient(135deg, #f59e0b, #d97706); color: #fff; font-weight: 700; padding: 0.4rem 0.9rem; border-radius: 6px; border: none; cursor: pointer; font-size: 0.8rem; }
.kpi-row { display: grid; grid-template-columns: repeat(auto-fit, minmax(170px, 1fr)); gap: 0.75rem; }
.kpi-box { background: #090d16; padding: 0.75rem; border-radius: 8px; border-top: 3px solid #3b82f6; }
.border-blue { border-top-color: #3b82f6; } .border-amber { border-top-color: #f59e0b; } .border-rose { border-top-color: #e11d48; } .border-purple { border-top-color: #8b5cf6; }
.kpi-num { font-size: 1.35rem; font-weight: 800; color: #f8fafc; } .text-danger { color: #f43f5e; }
.kpi-title { font-size: 0.75rem; color: #94a3b8; margin-top: 0.25rem; font-weight: 600; }
.grid-two-cols { display: grid; grid-template-columns: repeat(auto-fit, minmax(320px, 1fr)); gap: 1rem; }
.panel-box { background: rgba(0,0,0,0.25); padding: 0.75rem; border-radius: 6px; border: 1px solid rgba(255,255,255,0.05); display: flex; flex-direction: column; gap: 0.5rem; }
.panel-title { font-size: 0.85rem; font-weight: 700; color: #f8fafc; margin: 0; }
.data-table { width: 100%; border-collapse: collapse; font-size: 0.75rem; text-align: left; }
.data-table th { padding: 0.35rem 0.5rem; color: #94a3b8; border-bottom: 1px solid rgba(255,255,255,0.1); }
.data-table td { padding: 0.4rem 0.5rem; border-bottom: 1px solid rgba(255,255,255,0.05); color: #f8fafc; }
.score-pill { padding: 0.1rem 0.35rem; border-radius: 4px; font-weight: 800; font-size: 0.7rem; }
.pill-red { background: rgba(239, 68, 68, 0.2); color: #f87171; border: 1px solid #ef4444; }
.pill-amber { background: rgba(245, 158, 11, 0.2); color: #fbbf24; border: 1px solid #f59e0b; }
.factors-wrap { display: flex; flex-wrap: wrap; gap: 0.2rem; }
.factor-badge { background: rgba(255,255,255,0.08); font-size: 0.65rem; padding: 0.05rem 0.3rem; border-radius: 3px; color: #cbd5e1; }
.alert-error { padding: 0.5rem; background: rgba(239, 68, 68, 0.1); color: #f87171; border-radius: 4px; font-size: 0.85rem; }
.font-mono { font-family: monospace; } .bold { font-weight: 700; } .text-center { text-align: center; }
</style>
