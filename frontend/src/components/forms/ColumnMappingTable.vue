<script setup lang="ts">
/**
 * Tabla interactiva de Mapeo y Reglas por Columna.
 * Oculta la opción de imputar nulos si la columna está 100% completa (sin nulos).
 * Muestra únicamente opciones de imputación coherentes según el tipo (Texto vs Número vs Fecha).
 */
import { ref, computed } from 'vue'
import { useProjectStore } from '@/stores/project_store'

const store = useProjectStore()
const search = ref('')
const filterIncluded = ref<'ALL' | 'INCLUDED' | 'EXCLUDED'>('ALL')

const columnEntries = computed(() => {
  const entries = Object.entries(store.rules.column_rules)
  return entries.filter(([colName, rule]) => {
    const matchesSearch = colName.toLowerCase().includes(search.value.toLowerCase()) ||
      (rule.new_column_name && rule.new_column_name.toLowerCase().includes(search.value.toLowerCase()))
    
    if (!matchesSearch) return false
    if (filterIncluded.value === 'INCLUDED') return rule.include_in_silver
    if (filterIncluded.value === 'EXCLUDED') return !rule.include_in_silver
    return true
  })
})

function getNullStrategies(targetDataType: string | null) {
  const dt = (targetDataType || '').toUpperCase()
  const isNumeric = ['DOUBLE', 'BIGINT', 'INTEGER', 'FLOAT', 'DECIMAL', 'NUMERIC'].includes(dt)
  const isText = ['VARCHAR', 'TEXT', 'STRING', 'CHAR(3)'].includes(dt)

  if (isNumeric) {
    return [
      { id: 'ZERO', label: 'Imputar Cero (0)' },
      { id: 'MEAN', label: 'Imputar Promedio' },
      { id: 'MEDIAN', label: 'Imputar Mediana' },
      { id: 'MODE', label: 'Imputar Moda (Más Frecuente)' },
      { id: 'DEFAULT', label: 'Dejar Nulo' }
    ]
  } else if (isText) {
    return [
      { id: 'UNKNOWN', label: 'Imputar "DESCONOCIDO"' },
      { id: 'MODE', label: 'Imputar Moda (Más Frecuente)' },
      { id: 'DEFAULT', label: 'Dejar Nulo' }
    ]
  } else {
    return [
      { id: 'MODE', label: 'Imputar Moda (Más Frecuente)' },
      { id: 'DEFAULT', label: 'Dejar Nulo' }
    ]
  }
}
</script>

