<script setup lang="ts">
/**
 * CU-20: Componente Atómico para la Visualización de Alertas de Auditoría Forense.
 * Muestra violaciones de SoD, Trampas Forenses y Anomalías Cut-off con Badges de Riesgo.
 */
import type { SodViolationDTO, ForensicTrapAlertDTO, CutoffAnomalyDTO } from '@/types/audit'

defineProps<{
  sodViolations: SodViolationDTO[]
  traps: ForensicTrapAlertDTO[]
  cutoffAnomalies: CutoffAnomalyDTO[]
}>()
</script>

<template>
  <div class="audit-alert-container glass-card">
    <h3 class="container-title">🚨 Matriz de Hallazgos Forenses y Riesgo Financiero</h3>

    <!-- Section 1: SoD Violations (CU-16) -->
    <div class="section-block">
      <div class="block-title">
        <span>👤 Violaciones Segregación de Funciones (Maker == Checker)</span>
        <span class="count-badge">{{ sodViolations.length }} hallazgos</span>
      </div>
      <div v-if="sodViolations.length" class="table-wrap">
        <table class="audit-table">
          <thead>
            <tr>
              <th>Folio Asiento</th>
              <th>Registrador (Maker)</th>
              <th>Aprobador (Checker)</th>
              <th>Monto Total</th>
              <th>Riesgo</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="(item, idx) in sodViolations" :key="idx">
              <td class="col-code">{{ item.folio_asiento }}</td>
              <td class="col-user">{{ item.usuario_registrador }}</td>
              <td class="col-user user-match">{{ item.usuario_aprobador }}</td>
              <td class="col-num">${{ item.monto_total.toLocaleString('es-ES', { minimumFractionDigits: 2 }) }}</td>
              <td><span class="badge badge-risk-high">ALTO (SoD)</span></td>
            </tr>
          </tbody>
        </table>
      </div>
      <div v-else class="empty-msg">No se detectaron violaciones de Maker == Checker.</div>
    </div>

    <!-- Section 2: Forensic Traps (CU-17) -->
    <div class="section-block">
      <div class="block-title">
        <span>🕵️ Trampas Forenses & Asientos Fantasma</span>
        <span class="count-badge">{{ traps.length }} hallazgos</span>
      </div>
      <div v-if="traps.length" class="table-wrap">
        <table class="audit-table">
          <thead>
            <tr>
              <th>Folio Asiento</th>
              <th>Tipo de Trampa</th>
              <th>Descripción Hallazgo</th>
              <th>Monto</th>
              <th>Riesgo</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="(item, idx) in traps" :key="idx">
              <td class="col-code">{{ item.folio_asiento }}</td>
              <td><span class="trap-type">{{ item.tipo_trampa }}</span></td>
              <td class="col-desc">{{ item.descripcion_trampa }}</td>
              <td class="col-num">${{ item.monto.toLocaleString('es-ES', { minimumFractionDigits: 2 }) }}</td>
              <td>
                <span :class="item.nivel_riesgo === 'ALTO' ? 'badge badge-risk-high' : 'badge badge-risk-med'">
                  {{ item.nivel_riesgo }}
                </span>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
      <div v-else class="empty-msg">No se detectaron trampas forenses de horario o montos redondos.</div>
    </div>

    <!-- Section 3: Cut-off Anomalies (CU-18) -->
    <div class="section-block">
      <div class="block-title">
        <span>📅 Anomalías de Corte Temporal (Cut-off & Backdating)</span>
        <span class="count-badge">{{ cutoffAnomalies.length }} hallazgos</span>
      </div>
      <div v-if="cutoffAnomalies.length" class="table-wrap">
        <table class="audit-table">
          <thead>
            <tr>
              <th>Folio Asiento</th>
              <th>Periodo</th>
              <th>F. Registro</th>
              <th>F. Contabilización</th>
              <th>Descalce (Días)</th>
              <th>Riesgo</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="(item, idx) in cutoffAnomalies" :key="idx">
              <td class="col-code">{{ item.folio_asiento }}</td>
              <td>{{ item.periodo_contable }}</td>
              <td>{{ item.fecha_registro }}</td>
              <td>{{ item.fecha_contabilizacion }}</td>
              <td class="col-num text-warn">{{ item.diferencia_dias }} días</td>
              <td><span class="badge badge-risk-high">ALTO (Cut-off)</span></td>
            </tr>
          </tbody>
        </table>
      </div>
      <div v-else class="empty-msg">No se encontraron descalces de cierre de periodo.</div>
    </div>
  </div>
</template>

<style scoped>
.audit-alert-container { padding: 1.25rem; display: flex; flex-direction: column; gap: 1.25rem; }
.container-title { font-size: 1.1rem; font-weight: 700; color: var(--text-main); margin: 0; }
.section-block { display: flex; flex-direction: column; gap: 0.5rem; background: rgba(0,0,0,0.2); padding: 0.75rem; border-radius: 8px; }
.block-title { display: flex; justify-content: space-between; align-items: center; font-size: 0.9rem; font-weight: 600; color: var(--text-main); }
.count-badge { font-size: 0.75rem; background: rgba(255,255,255,0.1); padding: 0.15rem 0.5rem; border-radius: 12px; color: var(--text-muted); }
.table-wrap { overflow-x: auto; max-height: 250px; }
.audit-table { width: 100%; border-collapse: collapse; font-size: 0.825rem; text-align: left; }
.audit-table th { background: rgba(0,0,0,0.4); padding: 0.45rem 0.6rem; color: var(--text-muted); font-weight: 600; }
.audit-table td { padding: 0.45rem 0.6rem; border-bottom: 1px solid rgba(255,255,255,0.05); }
.col-code { font-family: monospace; font-weight: 700; color: var(--accent-amber); }
.col-user { font-family: monospace; }
.user-match { color: #f87171; font-weight: 700; }
.col-num { text-align: right; font-family: monospace; font-weight: 600; }
.col-desc { color: var(--text-muted); }
.trap-type { font-size: 0.75rem; background: rgba(59, 130, 246, 0.2); color: #60a5fa; padding: 0.1rem 0.4rem; border-radius: 4px; }
.badge { font-size: 0.7rem; font-weight: 700; padding: 0.15rem 0.45rem; border-radius: 4px; text-transform: uppercase; }
.badge-risk-high { background: rgba(239, 68, 68, 0.2); color: #f87171; border: 1px solid rgba(239, 68, 68, 0.4); }
.badge-risk-med { background: rgba(245, 158, 11, 0.2); color: #fbbf24; border: 1px solid rgba(245, 158, 11, 0.4); }
.empty-msg { font-size: 0.8rem; color: var(--text-muted); font-style: italic; padding: 0.5rem 0; }
.text-warn { color: #fbbf24; font-weight: 700; }
</style>
