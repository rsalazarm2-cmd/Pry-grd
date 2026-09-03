<script setup lang="ts">
/**
 * Tabla interactiva de Inspección de Salud por Columna.
 * Muestra nulos, completitud, tipos de datos e indicadores de calidad.
 */
import { ref, computed } from 'vue'
import type { ColumnProfileDTO } from '@/types/profiling'

const props = defineProps<{
  columns: ColumnProfileDTO[]
}>()

const search = ref('')
const filterStatus = ref<'ALL' | 'PERFECT' | 'NULLS' | 'CONSTANT'>('ALL')

const filteredColumns = computed(() => {
  return props.columns.filter((col) => {
    const matchesSearch = col.column_name.toLowerCase().includes(search.value.toLowerCase()) ||
      col.domain_category.toLowerCase().includes(search.value.toLowerCase())
    
    if (!matchesSearch) return false

    if (filterStatus.value === 'PERFECT') return col.null_count === 0 && col.unique_count > 1
    if (filterStatus.value === 'NULLS') return col.null_count > 0
    if (filterStatus.value === 'CONSTANT') return col.unique_count <= 1
    return true
  })
})

function getStatusBadge(col: ColumnProfileDTO) {
  if (col.unique_count <= 1) return { label: 'Constante', class: 'badge-rose' }
  if (col.null_count > 0) return { label: `${col.null_percentage}% Nulos`, class: 'badge-amber' }
  return { label: 'Limpiada / Perfecta', class: 'badge-emerald' }
}
</script>

<template>
  <div class="column-health-container">
    <div class="table-toolbar">
      <h4 class="table-title">📋 Inspección Detallada de Campos y Nulos ({{ filteredColumns.length }}/{{ columns.length }})</h4>
      <div class="toolbar-controls">
        <input
          v-model="search"
          type="text"
          placeholder="🔍 Buscar columna o categoría..."
          class="input-search"
        />
        <select v-model="filterStatus" class="select-filter">
          <option value="ALL">Todas las columnas</option>
          <option value="PERFECT">🟢 Perfectas (0 Nulos)</option>
          <option value="NULLS">🟡 Con Nulos</option>
          <option value="CONSTANT">🔴 Constantes (1 Valor)</option>
        </select>
      </div>
    </div>

    <div class="table-scroll">
      <table class="health-table">
        <thead>
          <tr>
            <th>Nombre del Campo</th>
            <th>Categoría Semántica</th>
            <th>Tipo Dato</th>
            <th>Completitud / Nulos</th>
            <th>Cardinalidad</th>
            <th>Valores Frecuentes / Ejemplo</th>
            <th>Estado Calidad</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="col in filteredColumns" :key="col.column_name">
            <td class="col-name">{{ col.column_name }}</td>
            <td class="col-domain">{{ col.domain_category }}</td>
            <td><span class="type-badge">{{ col.data_type }}</span></td>
            <td>
              <div class="completeness-bar-container">
                <div class="completeness-bar" :style="{ width: `${100 - col.null_percentage}%`, background: col.null_count > 0 ? 'var(--accent-amber)' : 'var(--accent-emerald)' }"></div>
                <span class="completeness-text">{{ (100 - col.null_percentage).toFixed(1) }}% ({{ col.null_count }} nulos)</span>
              </div>
            </td>
            <td class="col-mono">{{ col.unique_count.toLocaleString() }} unq</td>
            <td class="col-samples">
              <span v-for="(item, idx) in col.top_frequencies.slice(0, 2)" :key="idx" class="sample-tag">
                {{ item.value }} ({{ item.percentage }}%)
              </span>
            </td>
            <td>
              <span class="status-tag" :class="getStatusBadge(col).class">
                {{ getStatusBadge(col).label }}
              </span>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<style scoped>
.column-health-container { margin-top: 1.75rem; }

.table-toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 0.75rem;
  margin-bottom: 1rem;
}

