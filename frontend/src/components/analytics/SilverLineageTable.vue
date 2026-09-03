<script setup lang="ts">
/**
 * CU-07: Visualización de Linaje Transparente de Mapeo (Origen ➔ Plata).
 * Muestra el mapa completo de metamorfosis con badges de integridad.
 */
import type { LineageMatrixDTO } from '@/types/silver'

defineProps<{
  lineage: LineageMatrixDTO | null
  isLoading?: boolean
}>()
</script>

<template>
  <div class="lineage-card glass-card">
    <div class="lineage-header">
      <h3 class="lineage-title">🧬 Matriz de Trazabilidad y Linaje (Origen ➔ Plata)</h3>
      <div v-if="lineage" class="lineage-summary">
        <span>Bronce: <strong>{{ lineage.source_columns_count }}</strong> cols</span>
        <span>➔</span>
        <span>Plata: <strong>{{ lineage.target_columns_count }}</strong> cols</span>
      </div>
    </div>

    <div v-if="isLoading" class="loading-state">Calculando matriz de linaje...</div>
    <div v-else-if="!lineage || !lineage.items.length" class="empty-state">
      No hay información de linaje disponible. Ejecuta la compilación Plata.
    </div>

    <div v-else class="table-container">
      <table class="lineage-table">
        <thead>
          <tr>
            <th>Status</th>
            <th>Columna Origen (Bronce)</th>
            <th>Tipo Inferido</th>
            <th>➔</th>
            <th>Columna Plata (Canónica)</th>
            <th>Tipo Destino</th>
            <th>Imputación</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="item in lineage.items" :key="item.source_column">
            <td>
              <span
                class="badge-status"
                :class="item.is_included ? 'status-ok' : 'status-excluded'"
              >
                {{ item.is_included ? 'INCLUIDA' : 'EXCLUIDA' }}
              </span>
            </td>
            <td class="col-code">{{ item.source_column }}</td>
            <td class="col-type">{{ item.inferred_type }}</td>
            <td class="col-arrow">➔</td>
            <td class="col-code target-code">{{ item.target_column }}</td>
            <td class="col-type">{{ item.target_type }}</td>
            <td class="col-impute">{{ item.null_imputation }}</td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<style scoped>
.lineage-card { padding: 1.25rem; display: flex; flex-direction: column; gap: 1rem; }
.lineage-header { display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 0.5rem; }
.lineage-title { font-size: 1.1rem; font-weight: 700; color: var(--text-main); margin: 0; }
.lineage-summary { font-size: 0.85rem; color: var(--text-muted); display: flex; gap: 0.5rem; align-items: center; }
.table-container { overflow-x: auto; max-height: 380px; }
.lineage-table { width: 100%; border-collapse: collapse; font-size: 0.85rem; }
.lineage-table th { text-align: left; padding: 0.5rem; border-bottom: 1px solid rgba(255,255,255,0.1); color: var(--text-muted); }
.lineage-table td { padding: 0.45rem 0.5rem; border-bottom: 1px solid rgba(255,255,255,0.05); }
.badge-status { padding: 0.15rem 0.4rem; border-radius: 4px; font-size: 0.7rem; font-weight: 700; }
.status-ok { background: rgba(16, 185, 129, 0.2); color: #34d399; }
.status-excluded { background: rgba(107, 114, 128, 0.2); color: #9ca3af; }
.col-code { font-family: monospace; color: var(--accent-amber); }
.target-code { color: #60a5fa; font-weight: 600; }
.col-type { font-family: monospace; font-size: 0.75rem; color: var(--text-muted); }
.col-arrow { color: var(--text-muted); font-weight: 700; }
.col-impute { font-size: 0.75rem; color: var(--accent-amber); }
.loading-state, .empty-state { padding: 1.5rem; text-align: center; color: var(--text-muted); font-style: italic; }
</style>
