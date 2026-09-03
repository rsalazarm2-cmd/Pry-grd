<script setup lang="ts">
/**
 * Workspace de la Capa Bronce (Data Lake).
 * Muestra: Profiling → Config Mapeo → Pipeline Silver → Raw Data.
 * Redirección automática a Plata tras procesamiento e indicador de estado.
 */
import { ref, onMounted } from 'vue'
import { useProjectStore } from '@/stores/project_store'
import { useUiStore } from '@/stores/ui_store'
import { useBronzeProfile } from '@/composables/useBronzeProfile'
import { useBronzeRecords } from '@/composables/useBronzeRecords'
import { useSilverTransform } from '@/composables/useSilverTransform'

import ProfilingPanel from '@/components/diagnostics/ProfilingPanel.vue'
import DataTable from '@/components/tables/DataTable.vue'
import ColumnMappingTable from '@/components/forms/ColumnMappingTable.vue'
import GlobalCleaningControls from '@/components/forms/GlobalCleaningControls.vue'
import UploadDatasetModal from '@/components/modals/UploadDatasetModal.vue'

const store = useProjectStore()
const ui = useUiStore()
const { profile, isLoading: profileLoading } = useBronzeProfile()
const { records, isLoading: recordsLoading, error: recordsError } = useBronzeRecords()
const { result, isProcessing, error: transformError, execute } = useSilverTransform()

const showConfig = ref(false)
const showUploadModal = ref(false)

onMounted(() => {
  store.loadConfigOptions()
})

function toggleConfig(): void {
  showConfig.value = !showConfig.value
  if (showConfig.value) {
    store.loadSuggestedMapping()
  }
}

async function handleProcess(): Promise<void> {
  await execute(store.rules)
  if (result.value && result.value.status === 'success') {
    store.setSilverStatus(true, result.value.silver_row_count)
    setTimeout(() => {
      ui.setActiveTab('silver')
    }, 600)
  }
}

function goToSilver(): void {
  ui.setActiveTab('silver')
}
</script>

<template>
  <div class="workspace">
    <!-- Header -->
    <div class="workspace-header">
      <div>
        <h2 class="workspace-title">Capa Bronce: Data Lake</h2>
        <p class="workspace-subtitle">Ingestión cruda y diagnóstico físico exploratorio</p>
      </div>
      <div class="header-buttons">
        <button class="btn-upload" @click="showUploadModal = true">
          📤 Cargar Nuevo CSV / Parquet
        </button>
        <button class="btn-primary btn-config" @click="toggleConfig">
          {{ showConfig ? '🔽 Ocultar Configuración' : '⚙️ Configurar Limpieza y Tipado' }}
        </button>
      </div>
    </div>

    <!-- Banner Informativo: Si la Capa Plata ya existe -->
    <div v-if="store.hasSilverData" class="alert-silver-ready glass-card">
      <div class="alert-silver-content">
        <span class="alert-silver-icon">🟢</span>
        <div>
          <strong>¡La Capa Plata ya fue procesada!</strong>
          <span class="alert-silver-desc"> Hay {{ store.silverRowCount.toLocaleString('es-CO') }} asientos estandarizados y limpios listos para auditoría.</span>
        </div>
      </div>
      <button class="btn-silver-link" @click="goToSilver">Ir a Capa Plata ➔</button>
    </div>

    <!-- Error de transformación -->
    <div v-if="transformError" class="alert-error">❌ Error: {{ transformError }}</div>

    <!-- Profiling -->
    <ProfilingPanel v-if="profile" :profile="profile" />
    <div v-else-if="profileLoading" class="loading-indicator">Cargando perfil estadístico...</div>

    <!-- Config de Limpieza (toggle) -->
    <div v-if="showConfig" class="glass-card config-panel">
      <div v-if="store.isLoadingSuggestions" class="loading-indicator">
        🤖 La IA está generando sugerencias semánticas...
      </div>
      <template v-else>
        <GlobalCleaningControls />
        <ColumnMappingTable />
        <div class="config-actions">
          <button class="btn-primary btn-execute" :disabled="isProcessing" @click="handleProcess">
            {{ isProcessing ? '⏳ Procesando e Ingestionando...' : '🚀 Ejecutar Limpieza ➔ Ir a Capa Plata' }}
          </button>
        </div>
      </template>
    </div>

    <!-- Tabla de Raw Data -->
    <div class="glass-card">
      <div class="table-header">
        <span class="table-label">Datos sin procesar (Raw Data)</span>
        <span v-if="records" class="table-count">Mostrando {{ records.total_returned }} asientos</span>
      </div>
      <div v-if="recordsLoading" class="loading-indicator">Cargando Dataset de DuckDB...</div>
      <div v-else-if="recordsError" class="alert-error">Error del Backend: {{ recordsError }}</div>
      <DataTable v-else-if="records" :data="records" max-height="400px" />
    </div>

    <!-- Modal de Carga de Datasets -->
    <UploadDatasetModal v-if="showUploadModal" @close="showUploadModal = false" />
  </div>
