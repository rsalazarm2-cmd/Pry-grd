<script setup lang="ts">
/**
 * Componente Lateral de Lista de Espera / Parking Lot (Fase Canvas Pro).
 * Panel colapsable a la derecha para gestionar campos excluidos o en pausa.
 */
import { ref, computed } from 'vue'

export interface PausedFieldItem {
  name: string
  targetName?: string
  dataType?: string
  originTable?: string
  relevanceScore?: number
  rationale?: string
}

const props = defineProps<{
  show: boolean
  pausedFields: PausedFieldItem[]
}>()

const emit = defineEmits<{
  (e: 'toggle'): void
  (e: 'restoreField', fieldName: string): void
  (e: 'restoreAll'): void
  (e: 'dropToParking', fieldName: string): void
}>()

const searchQuery = ref('')

const filteredFields = computed(() => {
  if (!searchQuery.value.trim()) return props.pausedFields
  const q = searchQuery.value.toLowerCase()
  return props.pausedFields.filter(f => f.name.toLowerCase().includes(q) || (f.targetName && f.targetName.toLowerCase().includes(q)))
})

function handleDragOver(e: DragEvent) {
  e.preventDefault()
  if (e.dataTransfer) e.dataTransfer.dropEffect = 'move'
}

function handleDrop(e: DragEvent) {
  e.preventDefault()
  if (!e.dataTransfer) return
  try {
    const raw = e.dataTransfer.getData('text/plain')
    if (!raw) return
    const data = JSON.parse(raw)
    if (data.fieldName) {
      emit('dropToParking', data.fieldName)
    }
  } catch (err) {
    console.error('Error procesando drop en Lista de Espera:', err)
  }
}
</script>

<template>
  <div class="parking-drawer-wrapper" :class="{ 'is-open': show }">
    <!-- Toggle Tab Button -->
    <button class="drawer-toggle-btn" @click="emit('toggle')" title="Toggle Lista de Espera">
      <span class="toggle-icon">{{ show ? '❯' : '❮' }}</span>
      <span class="toggle-label">📥 Lista de Espera ({{ pausedFields.length }})</span>
    </button>

    <!-- Collapsible Drawer Container -->
    <div
      v-if="show"
      class="drawer-panel glass-card"
      @dragover="handleDragOver"
      @drop="handleDrop"
    >
      <div class="drawer-header">
        <div class="header-title-group">
          <h4>📥 Lista de Espera</h4>
          <span class="count-badge">{{ pausedFields.length }} en pausa</span>
        </div>
        <button v-if="pausedFields.length > 0" class="btn-restore-all" @click="emit('restoreAll')">
          🔄 Restaurar Todos
        </button>
      </div>

      <div class="drawer-search">
        <input
          v-model="searchQuery"
          type="text"
          placeholder="🔍 Buscar campo excluido..."
          class="search-input"
        />
      </div>

      <!-- Drop Zone Indicator -->
      <div class="drop-zone-hint">
        <span>Arrastra aquí un campo para pasarlo a espera</span>
      </div>

      <div class="drawer-body">
        <div v-for="field in filteredFields" :key="field.name" class="field-item-card" :title="field.rationale || 'Campo excluido de la vista'">
          <div class="field-info">
            <div class="name-row">
              <span class="field-name">{{ field.targetName || field.name }}</span>
              <span class="ai-score-badge">⚪ 20% Técnico</span>
            </div>
            <span v-if="field.dataType" class="field-type">{{ field.dataType }}</span>
          </div>
          <button
            class="btn-restore-single"
            title="Re-incluir en la Vista"
            @click="emit('restoreField', field.name)"
          >
            ➕ Incluir
          </button>
        </div>

        <div v-if="pausedFields.length === 0" class="empty-state">
          <span>✨ No hay campos en la lista de espera. Todos están activos en la vista.</span>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.parking-drawer-wrapper { position: absolute; right: 0; top: 0; bottom: 0; display: flex; z-index: 50; pointer-events: none; }
.drawer-toggle-btn { pointer-events: auto; background: #0f172a; border: 1px solid rgba(255,255,255,0.15); border-right: none; color: #38bdf8; font-weight: 700; font-size: 0.78rem; padding: 0.6rem 0.8rem; border-top-left-radius: 8px; border-bottom-left-radius: 8px; cursor: pointer; display: flex; align-items: center; gap: 0.4rem; height: fit-content; margin-top: 1rem; box-shadow: -4px 0 16px rgba(0,0,0,0.4); }
.drawer-panel { pointer-events: auto; width: 310px; background: #0b1329; border-left: 1px solid rgba(255,255,255,0.12); display: flex; flex-direction: column; gap: 0.75rem; padding: 1rem; height: 100%; box-shadow: -8px 0 24px rgba(0,0,0,0.6); }
.drawer-header { display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid rgba(255,255,255,0.08); pb: 0.5rem; }
.header-title-group { display: flex; align-items: center; gap: 0.5rem; }
.header-title-group h4 { margin: 0; font-size: 0.9rem; color: #f8fafc; font-weight: 700; }
.count-badge { background: rgba(245, 158, 11, 0.2); color: #fbbf24; font-size: 0.7rem; font-weight: 700; padding: 0.1rem 0.4rem; border-radius: 4px; }
.btn-restore-all { background: rgba(56, 189, 248, 0.15); border: 1px solid #38bdf8; color: #38bdf8; font-size: 0.7rem; font-weight: 700; padding: 0.2rem 0.5rem; border-radius: 4px; cursor: pointer; }
.search-input { width: 100%; background: #090d16; border: 1px solid rgba(255,255,255,0.1); border-radius: 6px; padding: 0.35rem 0.6rem; color: #f8fafc; font-size: 0.75rem; }
.drop-zone-hint { border: 1px dashed rgba(245, 158, 11, 0.4); background: rgba(245, 158, 11, 0.05); padding: 0.4rem; text-align: center; border-radius: 6px; color: #fbbf24; font-size: 0.7rem; font-weight: 600; }
.drawer-body { flex: 1; overflow-y: auto; display: flex; flex-direction: column; gap: 0.4rem; }
.field-item-card { display: flex; justify-content: space-between; align-items: center; background: #162032; border: 1px solid rgba(255,255,255,0.06); padding: 0.45rem 0.6rem; border-radius: 6px; }
.field-info { display: flex; flex-direction: column; gap: 0.1rem; }
.name-row { display: flex; align-items: center; gap: 0.35rem; }
.field-name { font-size: 0.78rem; font-family: monospace; font-weight: 600; color: #e2e8f0; }
.ai-score-badge { font-size: 0.6rem; color: #94a3b8; background: rgba(255,255,255,0.06); padding: 0.05rem 0.3rem; border-radius: 3px; font-weight: 600; }
.field-type { font-size: 0.65rem; color: #94a3b8; }
.btn-restore-single { background: linear-gradient(135deg, #10b981, #059669); color: #fff; border: none; font-size: 0.7rem; font-weight: 700; padding: 0.25rem 0.55rem; border-radius: 4px; cursor: pointer; }
.empty-state { padding: 1.5rem; text-align: center; color: #64748b; font-size: 0.75rem; font-style: italic; }
</style>
