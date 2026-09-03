<template>
  <div class="date-studio-container glass-card">
    <div class="studio-header">
      <div>
        <h3 class="studio-title">📅 Motor de Auditoría y Expresiones de Fechas</h3>
        <p class="studio-subtitle">Análisis de redundancia, deltas de aprobación y patrones en días no laborables para Plata y Oro.</p>
      </div>
      <button @click="loadDateColumns" class="btn-refresh">🔄 Cargar Columnas</button>
    </div>

    <!-- CARDS GRID -->
    <div class="cards-grid">
      
      <!-- CARD 1: REDUNDANCIA -->
      <div class="date-card">
        <div class="card-head">
          <span class="card-title">1. Redundancia (% Iguales)</span>
          <span class="code-badge badge-emerald">fechas_iguales</span>
        </div>
        <p class="card-desc">Compara 2 fechas para medir la coincidencia exacta al milisegundo.</p>
        
        <div class="inputs-group">
          <select v-model="redColA" class="select-custom">
            <option value="" disabled>Seleccionar Fecha A...</option>
            <option v-for="c in dateCols" :key="c" :value="c">{{ c }}</option>
          </select>
          <select v-model="redColB" class="select-custom">
            <option value="" disabled>Seleccionar Fecha B...</option>
            <option v-for="c in dateCols" :key="c" :value="c">{{ c }}</option>
          </select>
        </div>

        <div class="card-footer">
          <button @click="analyzeRedundancy" :disabled="!redColA || !redColB" class="btn-action btn-emerald">
            🔍 Analizar Redundancia
          </button>
          <div v-if="redundancyResult" class="result-box">
            <div class="res-value text-emerald">{{ (redundancyResult.match_percentage ?? 0).toFixed(1) }}%</div>
            <div class="res-detail">{{ (redundancyResult.matching_rows ?? 0).toLocaleString() }} / {{ (redundancyResult.total_rows ?? 0).toLocaleString() }} Filas Iguales</div>
            <div :class="redundancyResult.are_identical ? 'status-pill pill-emerald' : 'status-pill pill-amber'">
              {{ redundancyResult.are_identical ? '🟢 100% Redundante (Batch)' : '🟠 Discrepancias Detectadas' }}
            </div>
          </div>
        </div>
      </div>

      <!-- CARD 2: DELTAS DE TIEMPO -->
      <div class="date-card">
        <div class="card-head">
          <span class="card-title">2. Veloz Aprobación (Deltas)</span>
          <span class="code-badge badge-amber">Maker/Checker</span>
        </div>
        <p class="card-desc">Mide segundos/días transcurridos entre el registro y la aprobación.</p>
        
        <div class="inputs-group">
          <select v-model="deltaColA" class="select-custom">
            <option value="" disabled>Fecha Registro (Origen)...</option>
            <option v-for="c in dateCols" :key="c" :value="c">{{ c }}</option>
          </select>
          <select v-model="deltaColB" class="select-custom">
            <option value="" disabled>Fecha Aprobación (Fin)...</option>
            <option v-for="c in dateCols" :key="c" :value="c">{{ c }}</option>
          </select>
        </div>

        <div class="card-footer">
          <button @click="analyzeDelta" :disabled="!deltaColA || !deltaColB" class="btn-action btn-amber">
            ⚡ Calcular Delta de Tiempo
          </button>
          <div v-if="deltaResult" class="result-box text-left font-sm">
            <div class="flex-between"><span>Promedio:</span> <strong class="text-amber">{{ ((deltaResult.avg_delta_seconds ?? 0) / 3600).toFixed(2) }} horas</strong></div>
            <div class="flex-between"><span>Rango:</span> <span class="text-muted">{{ deltaResult.min_delta_seconds ?? 0 }}s ~ {{ deltaResult.max_delta_seconds ?? 0 }}s</span></div>
            <div v-if="(deltaResult.rapid_approvals_count ?? 0) > 0" class="alert-rapid">
              ⚠️ {{ deltaResult.rapid_approvals_count }} Aprobaciones Instantáneas (&lt; 60s)
            </div>
          </div>
        </div>
      </div>

      <!-- CARD 3: AUDITORÍA FIN DE SEMANA -->
      <div class="date-card">
        <div class="card-head">
          <span class="card-title">3. Día de la Semana</span>
          <span class="code-badge badge-indigo">Weekend Audits</span>
        </div>
        <p class="card-desc">Identifica asientos registrados en Sábado o Domingo (Fin de semana).</p>
        
        <div class="inputs-group">
          <select v-model="weekdayCol" class="select-custom">
            <option value="" disabled>Seleccionar Columna de Fecha...</option>
            <option v-for="c in dateCols" :key="c" :value="c">{{ c }}</option>
          </select>
        </div>

        <div class="card-footer">
          <button @click="analyzeWeekday" :disabled="!weekdayCol" class="w-full btn-action btn-indigo">
            📆 Auditar Días No Laborables
          </button>
          <div v-if="weekdayResult" class="result-box">
            <div class="flex-between"><span>Total Fin de Semana:</span> <strong class="text-rose">{{ (weekdayResult.weekend_count ?? 0).toLocaleString() }} ({{ (weekdayResult.weekend_percentage ?? 0).toFixed(1) }}%)</strong></div>
            <div class="days-bar">
              <div v-for="(wb, idx) in (weekdayResult.weekday_distribution || [])" :key="idx" :class="isWeekend(wb.day) ? 'day-item day-weekend' : 'day-item'" :title="`${wb.day || dayNames[idx]}: ${wb.count} asientos`">
                <div class="day-name">{{ shortDay(wb.day || dayNames[idx]) }}</div>
                <strong class="day-count">{{ wb.count }}</strong>
              </div>
            </div>
          </div>
        </div>
      </div>


    </div>
  </div>
