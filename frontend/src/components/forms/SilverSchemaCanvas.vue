<script setup lang="ts">
/**
 * CU-06: Schema Blueprint Canvas Visual (Estudio de Modelado por Nodos e Hilos SVG).
 * Permite cambiar entre el Studio Canvas Interactivo por Nodos (Draw.io Style) y la Vista Lista.
 */
import { ref, computed } from 'vue'
import type { BronzeToSilverRulesDTO } from '@/types/bronze'
import VisualNodeGraphCanvas from '@/components/canvas/VisualNodeGraphCanvas.vue'

const props = defineProps<{
  rules: BronzeToSilverRulesDTO | null
  isRecipeSaved: boolean
  isProcessing: boolean
}>()

const emit = defineEmits<{
  (e: 'update-target', payload: { col: string; target: string }): void
  (e: 'toggle-include', col: string): void
  (e: 'compile'): void
}>()

const canvasMode = ref<'STUDIO_GRAPH' | 'LIST'>('STUDIO_GRAPH')
const searchTerm = ref('')
const filterIncludedOnly = ref(false)

const columnEntries = computed(() => {
  if (!props.rules?.column_rules) return []
  return Object.entries(props.rules.column_rules).filter(([src, rule]) => {
    const matchesSearch = src.toLowerCase().includes(searchTerm.value.toLowerCase()) ||
      (rule.new_column_name || src).toLowerCase().includes(searchTerm.value.toLowerCase())
    const matchesFilter = filterIncludedOnly.value ? rule.include_in_silver : true
    return matchesSearch && matchesFilter
  })
})

const stats = computed(() => {
  if (!props.rules?.column_rules) return { total: 0, included: 0 }
  const entries = Object.values(props.rules.column_rules)
  const included = entries.filter((r) => r.include_in_silver).length
  return { total: entries.length, included }
})
</script>