</template>

<style scoped>
.workspace { display: flex; flex-direction: column; gap: 1.25rem; padding: 1.5rem; }
.workspace-header { display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 1rem; }
.workspace-title { font-size: 1.4rem; font-weight: 700; color: #f8fafc; margin: 0; }
.workspace-subtitle { font-size: 0.8rem; color: #94a3b8; margin: 0.2rem 0 0 0; }

.header-buttons { display: flex; align-items: center; gap: 0.75rem; }
.btn-upload { background: rgba(56, 189, 248, 0.15); border: 1px solid #38bdf8; color: #38bdf8; font-size: 0.85rem; padding: 0.5rem 1rem; border-radius: 8px; font-weight: 700; cursor: pointer; transition: all 0.2s ease; }
.btn-upload:hover { background: #38bdf8; color: #0f172a; }

.btn-config { background: linear-gradient(135deg, #a855f7, #6366f1); font-size: 0.85rem; padding: 0.5rem 1.25rem; border-radius: 8px; font-weight: 600; border: none; color: white; cursor: pointer; }

.alert-silver-ready { display: flex; justify-content: space-between; align-items: center; padding: 0.85rem 1.25rem; background: rgba(16, 185, 129, 0.08); border: 1px solid rgba(16, 185, 129, 0.3); border-radius: 10px; }
.alert-silver-content { display: flex; align-items: center; gap: 0.75rem; color: #f8fafc; font-size: 0.88rem; }
.alert-silver-icon { font-size: 1.2rem; }
.alert-silver-desc { color: #94a3b8; }
.btn-silver-link { background: #10b981; color: #0f172a; font-weight: 700; padding: 0.4rem 1rem; border-radius: 6px; border: none; cursor: pointer; transition: all 0.2s ease; }
.btn-silver-link:hover { background: #34d399; transform: translateX(2px); }

.config-panel { padding: 1.5rem; }
.config-actions { display: flex; justify-content: flex-end; margin-top: 1rem; }
.btn-execute { background: linear-gradient(135deg, #10b981, #059669); font-size: 1rem; padding: 0.65rem 1.5rem; font-weight: 700; border-radius: 8px; border: none; color: white; cursor: pointer; }
.table-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem; }
.table-label { font-size: 0.95rem; font-weight: 600; color: #f8fafc; }
.table-count { font-size: 0.82rem; color: #94a3b8; }
.loading-indicator { display: flex; justify-content: center; align-items: center; min-height: 180px; color: #38bdf8; font-weight: 600; }
.alert-error { padding: 1rem; background: rgba(239, 68, 68, 0.1); border: 1px solid #f87171; border-radius: 8px; color: #f87171; font-weight: 600; }
</style>
