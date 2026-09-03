<script setup lang="ts">
/**
 * Tabla de datos genérica con scroll horizontal y vertical.
 * Reemplaza raw_data_table.rs de Dioxus.
 * Acepta TabularResultDTO y renderiza columnas/filas dinámicas.
 */
import type { TabularResultDTO } from '@/types/gold'

defineProps<{
  data: TabularResultDTO
  maxHeight?: string
}>()
</script>

<template>
  <div class="table-wrapper" :style="{ maxHeight: maxHeight ?? '500px' }">
    <table class="medallion-table">
      <thead>
        <tr>
          <th v-for="col in data.columns" :key="col">{{ col }}</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="(row, idx) in data.rows" :key="idx">
          <td v-for="col in data.columns" :key="col">
            {{ formatCell(row[col]) }}
          </td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<script lang="ts">
/** Formatea el valor de una celda para renderizado. */
function formatCell(value: unknown): string {
  if (value === null || value === undefined) return '—'
  if (typeof value === 'number') return value.toLocaleString()
  return String(value)
}
</script>

<style scoped>
.table-wrapper {
  overflow: auto;
  border: 1px solid var(--table-border);
  border-radius: 8px;
}

.medallion-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.82rem;
  font-family: var(--font-mono);
}

.medallion-table thead {
  position: sticky;
  top: 0;
  z-index: 1;
}

.medallion-table th {
  background: var(--table-header-bg);
  padding: 0.65rem 0.75rem;
  text-align: left;
  font-weight: 700;
  color: var(--text-main);
  border-bottom: 1px solid var(--table-border);
  white-space: nowrap;
}

.medallion-table td {
  padding: 0.55rem 0.75rem;
  border-bottom: 1px solid var(--table-border);
  color: var(--text-muted);
  white-space: nowrap;
}

.medallion-table tbody tr:hover {
  background: var(--table-hover);
}
</style>
