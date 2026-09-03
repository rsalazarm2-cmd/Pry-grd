<script setup lang="ts">
/**
 * Componente Barra de Herramientas para el Canvas Visual Pro.
 * Contiene controles de Zoom, Botón de Agregar Vista Manual, Botones de Acción (IA) y SQL.
 */
defineProps<{
  targetNodesCount: number
  zoomLevel: number
}>()

const emit = defineEmits<{
  (e: 'updateZoom', delta: number): void
  (e: 'resetZoom'): void
  (e: 'openSqlModal'): void
  (e: 'autoSuggest'): void
  (e: 'addCustomView'): void
}>()
</script>

<template>
  <div class="studio-toolbar">
    <div class="toolbar-left">
      <span class="studio-title">🎨 Studio Blueprint Canvas (Capa Plata Pro)</span>
      <span class="badge-entities">{{ targetNodesCount }} Vistas para ORO</span>
    </div>

    <!-- Zoom & Action Toolbar -->
    <div class="toolbar-center">
      <div class="zoom-controls">
        <button class="btn-zoom" @click="emit('updateZoom', -0.1)">-</button>
        <span class="zoom-text">{{ Math.round(zoomLevel * 100) }}%</span>
        <button class="btn-zoom" @click="emit('updateZoom', 0.1)">+</button>
        <button class="btn-zoom-reset" @click="emit('resetZoom')">Reset</button>
      </div>
    </div>

    <div class="toolbar-right">
      <button class="btn-add-view" @click="emit('addCustomView')">
        ➕ Agregar Vista
      </button>
      <button class="btn-sql-preview" @click="emit('openSqlModal')">
        💻 Previsualizar SQL
      </button>
      <button class="btn-suggest-ia" @click="emit('autoSuggest')">
        ✨ Auto-Sugerir (IA)
      </button>
    </div>
  </div>
</template>

<style scoped>
.studio-toolbar { padding: 0.65rem 1rem; background: #0f172a; border-bottom: 1px solid rgba(255,255,255,0.08); display: flex; justify-content: space-between; align-items: center; z-index: 20; }
.studio-title { font-weight: 800; font-size: 0.9rem; color: #f8fafc; }
.badge-entities { margin-left: 0.5rem; background: rgba(56, 189, 248, 0.15); color: #38bdf8; padding: 0.2rem 0.5rem; border-radius: 4px; font-size: 0.7rem; font-weight: 700; }
.toolbar-center { display: flex; align-items: center; }
.zoom-controls { display: flex; align-items: center; gap: 0.3rem; background: #090d16; padding: 0.15rem 0.5rem; border-radius: 6px; border: 1px solid rgba(255,255,255,0.1); }
.btn-zoom { background: transparent; border: none; color: #38bdf8; font-weight: 800; cursor: pointer; padding: 0.1rem 0.4rem; }
.btn-zoom-reset { background: transparent; border: none; color: #94a3b8; font-size: 0.7rem; cursor: pointer; }
.zoom-text { font-size: 0.75rem; color: #f8fafc; font-weight: 700; min-width: 40px; text-align: center; }
.toolbar-right { display: flex; gap: 0.4rem; }
.btn-suggest-ia, .btn-sql-preview, .btn-add-view { color: #fff; border: none; padding: 0.35rem 0.75rem; border-radius: 6px; font-weight: 700; font-size: 0.75rem; cursor: pointer; }
.btn-add-view { background: linear-gradient(135deg, #0284c7, #0369a1); }
.btn-suggest-ia { background: linear-gradient(135deg, #10b981, #059669); }
.btn-sql-preview { background: linear-gradient(135deg, #6366f1, #4f46e5); }
</style>
