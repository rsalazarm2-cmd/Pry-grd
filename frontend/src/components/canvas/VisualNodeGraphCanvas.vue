<script setup lang="ts">
/**
 * Studio Blueprint Canvas (Capa Plata Pro).
 * Lienzo con resolución insensible a mayúsculas/minúsculas y soporte de llaves sintéticas (PK/FK).
 */
import { ref, computed, onMounted } from 'vue'
import { useProjectStore } from '@/stores/project_store'
import { apiGet } from '@/api/http_client'
import CanvasNodeCard, { type FieldItem } from './CanvasNodeCard.vue'
import CanvasParkingLotDrawer, { type PausedFieldItem } from './CanvasParkingLotDrawer.vue'
import CanvasToolbar from './CanvasToolbar.vue'
import CanvasSqlModal from './CanvasSqlModal.vue'

const store = useProjectStore()
const zoomLevel = ref(1.0)
const showDrawer = ref(false)
const showSqlModal = ref(false)

const targetNodes = ref<any[]>([])
const activeNodeId = ref<string | null>(null)

const allDatasetColumns = computed<FieldItem[]>(() => {
  if (store.profile?.columns && store.profile.columns.length > 0) {
    return store.profile.columns.map(c => {
      const orig = c.column_name
      const rule = store.rules.column_rules?.[orig] || store.rules.column_rules?.[orig.toLowerCase()]
      return {
        name: orig, targetName: rule?.new_column_name || orig, dataType: c.inferred_data_type || rule?.target_data_type || 'VARCHAR', included: rule?.include_in_silver !== false
      }
    })
  }
  const rules = store.rules.column_rules || {}
  return Object.entries(rules).map(([orig, r]) => ({
    name: orig, targetName: r.new_column_name || orig, dataType: r.target_data_type || 'VARCHAR', included: r.include_in_silver !== false
  }))
})

const activeUsedFields = computed(() => {
  const used = new Set<string>()
  targetNodes.value.forEach(node => (node.selectedFields || []).forEach((f: string) => used.add(f.toUpperCase())))
  return used
})

const pausedFieldsList = computed<PausedFieldItem[]>(() =>
  allDatasetColumns.value.filter(f => !activeUsedFields.value.has(f.name.toUpperCase())).map(f => ({ name: f.name, targetName: f.targetName, dataType: f.dataType }))
)

function getFieldsForNode(nodeId: string): FieldItem[] {
  const node = targetNodes.value.find(n => n.id === nodeId)
  if (!node || !node.selectedFields) return []
  return node.selectedFields.map((fieldName: string) => {
    const matched = allDatasetColumns.value.find(sf => sf.name.toUpperCase() === fieldName.toUpperCase())
    return matched ? { ...matched, name: fieldName } : { name: fieldName, targetName: fieldName, dataType: fieldName.includes('ID') ? 'BIGINT' : 'VARCHAR', included: true }
  })
}

function pauseField(fieldName: string) { targetNodes.value.forEach(n => { if (n.selectedFields) n.selectedFields = n.selectedFields.filter((f: string) => f.toUpperCase() !== fieldName.toUpperCase()) }) }
function restoreField(fieldName: string) { if (targetNodes.value.length > 0 && !targetNodes.value[0].selectedFields?.includes(fieldName)) targetNodes.value[0].selectedFields.push(fieldName) }
function restoreAllFields() { if (targetNodes.value.length > 0) targetNodes.value[0].selectedFields = allDatasetColumns.value.map(c => c.name) }
function updateAlias(fieldName: string, newAlias: string) { if (store.rules.column_rules?.[fieldName]) store.rules.column_rules[fieldName].new_column_name = newAlias }
function updateNodeTitle(nodeId: string, newTitle: string) { const n = targetNodes.value.find(t => t.id === nodeId); if (n) n.name = newTitle }
function updateJoinType(nodeId: string, joinType: 'LEFT' | 'INNER' | 'RIGHT' | 'FULL') { const n = targetNodes.value.find(t => t.id === nodeId); if (n) n.joinType = joinType }
function moveNode(id: string, x: number, y: number) { const n = targetNodes.value.find(t => t.id === id); if (n) { n.posX = x; n.posY = y } }
function removeNode(id: string) { targetNodes.value = targetNodes.value.filter(n => n.id !== id) }
function generateIdForNode(nodeId: string) { const n = targetNodes.value.find(t => t.id === nodeId); if (n) { if (!n.selectedFields) n.selectedFields = []; if (!n.selectedFields.includes('FOLIO_ASIENTO_ID')) n.selectedFields.unshift('FOLIO_ASIENTO_ID') } }
function addCustomView() { targetNodes.value.push({ id: `view_custom_${Date.now()}`, name: `🥇 VISTA_PERSONALIZADA_${targetNodes.value.length + 1}`, subtitle: 'Vista Relacional Definida por Auditor', joinType: 'INNER', posX: 140 + (targetNodes.value.length * 40), posY: 80 + (targetNodes.value.length * 40), selectedFields: ['FOLIO_ASIENTO_ID'] }) }

