<script setup lang="ts">
/**
 * Componente de Tarjeta de Nodo Arrastrable para el Canvas Visual Pro.
 * Soporta edición inline de título de vista, selector de Join Type y edición de alias.
 */
import { ref } from 'vue'

export interface FieldItem {
  name: string
  targetName?: string
  dataType?: string
  isConstant?: boolean
  included?: boolean
}

const props = defineProps<{
  id: string
  title: string
  subtitle?: string
  nodeType: 'SOURCE' | 'TARGET' | 'TRANSFORM'
  joinType?: 'LEFT' | 'INNER' | 'RIGHT' | 'FULL'
  fields: FieldItem[]
  posX: number
  posY: number
  selected?: boolean
}>()

const emit = defineEmits<{
  (e: 'move', id: string, x: number, y: number): void
  (e: 'select', id: string): void
  (e: 'removeNode', id: string): void
  (e: 'pauseField', fieldName: string): void
  (e: 'updateAlias', fieldName: string, newAlias: string): void
  (e: 'updateJoinType', id: string, joinType: 'LEFT' | 'INNER' | 'RIGHT' | 'FULL'): void
  (e: 'generateId', id: string): void
  (e: 'updateNodeTitle', id: string, newTitle: string): void
}>()

const editingField = ref<string | null>(null)
const editingAliasValue = ref('')
const isEditingTitle = ref(false)
const editingTitleValue = ref('')

let isDraggingNode = false
let startX = 0, startY = 0, initialNodeX = 0, initialNodeY = 0

function startDragNode(event: MouseEvent) {
  isDraggingNode = true; startX = event.clientX; startY = event.clientY
  initialNodeX = props.posX; initialNodeY = props.posY
  emit('select', props.id)
  window.addEventListener('mousemove', onDragNode)
  window.addEventListener('mouseup', stopDragNode)
}

function onDragNode(event: MouseEvent) {
  if (!isDraggingNode) return
  emit('move', props.id, initialNodeX + (event.clientX - startX), initialNodeY + (event.clientY - startY))
}

function stopDragNode() {
  isDraggingNode = false
  window.removeEventListener('mousemove', onDragNode)
  window.removeEventListener('mouseup', stopDragNode)
}

function startEditTitle() {
  if (props.nodeType === 'SOURCE') return
  isEditingTitle.value = true
  editingTitleValue.value = props.title.replace(/^🥇\s*/, '')
}

function saveTitle() {
  if (editingTitleValue.value.trim()) {
    emit('updateNodeTitle', props.id, `🥇 ${editingTitleValue.value.trim().toUpperCase()}`)
  }
  isEditingTitle.value = false
}

function startEditAlias(field: FieldItem) {
  editingField.value = field.name
  editingAliasValue.value = field.targetName || field.name
}

function saveAlias(fieldName: string) {
  if (editingAliasValue.value.trim()) {
    emit('updateAlias', fieldName, editingAliasValue.value.trim().toUpperCase())
  }
  editingField.value = null
}
</script>

<template>
  <div
    class="node-card"
    :class="[nodeType.toLowerCase(), { 'is-selected': selected }]"
    :style="{ left: `${posX}px`, top: `${posY}px` }"
    @mousedown="emit('select', props.id)"
    @dragover.prevent
  >
    <div class="node-header" @mousedown.stop="startDragNode">
      <div class="header-info">
        <span class="node-icon">{{ nodeType === 'SOURCE' ? '📦' : '🗄️' }}</span>
        <div>
          <div class="title-row">
            <input
              v-if="isEditingTitle"
              v-model="editingTitleValue"
              type="text"
              class="inline-title-input"
              @blur="saveTitle"
              @keyup.enter="saveTitle"
              @mousedown.stop
            />
            <h4 v-else class="node-title" title="Doble clic para renombrar vista" @dblclick.stop="startEditTitle">
              {{ title }}
            </h4>
            <button v-if="nodeType === 'TARGET' && !isEditingTitle" class="btn-edit-alias" @click.stop="startEditTitle">✏️</button>
            <button v-if="nodeType === 'TARGET'" class="btn-gen-id" title="Inyectar Llave de Unión" @click.stop="emit('generateId', props.id)">🔑 + ID</button>
            <select
              v-if="nodeType === 'TARGET'"
              :value="joinType || 'LEFT'"
              class="join-type-select"
              @change="e => emit('updateJoinType', props.id, (e.target as HTMLSelectElement).value as any)"
              @mousedown.stop
            >
              <option value="LEFT">LEFT JOIN</option>
              <option value="INNER">INNER JOIN</option>
              <option value="RIGHT">RIGHT JOIN</option>
              <option value="FULL">FULL JOIN</option>
            </select>
          </div>
          <span v-if="subtitle" class="node-subtitle">{{ subtitle }}</span>
        </div>
      </div>
      <button v-if="nodeType === 'TARGET'" class="btn-node-remove" @click.stop="emit('removeNode', props.id)">✕</button>
    </div>

    <div class="node-body">
      <div v-for="field in fields" :key="field.name" class="field-row" draggable="true">
        <span v-if="nodeType === 'TARGET'" class="port port-left" />
        <div class="field-details">
          <span class="drag-handle">::</span>
          <span v-if="field.name.includes('ID')" class="tag-pk">🔑 ID</span>

          <div class="alias-wrap">
            <input
              v-if="editingField === field.name"
              v-model="editingAliasValue"
              type="text"
              class="inline-alias-input"
              @blur="saveAlias(field.name)"
              @keyup.enter="saveAlias(field.name)"
            />
            <span v-else class="field-name" @dblclick="startEditAlias(field)">
              {{ field.targetName || field.name }}
            </span>
            <button class="btn-edit-alias" title="Renombrar alias" @click.stop="startEditAlias(field)">✏️</button>
          </div>

          <span v-if="field.dataType" class="field-type">{{ field.dataType }}</span>
          <button class="btn-pause-field" title="Enviar a Lista de Espera" @click.stop="emit('pauseField', field.name)">📥</button>
        </div>
        <span v-if="nodeType === 'SOURCE'" class="port port-right" />
      </div>
    </div>
  </div>
