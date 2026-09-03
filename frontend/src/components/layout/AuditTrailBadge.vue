<script setup lang="ts">
/**
 * Componente UI de Verificación Criptográfica SHA-256 (Fase 4).
 * Muestra el estado de la Cadena de Custodia y la firma inmutable de los datos.
 */
import { ref, onMounted } from 'vue'
import { apiGet } from '@/api/http_client'

const props = defineProps<{ projectId?: string }>()

interface AuditReceipt {
  recipe_hash_sha256: string
  dataset_hash_sha256: string
  row_count: number
  timestamp: string
  integrity_status: string
}

const receipt = ref<AuditReceipt | null>(null)
const showModal = ref(false)

async function loadReceipt() {
  try {
    const q = props.projectId ? `?project_id=${encodeURIComponent(props.projectId)}` : ''
    receipt.value = await apiGet<AuditReceipt>(`/core/audit-receipt${q}`)
  } catch (err) {
    console.error('Error cargando recibo criptográfico:', err)
  }
}

onMounted(loadReceipt)
</script>

<template>
  <div class="audit-badge-container">
    <button class="badge-btn" @click="showModal = true">
      <span class="lock-icon">🔒</span>
      <span class="badge-text">SHA-256 Verified</span>
    </button>

    <!-- Modal Modal Audit Receipt -->
    <div v-if="showModal" class="modal-backdrop" @click.self="showModal = false">
      <div class="modal-card glass-card">
        <div class="modal-header">
          <h4>🛡️ Cadena de Custodia & Firma Criptográfica (SHA-256)</h4>
          <button class="btn-close" @click="showModal = false">✕</button>
        </div>

        <div v-if="receipt" class="modal-body">
          <div class="status-row">
            <span class="status-lbl">Estado de Integridad:</span>
            <span class="status-tag tag-verified">{{ receipt.integrity_status }}</span>
          </div>

          <div class="hash-field">
            <label>Firma SHA-256 del Parquet Activo:</label>
            <code class="hash-code">{{ receipt.dataset_hash_sha256 }}</code>
          </div>

          <div class="hash-field">
            <label>Firma SHA-256 de Receta (.json):</label>
            <code class="hash-code">{{ receipt.recipe_hash_sha256 }}</code>
          </div>

          <div class="meta-grid">
            <div><span class="lbl">Registros Verificados:</span> <strong>{{ receipt.row_count }}</strong></div>
            <div><span class="lbl">Sello de Tiempo:</span> <strong class="font-mono">{{ new Date(receipt.timestamp).toLocaleString() }}</strong></div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.audit-badge-container { display: inline-block; }
.badge-btn { display: flex; align-items: center; gap: 0.35rem; background: rgba(16, 185, 129, 0.15); border: 1px solid #10b981; color: #34d399; padding: 0.25rem 0.6rem; border-radius: 20px; font-size: 0.75rem; font-weight: 700; cursor: pointer; }
.lock-icon { font-size: 0.8rem; }
.modal-backdrop { position: fixed; inset: 0; background: rgba(0,0,0,0.7); backdrop-filter: blur(4px); display: flex; align-items: center; justify-content: center; z-index: 1000; }
.modal-card { width: 90%; max-width: 520px; padding: 1.25rem; background: #0f172a; border: 1px solid rgba(255,255,255,0.15); border-radius: 12px; display: flex; flex-direction: column; gap: 1rem; }
.modal-header { display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid rgba(255,255,255,0.08); pb: 0.5rem; }
.modal-header h4 { margin: 0; font-size: 0.95rem; color: #f8fafc; font-weight: 700; }
.btn-close { background: transparent; border: none; color: #94a3b8; font-size: 1rem; cursor: pointer; }
.modal-body { display: flex; flex-direction: column; gap: 0.85rem; font-size: 0.8rem; }
.status-row { display: flex; justify-content: space-between; align-items: center; }
.status-lbl { color: #94a3b8; font-weight: 600; }
.status-tag { padding: 0.15rem 0.5rem; border-radius: 4px; font-weight: 800; font-size: 0.75rem; }
.tag-verified { background: rgba(16, 185, 129, 0.2); color: #34d399; border: 1px solid #10b981; }
.hash-field { display: flex; flex-direction: column; gap: 0.25rem; }
.hash-field label { color: #94a3b8; font-size: 0.75rem; font-weight: 600; }
.hash-code { background: #090d16; padding: 0.4rem 0.6rem; border-radius: 4px; font-family: monospace; font-size: 0.75rem; color: #f59e0b; word-break: break-all; border: 1px solid rgba(255,255,255,0.05); }
.meta-grid { display: flex; justify-content: space-between; border-top: 1px solid rgba(255,255,255,0.08); pt: 0.6rem; color: #cbd5e1; font-size: 0.75rem; }
.font-mono { font-family: monospace; }
</style>