async function autoSuggestModel() {
  try {
    const res = await apiGet<any[]>('/silver/suggest-multitable-model')
    if (res && res.length > 0) {
      targetNodes.value = res.map((e, idx) => ({ id: e.entity_id, name: `🥇 ${e.entity_name}`, subtitle: e.description, joinType: idx === 0 ? 'LEFT' : 'INNER', posX: 120 + (idx * 360), posY: 80, selectedFields: e.selected_columns || [] }))
    }
  } catch (err) { console.error('Error auto-sugiriendo:', err) }
}


onMounted(async () => {
  if (!store.profile) await store.loadProfile()
  if (!store.rules || Object.keys(store.rules.column_rules || {}).length === 0) { await store.loadSuggestedMapping(false) }
})

const svgCables = computed(() => {
  if (targetNodes.value.length < 2) return []
  const cables: any[] = []
  const head = targetNodes.value[0]
  for (let i = 1; i < targetNodes.value.length; i++) {
    const child = targetNodes.value[i]
    const x1 = head.posX + 330, y1 = head.posY + 40, x2 = child.posX, y2 = child.posY + 40, dx = Math.abs(x2 - x1) / 2
    cables.push({ id: `${head.id}_${child.id}`, joinType: child.joinType || 'INNER', midX: (x1 + x2) / 2, midY: (y1 + y2) / 2, d: `M ${x1} ${y1} C ${x1 + dx} ${y1}, ${x2 - dx} ${y2}, ${x2} ${y2}` })
  }
  return cables
})

const generatedSqlCode = computed(() => {
  if (targetNodes.value.length === 0) return "-- No hay vistas relacionales en el canvas. Usa '+ Agregar Vista' o '✨ Auto-Sugerir (IA)'."
  return targetNodes.value.map(tn => {
    const nodeCols = getFieldsForNode(tn.id).map(f => `  "${f.name}" AS "${f.targetName || f.name}"`).join(',\n')
    return `-- Vista Relacional: ${tn.name}\nCREATE OR REPLACE VIEW view_${tn.name.replace(/[^a-zA-Z0-9_]/g, '_').toLowerCase()} AS\nSELECT\n${nodeCols}\nFROM read_parquet('silver.parquet');`
  }).join('\n\n')
})
</script>