</template>
<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { apiGet, apiPost } from '@/api/http_client'
const props = defineProps<{ projectId?: string }>()
const dateCols = ref<string[]>([])
const redColA = ref(''), redColB = ref(''), deltaColA = ref(''), deltaColB = ref(''), weekdayCol = ref('')
const redundancyResult = ref<any>(null), deltaResult = ref<any>(null), weekdayResult = ref<any>(null)
const dayNames = ['LUNES', 'MARTES', 'MIÉRCOLES', 'JUEVES', 'VIERNES', 'SÁBADO', 'DOMINGO']


function isWeekend(day: string): boolean {
  if (!day) return false
  const d = day.toUpperCase().normalize("NFD").replace(/[\u0300-\u036f]/g, "")
  return d.includes('SABADO') || d.includes('DOMINGO') || d.includes('SAT') || d.includes('SUN')
}

function shortDay(day: string): string {
  if (!day) return ''
  const d = day.toUpperCase().normalize("NFD").replace(/[\u0300-\u036f]/g, "")
  if (d.includes('DOMINGO') || d.includes('SUN')) return 'DOM'
  if (d.includes('LUNES') || d.includes('MON')) return 'LUN'
  if (d.includes('MARTES') || d.includes('TUE')) return 'MAR'
  if (d.includes('MIERCOLES') || d.includes('WED')) return 'MIÉ'
  if (d.includes('JUEVES') || d.includes('THU')) return 'JUE'
  if (d.includes('VIERNES') || d.includes('FRI')) return 'VIE'
  if (d.includes('SABADO') || d.includes('SAT')) return 'SÁB'
  return day.substring(0, 3).toUpperCase()
}

function buildQuery(extraParams: Record<string, string> = {}) {

  const params = new URLSearchParams()
  if (props.projectId) params.append('project_id', props.projectId)
  for (const [k, v] of Object.entries(extraParams)) { if (v) params.append(k, v) }
  const str = params.toString()
  return str ? `?${str}` : ''
}

async function loadDateColumns() {
  try { dateCols.value = await apiGet<string[]>(`/silver/date-columns${buildQuery()}`) }
  catch (err) { console.error('Error cargando columnas:', err) }
}

async function analyzeRedundancy() {
  redundancyResult.value = await apiPost<any>(`/silver/date-redundancy${buildQuery()}`, { date_column_a: redColA.value, date_column_b: redColB.value })
}

async function analyzeDelta() {
  deltaResult.value = await apiPost<any>(`/silver/date-delta${buildQuery()}`, { date_column_a: deltaColA.value, date_column_b: deltaColB.value })
}