.table-title {
  font-size: 1rem;
  font-weight: 700;
  color: var(--text-main);
  margin: 0;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.toolbar-controls { display: flex; gap: 0.6rem; align-items: center; }

.input-search, .select-filter {
  padding: 0.5rem 0.85rem;
  border-radius: 8px;
  border: 1px solid rgba(255, 255, 255, 0.12);
  background: #111827;
  color: var(--text-main);
  font-size: 0.85rem;
  outline: none;
  transition: border-color 0.2s, box-shadow 0.2s;
}

.input-search:focus, .select-filter:focus {
  border-color: #6366f1;
  box-shadow: 0 0 0 2px rgba(99, 102, 241, 0.2);
}

.table-scroll {
  overflow-x: auto;
  max-height: 480px;
  border-radius: 12px;
  border: 1px solid rgba(255, 255, 255, 0.1);
  background: #0f172a;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
}

.health-table {
  width: 100%;
  border-collapse: separate;
  border-spacing: 0;
  font-size: 0.84rem;
  text-align: left;
}

.health-table th {
  position: sticky;
  top: 0;
  z-index: 10;
  background: #1e293b;
  color: #94a3b8;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.04em;
  font-size: 0.74rem;
  padding: 0.85rem 1rem;
  border-bottom: 2px solid rgba(255, 255, 255, 0.08);
  white-space: nowrap;
}

.health-table td {
  padding: 0.75rem 1rem;
  border-bottom: 1px solid rgba(255, 255, 255, 0.04);
  color: #e2e8f0;
  vertical-align: middle;
}

.health-table tbody tr:nth-child(even) {
  background: rgba(255, 255, 255, 0.015);
}

.health-table tbody tr:hover {
  background: rgba(99, 102, 241, 0.08);
}

.col-name {
  font-weight: 700;
  color: #38bdf8;
  font-family: var(--font-mono);
  font-size: 0.85rem;
  white-space: nowrap;
}

.col-domain {
  color: #94a3b8;
  font-size: 0.8rem;
  white-space: nowrap;
}

.col-mono {
  font-family: var(--font-mono);
  color: #cbd5e1;
  white-space: nowrap;
}

.type-badge {
  padding: 0.2rem 0.5rem;
  border-radius: 5px;
  background: rgba(99, 102, 241, 0.2);
  color: #a5b4fc;
  font-family: var(--font-mono);
  font-size: 0.76rem;
  font-weight: 700;
  border: 1px solid rgba(99, 102, 241, 0.3);
}

.completeness-bar-container {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
  min-width: 140px;
}

.completeness-bar {
  height: 5px;
  border-radius: 3px;
  transition: width 0.3s ease;
}

.completeness-text {
  font-size: 0.75rem;
  color: #94a3b8;
  font-family: var(--font-mono);
}

.col-samples {
  display: flex;
  gap: 0.35rem;
  flex-wrap: wrap;
}

.sample-tag {
  padding: 0.15rem 0.45rem;
  border-radius: 5px;
  background: rgba(255, 255, 255, 0.06);
  font-size: 0.74rem;
  color: #cbd5e1;
  max-width: 160px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  border: 1px solid rgba(255, 255, 255, 0.05);
}

.status-tag {
  padding: 0.25rem 0.65rem;
  border-radius: 6px;
  font-weight: 700;
  font-size: 0.76rem;
  white-space: nowrap;
  display: inline-block;
}

.badge-emerald {
  background: rgba(16, 185, 129, 0.18);
  color: #34d399;
  border: 1px solid rgba(16, 185, 129, 0.4);
}

.badge-amber {
  background: rgba(245, 158, 11, 0.18);
  color: #fbbf24;
  border: 1px solid rgba(245, 158, 11, 0.4);
}

.badge-rose {
  background: rgba(239, 68, 68, 0.18);
  color: #f87171;
  border: 1px solid rgba(239, 68, 68, 0.4);
}
</style>

