<script setup lang="ts">
/**
 * Panel de Diagnóstico Exploratorio Básico (EDA - Capa Bronce Data Lake).
 * Enfocado en calidad física de la data sucia: Nulos %, Medias (mean), Min/Max y Salud Estructural.
 */
import { computed } from 'vue'
import type { DatasetProfileDTO } from '@/types/profiling'
import KpiCard from '@/components/layout/KpiCard.vue'
import ColumnHealthTable from '@/components/diagnostics/ColumnHealthTable.vue'

const props = defineProps<{
  profile: DatasetProfileDTO
}>()

const numericColumns = computed(() => {
  return (props.profile.columns || []).filter(c => c.mean_value !== null && c.mean_value !== undefined)
})

function formatCurrency(amount: number | string | null | undefined): string {
  if (amount === null || amount === undefined) return '-'
  const num = typeof amount === 'string' ? parseFloat(amount) : amount
  if (isNaN(num)) return '-'
  if (Math.abs(num) >= 1_000_000_000) return `$${(num / 1_000_000_000).toFixed(2)}B`
  if (Math.abs(num) >= 1_000_000) return `$${(num / 1_000_000).toFixed(2)}M`
  return `$${num.toLocaleString('es-CO')}`
}

function formatBytes(bytes: number): string {
  if (!bytes || bytes <= 0) return '0 B'
  if (bytes < 1024) return `${bytes} B`
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`
}

function getHealthStatus(score: number): { label: string; color: string } {
  if (score >= 85) return { label: 'Excelente / Óptimo', color: '#10b981' }
  if (score >= 60) return { label: 'Riesgo Moderado (Requiere Limpieza)', color: '#f59e0b' }
  return { label: 'Alto Riesgo (Múltiples Anomalías)', color: '#ef4444' }
}
</script>

<template>
  <div class="profiling-panel glass-card">
    <!-- Header -->
    <div class="header-row">
      <div>
        <h3 class="panel-title">📊 Diagnóstico Exploratorio de Datos (EDA Crudo)</h3>
        <p class="panel-subtitle">Análisis Físico de Calidad, Nulos y Estadísticas Descriptivas de Capa Bronce</p>
      </div>
      <div v-if="profile.data_health_score !== undefined" class="health-badge-container">
        <span class="health-label">🎯 Salud Estructural:</span>
        <span class="health-badge" :style="{ borderColor: getHealthStatus(profile.data_health_score).color, color: getHealthStatus(profile.data_health_score).color }">
          {{ profile.data_health_score }}% — {{ getHealthStatus(profile.data_health_score).label }}
        </span>
      </div>
    </div>

    <!-- KPIs de Ingestión y Estructura -->
    <div class="kpi-grid">
      <KpiCard :value="profile.total_rows" label="Filas Totales" accent-color="#38bdf8" />
      <KpiCard :value="profile.total_columns" label="Columnas Totales" accent-color="#818cf8" />
      <KpiCard :value="profile.perfect_columns_count" label="Columnas Integras" accent-color="#34d399" />
      <KpiCard :value="profile.null_columns_count" label="Columnas con Nulos" accent-color="#fbbf24" />
      <KpiCard :value="profile.constant_columns_count" label="Columnas Constantes" accent-color="#f87171" />
      <KpiCard :value="formatBytes(profile.file_size_bytes)" label="Tamaño en Disco" accent-color="#c084fc" />
    </div>

    <!-- Estadísticas Descriptivas en Columnas con Montos / Numéricas -->
    <div v-if="numericColumns.length > 0" class="eda-section">
      <div class="section-header">
        <h4 class="section-title">📐 Estadísticas Descriptivas Crudas (Montos e Importes)</h4>
        <span class="section-badge">Medias & Valores Mín/Máx</span>
      </div>
      <div class="table-wrapper">
        <table class="eda-table">
          <thead>
            <tr>
              <th>Columna Origen</th>
              <th>Tipo Inferido</th>
              <th>Media (Mean)</th>
              <th>Mínimo (Min)</th>
              <th>Máximo (Max)</th>
              <th>Suma Total Cruda</th>
              <th>Nulos (%)</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="col in numericColumns" :key="col.column_name">
              <td class="col-name">{{ col.column_name }}</td>
              <td><span class="tag-type">{{ col.data_type }}</span></td>
              <td class="col-num font-mono text-cyan">{{ formatCurrency(col.mean_value) }}</td>
              <td class="col-num font-mono">{{ formatCurrency(col.min_value) }}</td>
              <td class="col-num font-mono">{{ formatCurrency(col.max_value) }}</td>
              <td class="col-num font-mono text-emerald">{{ formatCurrency(col.sum_value) }}</td>
              <td class="col-center">
                <span class="null-badge" :class="{ 'has-nulls': col.null_count > 0 }">
                  {{ col.null_percentage }}% ({{ col.null_count }})
                </span>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Tabla de Inspección por Columna -->
    <ColumnHealthTable v-if="profile.columns && profile.columns.length > 0" :columns="profile.columns" />
  </div>
</template>

<style scoped>
.profiling-panel { padding: 1.5rem; display: flex; flex-direction: column; gap: 1.5rem; }
.header-row { display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 1rem; }
.panel-title { font-size: 1.25rem; font-weight: 700; color: #f8fafc; margin: 0; }
.panel-subtitle { font-size: 0.82rem; color: #94a3b8; margin: 0.25rem 0 0 0; }
.health-badge-container { display: flex; align-items: center; gap: 0.5rem; font-size: 0.85rem; }
.health-label { color: #94a3b8; font-weight: 600; }
.health-badge { padding: 0.35rem 0.75rem; border-radius: 8px; border: 1.5px solid; background: rgba(15, 23, 42, 0.6); font-weight: 700; font-family: var(--font-mono); }

.kpi-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(160px, 1fr)); gap: 0.85rem; }

.eda-section { background: rgba(15, 23, 42, 0.5); padding: 1.25rem; border-radius: 12px; border: 1px solid rgba(255, 255, 255, 0.08); }
.section-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem; }
.section-title { font-size: 1rem; font-weight: 700; color: #f8fafc; margin: 0; }
.section-badge { font-size: 0.72rem; background: rgba(56, 189, 248, 0.15); color: #38bdf8; padding: 0.2rem 0.6rem; border-radius: 6px; border: 1px solid rgba(56, 189, 248, 0.3); font-weight: 600; }

.table-wrapper { overflow-x: auto; border-radius: 8px; border: 1px solid rgba(255, 255, 255, 0.08); }
.eda-table { width: 100%; border-collapse: collapse; font-size: 0.82rem; text-align: left; }
.eda-table th { background: #1e293b; color: #94a3b8; font-weight: 700; padding: 0.7rem 0.85rem; border-bottom: 2px solid rgba(255,255,255,0.08); font-size: 0.75rem; text-transform: uppercase; }
.eda-table td { padding: 0.6rem 0.85rem; border-bottom: 1px solid rgba(255,255,255,0.04); }
.col-name { font-weight: 700; color: #38bdf8; font-family: var(--font-mono); }
.tag-type { font-size: 0.7rem; background: rgba(129, 140, 248, 0.15); color: #818cf8; padding: 0.15rem 0.45rem; border-radius: 4px; font-weight: 600; }
.col-num { font-family: var(--font-mono); font-weight: 600; }
.text-cyan { color: #38bdf8; }
.text-emerald { color: #34d399; }
.col-center { text-align: center; }
.null-badge { font-size: 0.75rem; padding: 0.2rem 0.5rem; border-radius: 5px; background: rgba(52, 211, 153, 0.1); color: #34d399; font-weight: 600; }
.null-badge.has-nulls { background: rgba(251, 191, 36, 0.15); color: #fbbf24; }
</style>