async function analyzeWeekday() {
  weekdayResult.value = await apiGet<any>(`/silver/weekday-distribution${buildQuery({ date_column: weekdayCol.value })}`)
}
onMounted(loadDateColumns)
</script>
<style scoped>
.date-studio-container { padding: 1.25rem; display: flex; flex-direction: column; gap: 1.25rem; }
.studio-header { display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid rgba(255,255,255,0.08); pb: 0.75rem; }
.studio-title { font-size: 1.1rem; font-weight: 700; color: #f8fafc; margin: 0; }
.studio-subtitle { font-size: 0.75rem; color: #94a3b8; margin-top: 0.25rem; }
.btn-refresh { background: rgba(255,255,255,0.08); border: 1px solid rgba(255,255,255,0.15); color: #e2e8f0; padding: 0.35rem 0.75rem; border-radius: 6px; font-size: 0.75rem; cursor: pointer; }
.cards-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 1rem; }
.date-card { background: rgba(0,0,0,0.3); border: 1px solid rgba(255,255,255,0.1); border-radius: 8px; padding: 1rem; display: flex; flex-direction: column; justify-content: space-between; gap: 0.75rem; }
.card-head { display: flex; justify-content: space-between; align-items: center; } .card-title { font-size: 0.85rem; font-weight: 700; color: #f1f5f9; }
.code-badge { font-size: 0.7rem; font-family: monospace; padding: 0.15rem 0.4rem; border-radius: 4px; }
.badge-emerald { background: rgba(16, 185, 129, 0.15); color: #34d399; } .badge-amber { background: rgba(245, 158, 11, 0.15); color: #fbbf24; } .badge-indigo { background: rgba(99, 102, 241, 0.15); color: #818cf8; }
.card-desc { font-size: 0.75rem; color: #94a3b8; margin: 0; } .inputs-group { display: flex; flex-direction: column; gap: 0.5rem; }
.select-custom { background: #0f172a; border: 1px solid rgba(255,255,255,0.15); color: #f8fafc; padding: 0.4rem 0.6rem; border-radius: 6px; font-size: 0.8rem; width: 100%; } select option { background-color: #0f172a; color: #f8fafc; }
.card-footer { display: flex; flex-direction: column; gap: 0.75rem; pt: 0.5rem; border-top: 1px solid rgba(255,255,255,0.05); }

.btn-action { border: none; color: #fff; padding: 0.45rem; border-radius: 6px; font-weight: 700; font-size: 0.8rem; cursor: pointer; width: 100%; } .btn-action:disabled { opacity: 0.4; cursor: not-allowed; }
.btn-emerald { background: linear-gradient(135deg, #10b981, #059669); } .btn-amber { background: linear-gradient(135deg, #f59e0b, #d97706); } .btn-indigo { background: linear-gradient(135deg, #6366f1, #4f46e5); }
.result-box { background: #090d16; padding: 0.75rem; border-radius: 6px; border: 1px solid rgba(255,255,255,0.08); text-align: center; } .res-value { font-size: 1.4rem; font-weight: 900; }
.text-emerald { color: #34d399; } .text-amber { color: #fbbf24; } .text-rose { color: #f87171; } .text-muted { color: #94a3b8; } .res-detail { font-size: 0.7rem; color: #94a3b8; font-family: monospace; margin-top: 0.2rem; }
.status-pill { display: inline-block; font-size: 0.65rem; font-weight: 700; padding: 0.2rem 0.5rem; border-radius: 4px; margin-top: 0.5rem; } .pill-emerald { background: rgba(16, 185, 129, 0.2); color: #34d399; } .pill-amber { background: rgba(245, 158, 11, 0.2); color: #fbbf24; }
.flex-between { display: flex; justify-content: space-between; font-size: 0.75rem; } .alert-rapid { background: rgba(225, 29, 72, 0.15); border: 1px solid #e11d48; color: #fda4af; padding: 0.3rem 0.5rem; border-radius: 4px; font-size: 0.7rem; font-weight: 700; margin-top: 0.4rem; }
.days-bar { display: grid; grid-template-columns: repeat(7, 1fr); gap: 0.2rem; margin-top: 0.5rem; width: 100%; box-sizing: border-box; }
.day-item { background: #0f172a; padding: 0.25rem 0.1rem; border-radius: 4px; border: 1px solid rgba(255,255,255,0.08); color: #94a3b8; display: flex; flex-direction: column; align-items: center; justify-content: center; min-width: 0; }
.day-name { font-size: 0.6rem; font-weight: 700; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; width: 100%; text-align: center; }
.day-count { font-size: 0.7rem; color: #f8fafc; font-weight: 800; margin-top: 0.1rem; } .day-weekend { background: rgba(225, 29, 72, 0.2); border-color: #e11d48; color: #fda4af; } .day-weekend .day-count { color: #fda4af; }
</style>