<template>
  <div class="mapping-table-container">
    <div class="toolbar">
      <div class="toolbar-info">
        <span class="badge-count">
          {{ columnEntries.length }} / {{ Object.keys(store.rules.column_rules).length }} Campos
        </span>
        <span class="info-hint">Ajusta renombrado, tipados, imputación y limpieza</span>
      </div>
      <div class="toolbar-actions">
        <input v-model="search" type="text" placeholder="🔍 Buscar campo..." class="input-search" />
        <select v-model="filterIncluded" class="select-filter">
          <option value="ALL">Todas las columnas</option>
          <option value="INCLUDED">✅ Incluidas en Plata</option>
          <option value="EXCLUDED">🚫 Excluidas / Constantes</option>
        </select>
      </div>
    </div>

    <div class="table-wrapper">
      <table class="mapping-table">
        <thead>
          <tr>
            <th>Incluir</th>
            <th>Origen (Bronce)</th>
            <th>Nombre Destino (Plata)</th>
            <th>Tipo Dato</th>
            <th>Imputación Nulos</th>
            <th>Categoría</th>
            <th>Limpiar Comas</th>
            <th>Limpiar Puntos</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="[colName, rule] in columnEntries" :key="colName" :class="{ 'row-disabled': !rule.include_in_silver }">
            <td class="col-center">
              <input type="checkbox" v-model="rule.include_in_silver" class="checkbox-custom" />
            </td>
            <td class="col-orig">
              <span class="orig-name">{{ colName }}</span>
              <span v-if="rule.is_constant" class="tag-const">Constante</span>
            </td>
            <td>
              <input type="text" v-model="rule.new_column_name" placeholder="Nombre..." class="input-table-text" :disabled="!rule.include_in_silver" />
            </td>
            <td>
              <select v-model="rule.target_data_type" class="select-table" :disabled="!rule.include_in_silver">
                <option v-for="opt in store.configOptions?.available_data_types || []" :key="opt.id" :value="opt.id">
                  {{ opt.label }}
                </option>
                <option value="DATE">DATE (Fecha)</option>
                <option value="TIMESTAMP">TIMESTAMP (Fecha/Hora)</option>
                <option value="CHAR(3)">CHAR(3) (Texto Corto)</option>
              </select>
            </td>
            <td>
              <span v-if="!rule.has_nulls" class="badge-success" title="El campo está 100% completo en el dataset">
                ✅ Sin Nulos (100%)
              </span>
              <select v-else v-model="rule.null_imputation" class="select-table" :disabled="!rule.include_in_silver">
                <option v-for="opt in getNullStrategies(rule.target_data_type)" :key="opt.id" :value="opt.id">
                  {{ opt.label }}
                </option>
              </select>
            </td>
            <td class="col-center">
              <input type="checkbox" v-model="rule.convert_to_category" class="checkbox-custom" :disabled="!rule.include_in_silver" title="Convertir a Categoría / ENUM" />
            </td>
            <td class="col-center">
              <span v-if="!rule.has_commas" class="badge-na" title="El dato no contiene comas">N/A</span>
              <input v-else type="checkbox" v-model="rule.clean_commas" class="checkbox-custom" :disabled="!rule.include_in_silver" title="Eliminar comas del texto/monto" />
            </td>
            <td class="col-center">
              <span v-if="!rule.has_dots || ['DOUBLE','FLOAT','DECIMAL'].includes(rule.target_data_type || '')" class="badge-na" title="El dato no contiene puntos o protege decimales">N/A</span>
              <input v-else type="checkbox" v-model="rule.clean_dots" class="checkbox-custom" :disabled="!rule.include_in_silver" title="Eliminar puntos del texto/monto" />
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<style scoped>
.mapping-table-container { margin-top: 1rem; }
.toolbar { display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 0.75rem; margin-bottom: 0.75rem; }
.toolbar-info { display: flex; align-items: center; gap: 0.75rem; }
.badge-count { background: rgba(99, 102, 241, 0.2); color: #a5b4fc; padding: 0.35rem 0.75rem; border-radius: 6px; font-weight: 700; font-size: 0.8rem; border: 1px solid rgba(99, 102, 241, 0.3); }
.info-hint { color: var(--text-muted); font-size: 0.82rem; }
.toolbar-actions { display: flex; gap: 0.5rem; }
.input-search, .select-filter { padding: 0.4rem 0.75rem; border-radius: 6px; border: 1px solid rgba(255,255,255,0.12); background: #111827; color: var(--text-main); font-size: 0.82rem; outline: none; }
.table-wrapper { max-height: 420px; overflow-y: auto; border-radius: 8px; border: 1px solid rgba(255, 255, 255, 0.1); background: #0f172a; }
.mapping-table { width: 100%; border-collapse: collapse; font-size: 0.82rem; text-align: left; }
.mapping-table th { position: sticky; top: 0; z-index: 5; background: #1e293b; color: #94a3b8; font-weight: 700; padding: 0.75rem 0.85rem; border-bottom: 2px solid rgba(255,255,255,0.08); text-transform: uppercase; font-size: 0.72rem; }
.mapping-table td { padding: 0.5rem 0.85rem; border-bottom: 1px solid rgba(255,255,255,0.04); vertical-align: middle; }
.mapping-table tbody tr:hover { background: rgba(99, 102, 241, 0.06); }
.row-disabled { opacity: 0.45; background: rgba(0, 0, 0, 0.2); }
.col-center { text-align: center; }
.col-orig { font-weight: 600; color: #38bdf8; font-family: var(--font-mono); }
.tag-const { margin-left: 0.5rem; font-size: 0.68rem; background: rgba(239, 68, 68, 0.2); color: #f87171; padding: 0.15rem 0.4rem; border-radius: 4px; }
.badge-na { font-size: 0.72rem; color: #64748b; font-weight: 600; background: rgba(100, 116, 139, 0.15); padding: 0.2rem 0.45rem; border-radius: 4px; border: 1px solid rgba(100, 116, 139, 0.2); }
.badge-success { font-size: 0.72rem; color: #34d399; font-weight: 600; background: rgba(16, 185, 129, 0.15); padding: 0.25rem 0.55rem; border-radius: 4px; border: 1px solid rgba(16, 185, 129, 0.25); display: inline-block; }
.input-table-text { width: 100%; padding: 0.35rem 0.6rem; border-radius: 5px; border: 1px solid rgba(255,255,255,0.15); background: #1e293b; color: #f8fafc; font-size: 0.8rem; }
.select-table { width: 100%; padding: 0.35rem 0.5rem; border-radius: 5px; border: 1px solid rgba(255,255,255,0.15); background: #1e293b; color: #f8fafc; font-size: 0.8rem; }
.checkbox-custom { width: 16px; height: 16px; accent-color: #6366f1; cursor: pointer; }
</style>
