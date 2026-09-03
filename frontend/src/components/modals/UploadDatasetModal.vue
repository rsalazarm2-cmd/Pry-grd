<script setup lang="ts">
/**
 * Modal Enterprise para Carga e Ingesta de Nuevos Datasets (CSV/Parquet).
 * Permite al auditor subir nuevos archivos contables a disco.
 */
import { ref } from 'vue'
import { uploadIngest } from '@/api/bronze_api'
import { useProjectStore } from '@/stores/project_store'

const emit = defineEmits<{(e: 'close'): void; (e: 'success'): void}>()
const store = useProjectStore()

const fileInput = ref<HTMLInputElement | null>(null)
const selectedFile = ref<File | null>(null)
const projectNameInput = ref('')
const isUploading = ref(false)
const errorMessage = ref('')

function handleFileChange(event: Event): void {
  const target = event.target as HTMLInputElement
  if (target.files && target.files.length > 0) {
    selectedFile.value = target.files[0]
    if (!projectNameInput.value) {
      const baseName = selectedFile.value.name.split('.')[0]
      projectNameInput.value = baseName.toLowerCase().replace(/[^a-z0-9_]/g, '_')
    }
  }
}

async function handleUpload(): Promise<void> {
  if (!selectedFile.value) {
    errorMessage.value = 'Por favor selecciona un archivo CSV o Parquet.'
    return
  }

  isUploading.value = true
  errorMessage.value = ''

  try {
    const formData = new FormData()
    formData.append('file', selectedFile.value)

    const pid = projectNameInput.value.trim() || 'default'
    await uploadIngest(formData, pid)


    store.projectId = pid
    await store.initializeSmartNavigation()
    emit('success')
    emit('close')
  } catch (err: any) {
    console.error('Error al subir dataset:', err)
    errorMessage.value = err?.message || 'Error al procesar la ingesta del archivo.'
  } finally {
    isUploading.value = false
  }
}
</script>

<template>
  <Teleport to="body">
    <div class="modal-backdrop" @click="emit('close')">
      <div class="modal-card glass-card" @click.stop>
        <div class="modal-header">
          <div class="header-brand">
            <span class="brand-icon">📤</span>
            <div>
              <h3 class="modal-title">Cargar Nuevo Dataset / Proyecto</h3>
              <span class="modal-sub">Ingesta cruda de asientos contables a Capa Bronce</span>
            </div>
          </div>
          <button class="btn-close" @click="emit('close')">✕</button>
        </div>

        <div class="modal-body">
          <div v-if="errorMessage" class="error-banner">⚠️ {{ errorMessage }}</div>

          <div class="form-group">
            <label class="form-label">1. Seleccionar Archivo Contable (CSV / Parquet)</label>
            <div class="drop-zone" @click="fileInput?.click()">
              <span class="drop-icon">📄</span>
              <div v-if="selectedFile" class="file-details">
                <span class="file-name">{{ selectedFile.name }}</span>
                <span class="file-size">({{ (selectedFile.size / 1024).toFixed(1) }} KB)</span>
              </div>
              <div v-else class="drop-placeholder">
                <span class="drop-text">Haz clic o arrastra un archivo aquí</span>
                <span class="drop-sub">Formatos soportados: .csv, .txt, .parquet</span>
              </div>
              <input ref="fileInput" type="file" accept=".csv,.txt,.parquet" class="hidden-input" @change="handleFileChange" />
            </div>
          </div>

          <div class="form-group">
            <label class="form-label">2. Identificador del Proyecto</label>
            <input v-model="projectNameInput" type="text" placeholder="Ej: makro_q3_2026" class="form-input" />
          </div>
        </div>

        <div class="modal-footer">
          <button class="btn-cancel" @click="emit('close')">Cancelar</button>
          <button class="btn-primary" :disabled="isUploading || !selectedFile" @click="handleUpload">
            <span v-if="isUploading">⏳ Procesando Ingesta...</span>
            <span v-else>🚀 Ingestar en Capa Bronce</span>
          </button>
        </div>
      </div>
    </div>
  </Teleport>
</template>

<style scoped>
.modal-backdrop { position: fixed; inset: 0; background: rgba(15, 23, 42, 0.8); backdrop-filter: blur(6px); z-index: 1000; display: flex; align-items: center; justify-content: center; padding: 1rem; }
.modal-card { width: 100%; max-width: 480px; background: #0f172a; border: 1px solid rgba(56, 189, 248, 0.3); border-radius: 14px; padding: 1.5rem; display: flex; flex-direction: column; gap: 1.25rem; box-shadow: 0 20px 50px rgba(0,0,0,0.6); }
.modal-header { display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid rgba(255,255,255,0.08); padding-bottom: 1rem; }
.header-brand { display: flex; align-items: center; gap: 0.75rem; }
.brand-icon { font-size: 1.5rem; }
.modal-title { font-size: 1.05rem; font-weight: 700; color: #f8fafc; margin: 0; }
.modal-sub { font-size: 0.72rem; color: #94a3b8; }
.btn-close { background: none; border: none; color: #94a3b8; font-size: 1.2rem; cursor: pointer; }

.modal-body { display: flex; flex-direction: column; gap: 1rem; }
.error-banner { background: rgba(239, 68, 68, 0.15); border: 1px solid #ef4444; color: #f87171; padding: 0.6rem 0.8rem; border-radius: 8px; font-size: 0.8rem; }
.form-group { display: flex; flex-direction: column; gap: 0.4rem; }
.form-label { font-size: 0.8rem; font-weight: 600; color: #cbd5e1; }

.drop-zone { border: 2px dashed rgba(56, 189, 248, 0.4); border-radius: 10px; padding: 1.25rem; text-align: center; background: rgba(30, 41, 59, 0.4); cursor: pointer; transition: all 0.2s ease; display: flex; flex-direction: column; align-items: center; gap: 0.5rem; }
.drop-zone:hover { border-color: #38bdf8; background: rgba(56, 189, 248, 0.05); }
.drop-icon { font-size: 2rem; }
.drop-placeholder { display: flex; flex-direction: column; gap: 0.2rem; }
.drop-text { font-size: 0.85rem; font-weight: 600; color: #f8fafc; }
.drop-sub { font-size: 0.72rem; color: #94a3b8; }
.file-name { font-size: 0.88rem; font-weight: 700; color: #38bdf8; }
.file-size { font-size: 0.75rem; color: #94a3b8; }
.hidden-input { display: none; }

.form-input { background: #1e293b; border: 1px solid rgba(255,255,255,0.12); color: #f8fafc; padding: 0.6rem 0.8rem; border-radius: 8px; font-size: 0.85rem; font-family: var(--font-mono); outline: none; }
.form-input:focus { border-color: #38bdf8; }

.modal-footer { display: flex; justify-content: flex-end; gap: 0.75rem; border-top: 1px solid rgba(255,255,255,0.08); padding-top: 1rem; }
.btn-cancel { background: #334155; color: #f8fafc; border: none; padding: 0.5rem 1rem; border-radius: 6px; cursor: pointer; }
.btn-primary { background: linear-gradient(135deg, #38bdf8, #2563eb); color: white; border: none; padding: 0.5rem 1.2rem; border-radius: 6px; font-weight: 700; cursor: pointer; transition: transform 0.2s ease; }
.btn-primary:hover:not(:disabled) { transform: translateY(-1px); }
.btn-primary:disabled { opacity: 0.5; cursor: not-allowed; }
</style>
