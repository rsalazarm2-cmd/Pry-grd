<script setup lang="ts">
/**
 * Workspace de Auditoría Forense y Detección de Riesgos (Fase 5).
 * Muestra el Financial Integrity Risk Score (CU-19) y la Matriz de Hallazgos (CU-20).
 */
import { onMounted } from 'vue'
import { useForensicAudit } from '@/composables/useForensicAudit'
import AuditAlertTable from '@/components/analytics/AuditAlertTable.vue'

const { matrix, isLoading, error, loadMatrix } = useForensicAudit()

onMounted(loadMatrix)
</script>

<template>
  <div class="workspace">
    <!-- Header -->
    <div class="workspace-header">
      <div>
        <h2 class="workspace-title">🔍 Auditoría Forense: Segregación, Cut-off & Trampas</h2>
        <span class="workspace-sub">Validación de Integridad Contable, SoD (Maker/Checker) y Anomalías Financieras</span>
      </div>
      <button class="btn-refresh" :disabled="isLoading" @click="loadMatrix">
        {{ isLoading ? 'Analizando...' : '🔄 Re-analizar Riesgos' }}
      </button>
    </div>

    <!-- Error Alert -->
    <div v-if="error" class="alert-error">⚠️ {{ error }}</div>

    <!-- Financial Integrity Score Banner (CU-19) -->
    <div v-if="matrix" class="score-banner glass-card" :class="`risk-${matrix.score.nivel_riesgo_global.toLowerCase()}`">
      <div class="score-main">
        <div class="score-circle">
          <span class="score-num">{{ matrix.score.financial_integrity_score }}</span>
          <span class="score-denom">/ 100</span>
        </div>
        <div class="score-info">
          <span class="score-title">Financial Integrity Risk Score</span>
          <span class="score-level">Nivel de Riesgo Global: <strong>{{ matrix.score.nivel_riesgo_global }}</strong></span>
          <span class="score-desc">Calculado sobre {{ matrix.score.total_asientos_analizados }} asientos contables procesados.</span>
        </div>
      </div>

      <div class="score-metrics">
        <div class="m-item">
          <span class="m-val text-rose">{{ matrix.score.sod_violations_count }}</span>
          <span class="m-lbl">Violaciones SoD</span>
        </div>
        <div class="m-item">
          <span class="m-val text-amber">{{ matrix.score.forensic_traps_count }}</span>
          <span class="m-lbl">Trampas Forenses</span>
        </div>
        <div class="m-item">
          <span class="m-val text-blue">{{ matrix.score.cutoff_anomalies_count }}</span>
          <span class="m-lbl">Anomalías Cut-off</span>
        </div>
      </div>
    </div>

    <!-- CU-20: Atomic AuditAlertTable Component -->
    <AuditAlertTable
      v-if="matrix"
      :sod-violations="matrix.sod_violations"
      :traps="matrix.forensic_traps"
      :cutoff-anomalies="matrix.cutoff_anomalies"
    />
  </div>
</template>

<style scoped>
.workspace { display: flex; flex-direction: column; gap: 1.25rem; padding: 1.5rem; }
.workspace-header { display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 1rem; }
.workspace-title { font-size: 1.4rem; font-weight: 700; color: var(--text-main); margin: 0; }
.workspace-sub { font-size: 0.8rem; color: var(--text-muted); }
.btn-refresh { background: rgba(59, 130, 246, 0.2); border: 1px solid #3b82f6; color: #60a5fa; font-weight: 600; padding: 0.45rem 1rem; border-radius: 6px; cursor: pointer; }
.score-banner { display: flex; justify-content: space-between; align-items: center; padding: 1.25rem; flex-wrap: wrap; gap: 1.5rem; border-left: 6px solid #10b981; }
.risk-bajo { border-left-color: #10b981; }
.risk-medio { border-left-color: #f59e0b; }
.risk-alto, .risk-critico { border-left-color: #ef4444; }
.score-main { display: flex; align-items: center; gap: 1.25rem; }
.score-circle { display: flex; align-items: baseline; background: rgba(0,0,0,0.3); padding: 0.75rem 1rem; border-radius: 12px; }
.score-num { font-size: 2.2rem; font-weight: 800; color: var(--text-main); font-family: monospace; }
.score-denom { font-size: 0.85rem; color: var(--text-muted); margin-left: 0.25rem; }
.score-info { display: flex; flex-direction: column; gap: 0.2rem; }
.score-title { font-size: 1.1rem; font-weight: 700; color: var(--text-main); }
.score-level { font-size: 0.9rem; color: var(--text-muted); }
.score-desc { font-size: 0.75rem; color: var(--text-muted); }
.score-metrics { display: flex; gap: 1.5rem; }
.m-item { display: flex; flex-direction: column; align-items: center; }
.m-val { font-size: 1.4rem; font-weight: 700; font-family: monospace; }
.m-lbl { font-size: 0.75rem; color: var(--text-muted); }
.text-rose { color: #f87171; }
.text-amber { color: #fbbf24; }
.text-blue { color: #60a5fa; }
.alert-error { padding: 0.75rem; background: rgba(239, 68, 68, 0.1); border: 1px solid var(--accent-rose); border-radius: 6px; color: var(--accent-rose); }
</style>