<template>
  <div class="schema-canvas glass-card">
    <!-- Header & Canvas Actions -->
    <div class="canvas-header">
      <div class="header-info">
        <h3 class="canvas-title">🎨 Schema Blueprint Canvas (Capa Plata)</h3>
        <span v-if="isRecipeSaved" class="badge-recipe">⚡ Receta Inmutable (.json)</span>
      </div>

      <div class="view-mode-selector">
        <button
          class="btn-mode"
          :class="{ 'mode-active': canvasMode === 'STUDIO_GRAPH' }"
          @click="canvasMode = 'STUDIO_GRAPH'"
        >
          🎨 Node Studio Canvas (Draw.io)
        </button>
        <button
          class="btn-mode"
          :class="{ 'mode-active': canvasMode === 'LIST' }"
          @click="canvasMode = 'LIST'"
        >
          📋 Lista de Reglas
        </button>
      </div>

      <div class="canvas-stats">
        <span class="stat-pill">📦 Bronce: <strong>{{ stats.total }} cols</strong></span>
        <span class="stat-arrow">➔</span>
        <span class="stat-pill stat-active">🥈 Plata: <strong>{{ stats.included }} cols</strong></span>
      </div>

      <button
        class="btn-primary"
        :disabled="isProcessing || !rules"
        @click="emit('compile')"
      >
        {{ isProcessing ? 'Compilando a Capa ORO...' : '🏆 Compilar y Enviar a Capa ORO' }}
      </button>
    </div>

    <!-- Empty State -->
    <div v-if="!rules" class="canvas-empty">
      Cargando o generando reglas de esquema para la Capa Plata...
    </div>

    <!-- MODO 1: Studio Canvas Visual por Nodos (Draw.io / ERD Studio Style) -->
    <VisualNodeGraphCanvas v-else-if="canvasMode === 'STUDIO_GRAPH'" />

    <!-- MODO 2: Vista Lista Tradicional -->
    <div v-else class="list-view-container">
      <div class="canvas-toolbar">
        <input v-model="searchTerm" type="text" placeholder="🔍 Buscar columna..." class="search-input">
        <label class="toggle-label">
          <input v-model="filterIncludedOnly" type="checkbox"> Solo columnas activas para Plata
        </label>
      </div>

      <div class="nodes-viewport">
        <div class="nodes-grid">
          <div
            v-for="([srcCol, rule]) in columnEntries"
            :key="srcCol"
            class="node-card"
            :class="{ 'node-disabled': !rule.include_in_silver }"
          >
            <div class="node-source">
              <label class="switch">
                <input type="checkbox" :checked="rule.include_in_silver" @change="emit('toggle-include', String(srcCol))">
                <span class="slider"></span>
              </label>
              <div class="col-meta">
                <span class="col-type-tag">BRONCE</span>
                <span class="col-src-name">{{ srcCol }}</span>
              </div>
            </div>

            <div class="node-connector">
              <span class="connector-line"></span>
              <span class="connector-badge">{{ rule.target_data_type || 'VARCHAR' }}</span>
            </div>

            <div class="node-target">
              <span class="col-type-tag tag-silver">PLATA CANÓNICA</span>
              <input
                type="text"
                class="target-input"
                :value="rule.new_column_name || srcCol"
                :disabled="!rule.include_in_silver"
                @input="emit('update-target', { col: String(srcCol), target: ($event.target as HTMLInputElement).value })"
              >
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.schema-canvas { padding: 1.25rem; display: flex; flex-direction: column; gap: 1rem; }
.canvas-header { display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 1rem; }
.header-info { display: flex; align-items: center; gap: 0.75rem; }
.canvas-title { font-size: 1.15rem; font-weight: 700; color: var(--text-main); margin: 0; }
.badge-recipe { font-size: 0.75rem; background: rgba(16, 185, 129, 0.15); border: 1px solid var(--accent-emerald); color: var(--accent-emerald); padding: 0.2rem 0.5rem; border-radius: 4px; font-weight: 600; }
.view-mode-selector { display: flex; background: #0f172a; padding: 0.25rem; border-radius: 8px; border: 1px solid rgba(255,255,255,0.1); }
.btn-mode { background: transparent; border: none; color: #94a3b8; padding: 0.35rem 0.75rem; border-radius: 6px; font-size: 0.78rem; font-weight: 700; cursor: pointer; }
.mode-active { background: #6366f1; color: #fff; }
.canvas-stats { display: flex; align-items: center; gap: 0.5rem; font-size: 0.85rem; }
.stat-pill { background: rgba(255,255,255,0.05); border: 1px solid rgba(255,255,255,0.1); padding: 0.25rem 0.6rem; border-radius: 6px; color: var(--text-muted); }
.stat-active { border-color: rgba(59, 130, 246, 0.4); color: #60a5fa; background: rgba(59, 130, 246, 0.1); }
.stat-arrow { color: var(--text-muted); font-size: 0.8rem; }
.btn-primary { background: linear-gradient(135deg, #3b82f6, #2563eb); font-weight: 600; padding: 0.5rem 1rem; border-radius: 6px; color: #fff; cursor: pointer; border: none; }
.btn-primary:disabled { opacity: 0.5; cursor: not-allowed; }
.canvas-toolbar { display: flex; align-items: center; gap: 1rem; flex-wrap: wrap; background: rgba(0,0,0,0.2); padding: 0.5rem 0.75rem; border-radius: 8px; margin-bottom: 0.75rem; }
.search-input { background: rgba(0,0,0,0.3); border: 1px solid rgba(255,255,255,0.15); color: #fff; padding: 0.35rem 0.6rem; border-radius: 6px; font-size: 0.85rem; width: 260px; }
.toggle-label { font-size: 0.8rem; color: var(--text-muted); display: flex; align-items: center; gap: 0.4rem; cursor: pointer; }
.nodes-viewport { max-height: 480px; overflow-y: auto; padding-right: 0.25rem; }
.nodes-grid { display: flex; flex-direction: column; gap: 0.6rem; }
.node-card { display: grid; grid-template-columns: 1.2fr 0.8fr 1.2fr; align-items: center; background: rgba(255, 255, 255, 0.03); border: 1px solid rgba(255, 255, 255, 0.08); padding: 0.6rem 0.85rem; border-radius: 8px; }
.node-source { display: flex; align-items: center; gap: 0.75rem; }
.col-meta { display: flex; flex-direction: column; gap: 0.1rem; }
.col-type-tag { font-size: 0.65rem; color: var(--text-muted); font-weight: 700; }
.tag-silver { color: #60a5fa; }
.col-src-name { font-family: monospace; font-size: 0.85rem; color: var(--accent-amber); font-weight: 600; }
.node-connector { display: flex; align-items: center; justify-content: center; position: relative; }
.connector-line { width: 100%; height: 2px; background: linear-gradient(90deg, #f59e0b, #3b82f6); opacity: 0.5; }
.connector-badge { position: absolute; font-size: 0.65rem; font-family: monospace; background: rgba(0,0,0,0.8); border: 1px solid rgba(255,255,255,0.15); color: #fff; padding: 0.1rem 0.4rem; border-radius: 4px; }
.node-target { display: flex; flex-direction: column; gap: 0.2rem; }
.target-input { background: rgba(0,0,0,0.4); border: 1px solid rgba(255,255,255,0.15); color: #fff; padding: 0.35rem 0.5rem; border-radius: 4px; font-size: 0.85rem; font-family: monospace; width: 100%; }
.switch { position: relative; display: inline-block; width: 34px; height: 18px; }
.switch input { opacity: 0; width: 0; height: 0; }
.slider { position: absolute; cursor: pointer; top: 0; left: 0; right: 0; bottom: 0; background-color: #374151; transition: .2s; border-radius: 18px; }
.slider:before { position: absolute; content: ""; height: 12px; width: 12px; left: 3px; bottom: 3px; background-color: white; transition: .2s; border-radius: 50%; }
input:checked + .slider { background-color: #3b82f6; }
input:checked + .slider:before { transform: translateX(16px); }
.canvas-empty { padding: 2rem; text-align: center; color: var(--text-muted); font-style: italic; }
</style>
