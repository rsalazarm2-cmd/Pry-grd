<script setup lang="ts">
/**
 * Workspace de la Capa Plata (Silver).
 * Integra CU-05 (Dataset Cargos vs Abonos), CU-06 (Schema Canvas),
 * CU-07 (Linaje Origen ➔ Plata), CU-08 (Receta Inmutable) y CU-09/10 (Reglas No-Code).
 */
import { ref, onMounted } from 'vue'
import { useSilverRecords } from '@/composables/useSilverRecords'
import { useSilverSchemaBuilder } from '@/composables/useSilverSchemaBuilder'
import DataTable from '@/components/tables/DataTable.vue'
import SilverSchemaCanvas from '@/components/forms/SilverSchemaCanvas.vue'
import SilverLineageTable from '@/components/analytics/SilverLineageTable.vue'
import DateAuditStudio from '@/components/silver/DateAuditStudio.vue'
import ConditionalRuleBuilder from '@/components/forms/ConditionalRuleBuilder.vue'
import ForensicVectorStudio from '@/components/silver/ForensicVectorStudio.vue'

// ... existing setup ...


const activeTab = ref<'canvas' | 'records' | 'lineage' | 'rules' | 'forensic'>('forensic')
const { records, currentViewMode, isLoading: isLoadingRecords, error: recordsError, reload } = useSilverRecords()
const {
  rules, lineage, isRecipeSaved, isLoading: isSchemaLoading, error: schemaError,
  loadRules, loadLineage, toggleColumnInclude, updateColumnTarget, compileSchema,
} = useSilverSchemaBuilder()

onMounted(async () => {
  await loadRules()
  await loadLineage()
})

async function handleCompile() {
  const success = await compileSchema()
  if (success) {
    await reload(currentViewMode.value)
    activeTab.value = 'records'
  }
}
</script>

<template>
  <div class="workspace">
    <div class="workspace-header">
      <div>
        <h2 class="workspace-title">🥈 Capa Plata: Estandarización y Calidad</h2>
        <span v-if="isRecipeSaved" class="badge-saved">⚡ Receta .json Cargada en 1 ms</span>
      </div>

      <div class="workspace-tabs">
        <button class="tab-btn" :class="{ active: activeTab === 'forensic' }" @click="activeTab = 'forensic'">
          🛡️ Vectores Forenses (5D)
        </button>
        <button class="tab-btn" :class="{ active: activeTab === 'records' }" @click="activeTab = 'records'">
          📊 Dataset Plata
        </button>
        <button class="tab-btn" :class="{ active: activeTab === 'canvas' }" @click="activeTab = 'canvas'">
          🎨 Schema Canvas
        </button>
        <button class="tab-btn" :class="{ active: activeTab === 'rules' }" @click="activeTab = 'rules'">
          ⚡ Reglas No-Code
        </button>
        <button class="tab-btn" :class="{ active: activeTab === 'lineage' }" @click="activeTab = 'lineage'">
          🧬 Linaje Transparente
        </button>
      </div>
    </div>

    <div v-if="recordsError || schemaError" class="alert-error">
      ⚠️ {{ recordsError || schemaError }}
    </div>

    <!-- TAB 0: Motor Vectorial Forense (5D) -->
    <ForensicVectorStudio v-if="activeTab === 'forensic'" />

    <!-- TAB 1: Dataset Plata -->
    <div v-else-if="activeTab === 'records'" class="glass-card">
      <div class="table-header">
        <div class="table-title-group">
          <span class="table-label">Dataset Plata (silver.parquet)</span>
          <div class="view-mode-selector">
            <button class="mode-btn" :class="{ active: currentViewMode === 'ALL' }" @click="reload('ALL')">Todos</button>
            <button class="mode-btn mode-cargo" :class="{ active: currentViewMode === 'CARGOS' }" @click="reload('CARGOS')">📥 Solo Cargos</button>
            <button class="mode-btn mode-abono" :class="{ active: currentViewMode === 'ABONOS' }" @click="reload('ABONOS')">📤 Solo Abonos</button>
          </div>
        </div>
        <span v-if="records" class="table-count">{{ records.total_returned }} registros</span>
      </div>

      <div v-if="isLoadingRecords" class="loading-indicator">Cargando datos Plata...</div>
      <DataTable v-else-if="records && records.rows.length" :data="records" max-height="520px" />
      <div v-else class="empty-state">No hay registros para este filtro o capa Plata.</div>
    </div>

    <!-- TAB 2: Schema Canvas -->
    <SilverSchemaCanvas
      v-else-if="activeTab === 'canvas'"
      :rules="rules"
      :is-recipe-saved="isRecipeSaved"
      :is-processing="isSchemaLoading"
      @toggle-include="toggleColumnInclude"
      @update-target="(p) => updateColumnTarget(p.col, p.target)"
      @compile="handleCompile"
    />

    <!-- TAB 3: Reglas Condicionales & Motor de Fechas No-Code -->
    <div v-else-if="activeTab === 'rules'" class="space-y-6">
      <DateAuditStudio />
      <ConditionalRuleBuilder />
    </div>


    <!-- TAB 4: Linaje Transparente -->
    <SilverLineageTable
      v-else-if="activeTab === 'lineage'"
      :lineage="lineage"
      :is-loading="isSchemaLoading"
    />
  </div>
</template>

<style scoped>
.workspace { display: flex; flex-direction: column; gap: 1.25rem; padding: 1.5rem; }
.workspace-header { display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 1rem; }
.workspace-title { font-size: 1.4rem; font-weight: 700; color: var(--text-main); margin: 0; }
.badge-saved { font-size: 0.75rem; color: var(--accent-emerald); font-weight: 600; }
.workspace-tabs { display: flex; gap: 0.5rem; background: rgba(0,0,0,0.3); padding: 0.25rem; border-radius: 8px; }
.tab-btn { background: transparent; border: none; color: var(--text-muted); padding: 0.4rem 0.85rem; border-radius: 6px; font-weight: 600; cursor: pointer; font-size: 0.85rem; }
.tab-btn.active { background: var(--accent-amber); color: #000; }
.table-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem; flex-wrap: wrap; gap: 0.75rem; }
.table-title-group { display: flex; align-items: center; gap: 1rem; }
.table-label { font-size: 1rem; font-weight: 600; color: var(--text-main); }
.view-mode-selector { display: flex; gap: 0.25rem; background: rgba(255,255,255,0.05); padding: 0.2rem; border-radius: 6px; }
.mode-btn { background: transparent; border: none; color: var(--text-muted); padding: 0.25rem 0.6rem; border-radius: 4px; font-size: 0.75rem; cursor: pointer; font-weight: 600; }
.mode-btn.active { background: rgba(59, 130, 246, 0.3); color: #60a5fa; }
.mode-cargo.active { background: rgba(16, 185, 129, 0.3); color: #34d399; }
.mode-abono.active { background: rgba(239, 68, 68, 0.3); color: #f87171; }
.table-count { font-size: 0.85rem; color: var(--text-muted); }
.loading-indicator, .empty-state { padding: 2rem; text-align: center; color: var(--text-muted); font-style: italic; }
.alert-error { padding: 0.75rem; background: rgba(239, 68, 68, 0.1); border: 1px solid var(--accent-rose); border-radius: 6px; color: var(--accent-rose); }
</style>