</template>

<style scoped>
.node-card { position: absolute; width: 340px; background: #0f172a; border-radius: 10px; border: 1px solid rgba(255,255,255,0.12); box-shadow: 0 12px 32px rgba(0,0,0,0.5); user-select: none; z-index: 10; }
.node-card.is-selected { border-color: #6366f1; box-shadow: 0 0 20px rgba(99, 102, 241, 0.4); }
.node-header { padding: 0.7rem 0.9rem; background: #1e293b; border-top-left-radius: 9px; border-top-right-radius: 9px; cursor: grab; display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid rgba(255,255,255,0.08); }
.header-info { display: flex; align-items: center; gap: 0.5rem; }
.title-row { display: flex; align-items: center; gap: 0.3rem; }
.node-title { margin: 0; font-size: 0.85rem; font-weight: 700; color: #f8fafc; cursor: pointer; }
.inline-title-input { background: #090d16; border: 1px solid #38bdf8; color: #38bdf8; font-size: 0.8rem; font-weight: 800; padding: 0.1rem 0.3rem; border-radius: 4px; width: 140px; }
.btn-gen-id { background: rgba(234, 179, 8, 0.2); border: 1px solid #eab308; color: #eab308; font-size: 0.65rem; font-weight: 800; border-radius: 4px; padding: 0.05rem 0.3rem; cursor: pointer; }
.join-type-select { background: rgba(56, 189, 248, 0.15); border: 1px solid #38bdf8; color: #38bdf8; font-size: 0.65rem; font-weight: 800; border-radius: 4px; padding: 0.05rem 0.25rem; cursor: pointer; }
.node-subtitle { font-size: 0.7rem; color: #94a3b8; }
.btn-node-remove { background: transparent; border: none; color: #f87171; cursor: pointer; font-weight: 700; }
.node-body { max-height: 340px; overflow-y: auto; padding: 0.3rem 0; }
.field-row { position: relative; display: flex; align-items: center; padding: 0.4rem 0.65rem; border-bottom: 1px solid rgba(255,255,255,0.03); font-size: 0.78rem; cursor: grab; }
.field-details { display: flex; align-items: center; gap: 0.35rem; width: 100%; justify-content: space-between; }
.drag-handle { color: #64748b; font-weight: 900; font-size: 0.7rem; }
.alias-wrap { display: flex; align-items: center; gap: 0.3rem; flex: 1; overflow: hidden; }
.field-name { color: #e2e8f0; font-weight: 600; font-family: monospace; text-overflow: ellipsis; overflow: hidden; white-space: nowrap; cursor: pointer; }
.inline-alias-input { background: #090d16; border: 1px solid #38bdf8; color: #f8fafc; font-family: monospace; font-size: 0.75rem; font-weight: 700; padding: 0.1rem 0.3rem; border-radius: 4px; width: 110px; }
.btn-edit-alias { background: transparent; border: none; font-size: 0.65rem; cursor: pointer; opacity: 0.5; }
.btn-edit-alias:hover { opacity: 1; }
.field-type { font-size: 0.65rem; color: #38bdf8; background: rgba(56, 189, 248, 0.12); padding: 0.1rem 0.35rem; border-radius: 4px; }
.btn-pause-field { background: rgba(245, 158, 11, 0.15); border: 1px solid rgba(245, 158, 11, 0.4); color: #fbbf24; font-size: 0.65rem; padding: 0.1rem 0.3rem; border-radius: 4px; cursor: pointer; }
.btn-pause-field:hover { background: rgba(245, 158, 11, 0.3); }
.tag-pk { font-size: 0.65rem; background: rgba(234, 179, 8, 0.2); color: #eab308; padding: 0.1rem 0.35rem; border-radius: 4px; font-weight: 700; }
.port { position: absolute; width: 10px; height: 10px; background: #6366f1; border-radius: 50%; border: 2px solid #0f172a; top: 50%; transform: translateY(-50%); }
.port-left { left: -6px; } .port-right { right: -6px; }
</style>
