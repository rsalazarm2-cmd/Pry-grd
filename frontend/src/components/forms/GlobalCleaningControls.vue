<script setup lang="ts">
/**
 * Panel de Controles Globales de Limpieza y Mapeo Semántico.
 * Permite cambiar idioma de traducción, tildes/Ñ, duplicados y trampas forenses.
 */
import { ref } from 'vue'
import { useProjectStore } from '@/stores/project_store'

const store = useProjectStore()
const currentLang = ref<'es' | 'en'>('es')

async function handleRemap(): Promise<void> {
  await store.loadSuggestedMapping(currentLang.value, true)
}
</script>

<template>
  <div class="global-controls-panel">
    <!-- Header / Selector de Idioma -->
    <div class="panel-row border-bottom">
      <div class="control-group">
        <label class="group-title">🌐 Idioma Esquema Destino</label>
        <div class="lang-selector">
          <select v-model="currentLang" class="select-lang">
            <option value="es">🇪🇸 Español (Estándar NIIF/Oracle EBS)</option>
            <option value="en">🇺🇸 English (Standard ERP GL)</option>
          </select>
          <button
            class="btn-remap"
            :disabled="store.isLoadingSuggestions"
            @click="handleRemap"
          >
            {{ store.isLoadingSuggestions ? '⏳ Mapeando...' : '✨ Re-mapear con IA' }}
          </button>
        </div>
      </div>
    </div>

    <!-- Opciones Globales de Limpieza -->
    <div class="panel-grid">
      <div class="control-card">
        <label class="card-title">🧹 Limpieza de Caracteres y Texto</label>
        <div class="checkbox-list">
          <label class="checkbox-label">
            <input
              type="checkbox"
              v-model="store.rules.global_clean_accents_and_n"
              class="checkbox-custom"
            />
            <span>Limpiar Tildes (Á,É,Í,Ó,Ú) y reemplazar Ñ por N</span>
          </label>

          <label class="checkbox-label">
            <input
              type="checkbox"
              v-model="store.rules.global_clean_special_chars"
              class="checkbox-custom"
            />
            <span>Limpiar Caracteres Especiales (@,#,$,%,&,/,etc.)</span>
          </label>

          <label class="checkbox-label">
            <input
              type="checkbox"
              v-model="store.rules.global_trim_spaces"
              class="checkbox-custom"
            />
            <span>Eliminar Espacios en Blanco (Trim) al Inicio y Final</span>
          </label>

          <label class="checkbox-label">
            <input
              type="checkbox"
              v-model="store.rules.global_convert_uppercase"
              class="checkbox-custom"
            />
            <span>🔠 Convertir Todo a Mayúsculas (Transformar a Mayúsculas)</span>
          </label>

          <label class="checkbox-label">
            <input
              type="checkbox"
              v-model="store.rules.global_clean_colons"
              class="checkbox-custom"
            />
            <span>Limpiar Dos Puntos (:) de los Textos</span>
          </label>

        </div>
      </div>

      <!-- Manejo de Duplicados y Forense -->
      <div class="control-card">
        <label class="card-title">🕵️ Auditoría Forense y Duplicados</label>
        <div class="form-group">
          <label class="input-label">Manejo de Asientos Duplicados:</label>
          <select v-model="store.rules.duplicate_action_mode" class="select-full">
            <option
              v-for="opt in store.configOptions?.duplicate_action_modes || []"
              :key="opt.id"
              :value="opt.id"
            >
              {{ opt.label }}
            </option>
          </select>
        </div>

        <div class="checkbox-list margin-top">
          <label class="checkbox-label">
            <input
              type="checkbox"
              v-model="store.rules.enable_forensic_trap_detection"
              class="checkbox-custom"
            />
            <span>Habilitar Detección de Trampas Forenses (Cut-Off, Alteraciones)</span>
          </label>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.global-controls-panel {
  background: rgba(15, 23, 42, 0.6);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 10px;
  padding: 1.25rem;
  margin-bottom: 1.25rem;
}
.panel-row { padding-bottom: 1rem; margin-bottom: 1rem; }
.border-bottom { border-bottom: 1px solid rgba(255, 255, 255, 0.08); }
.group-title { font-size: 0.9rem; font-weight: 700; color: #a5b4fc; margin-bottom: 0.5rem; display: block; }
.lang-selector { display: flex; gap: 0.75rem; align-items: center; }
.select-lang { padding: 0.45rem 0.85rem; border-radius: 6px; border: 1px solid rgba(99, 102, 241, 0.3); background: #1e293b; color: #f8fafc; font-size: 0.85rem; font-weight: 600; outline: none; }
.btn-remap { background: linear-gradient(135deg, #6366f1, #8b5cf6); color: white; border: none; padding: 0.45rem 1rem; border-radius: 6px; font-weight: 700; font-size: 0.83rem; cursor: pointer; transition: transform 0.15s; }
.btn-remap:hover { transform: translateY(-1px); }
.panel-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 1.25rem; }
.control-card { background: rgba(30, 41, 59, 0.4); border: 1px solid rgba(255, 255, 255, 0.05); border-radius: 8px; padding: 1rem; }
.card-title { font-size: 0.85rem; font-weight: 700; color: var(--text-main); margin-bottom: 0.75rem; display: block; }
.checkbox-list { display: flex; flex-direction: column; gap: 0.6rem; }
.checkbox-label { display: flex; align-items: center; gap: 0.55rem; font-size: 0.82rem; color: #cbd5e1; cursor: pointer; }
.checkbox-custom { width: 16px; height: 16px; accent-color: #6366f1; cursor: pointer; }
.form-group { display: flex; flex-direction: column; gap: 0.35rem; }
.input-label { font-size: 0.8rem; color: #94a3b8; }
.select-full { width: 100%; padding: 0.45rem 0.75rem; border-radius: 6px; border: 1px solid rgba(255,255,255,0.12); background: #1e293b; color: #f8fafc; font-size: 0.82rem; }
.margin-top { margin-top: 0.85rem; }
</style>
