<script setup lang="ts">
/**
 * Componente Modal de Previsualización SQL para el Canvas Visual Pro.
 * Muestra la consulta DuckDB `CREATE VIEW` compilada en tiempo real.
 */
defineProps<{
  show: boolean
  sqlCode: string
}>()

const emit = defineEmits<{
  (e: 'close'): void
}>()
</script>

<template>
  <div v-if="show" class="modal-backdrop" @click.self="emit('close')">
    <div class="modal-card glass-card">
      <div class="modal-header">
        <h4>💻 Sentencia SQL Compilada (DuckDB)</h4>
        <button class="btn-close" @click="emit('close')">✕</button>
      </div>
      <div class="modal-body">
        <pre class="sql-code"><code>{{ sqlCode }}</code></pre>
      </div>
    </div>
  </div>
</template>

<style scoped>
.modal-backdrop { position: fixed; inset: 0; background: rgba(0,0,0,0.75); backdrop-filter: blur(4px); display: flex; align-items: center; justify-content: center; z-index: 100; }
.modal-card { width: 90%; max-width: 600px; padding: 1.25rem; background: #0f172a; border-radius: 12px; border: 1px solid rgba(255,255,255,0.15); }
.modal-header { display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid rgba(255,255,255,0.08); pb: 0.5rem; }
.modal-header h4 { margin: 0; color: #f8fafc; font-size: 0.95rem; font-weight: 700; }
.btn-close { background: transparent; border: none; color: #94a3b8; font-size: 1rem; cursor: pointer; }
.sql-code { background: #090d16; padding: 1rem; border-radius: 6px; color: #38bdf8; font-family: monospace; font-size: 0.8rem; overflow-x: auto; margin-top: 0.75rem; border: 1px solid rgba(255,255,255,0.05); }
</style>