<template>
  <div class="visual-studio-container">
    <CanvasToolbar
      :targetNodesCount="targetNodes.length"
      :zoomLevel="zoomLevel"
      @updateZoom="d => zoomLevel = Math.max(0.6, Math.min(1.5, zoomLevel + d))"
      @resetZoom="zoomLevel = 1.0"
      @openSqlModal="showSqlModal = true"
      @autoSuggest="autoSuggestModel"
      @addCustomView="addCustomView"
    />

    <div class="canvas-viewport" @dragover.prevent>
      <div class="node-graph-workspace" :style="{ transform: `scale(${zoomLevel})`, transformOrigin: '0 0' }">
        <svg class="svg-connections-layer">
          <defs>
            <linearGradient id="cableGradient" x1="0%" y1="0%" x2="100%" y2="0%">
              <stop offset="0%" stop-color="#6366f1" />
              <stop offset="100%" stop-color="#38bdf8" />
            </linearGradient>
          </defs>
          <g v-for="cable in svgCables" :key="cable.id">
            <path :d="cable.d" stroke="url(#cableGradient)" stroke-width="3" fill="none" class="cable-path" />
            <text :x="cable.midX" :y="cable.midY - 8" fill="#38bdf8" font-size="10" font-weight="bold" text-anchor="middle">
              🔗 {{ cable.joinType }} JOIN (PK/FK)
            </text>
          </g>
        </svg>

        <!-- Nodos de Vista Relacionales Destino (Inicialmente 0 en Rejilla) -->
        <CanvasNodeCard
          v-for="targetNode in targetNodes"
          :key="targetNode.id"
          :id="targetNode.id"
          :title="targetNode.name"
          :subtitle="targetNode.subtitle"
          nodeType="TARGET"
          :joinType="targetNode.joinType || 'LEFT'"
          :fields="getFieldsForNode(targetNode.id)"
          :posX="targetNode.posX"
          :posY="targetNode.posY"
          :selected="activeNodeId === targetNode.id"
          @move="moveNode"
          @select="id => activeNodeId = id"
          @removeNode="removeNode"
          @pauseField="pauseField"
          @updateAlias="updateAlias"
          @updateJoinType="updateJoinType"
          @generateId="generateIdForNode"
          @updateNodeTitle="updateNodeTitle"
        />

        <div v-if="targetNodes.length === 0" class="canvas-empty-state">
          <div class="empty-hint-card glass-card">
            <h3>🎨 Lienzo de Diseño de Esquema Vacío</h3>
            <p>Usa <strong>+ Agregar Vista</strong> para crear vistas manuales o haz clic en <strong>✨ Auto-Sugerir (IA)</strong> para estructurar el modelo relacional con NLP Forense.</p>
          </div>
        </div>
      </div>

      <!-- Drawer Lateral de Lista de Espera (Catálogo Completo) -->
      <CanvasParkingLotDrawer
        :show="showDrawer"
        :pausedFields="pausedFieldsList"
        @toggle="showDrawer = !showDrawer"
        @restoreField="restoreField"
        @restoreAll="restoreAllFields"
        @dropToParking="pauseField"
      />
    </div>

    <!-- SQL Preview Modal -->
    <CanvasSqlModal
      :show="showSqlModal"
      :sqlCode="generatedSqlCode"
      @close="showSqlModal = false"
    />
  </div>
</template>

<style scoped>
.visual-studio-container { display: flex; flex-direction: column; height: 600px; background: #090d16; border-radius: 12px; border: 1px solid rgba(255,255,255,0.1); overflow: hidden; position: relative; }
.canvas-viewport { flex: 1; position: relative; overflow: hidden; display: flex; }
.node-graph-workspace { flex: 1; position: relative; height: 100%; width: 100%; overflow: auto; background-color: #090d16; background-image: radial-gradient(rgba(255, 255, 255, 0.12) 1px, transparent 1px); background-size: 24px 24px; }
.svg-connections-layer { position: absolute; inset: 0; width: 100%; height: 100%; pointer-events: none; z-index: 1; }
.cable-path { filter: drop-shadow(0 0 6px rgba(99, 102, 241, 0.6)); }
.canvas-empty-state { position: absolute; inset: 0; display: flex; align-items: center; justify-content: center; pointer-events: none; }
.empty-hint-card { background: rgba(15, 23, 42, 0.85); border: 1px dashed rgba(56, 189, 248, 0.4); padding: 2rem; border-radius: 12px; text-align: center; max-width: 460px; pointer-events: auto; }
.empty-hint-card h3 { color: #38bdf8; margin: 0 0 0.5rem 0; font-size: 1.05rem; font-weight: 800; }
.empty-hint-card p { color: #94a3b8; font-size: 0.8rem; line-height: 1.4; margin: 0; }
</style>
