<script setup lang="ts">
/**
 * Menú Lateral (Drawer) Enterprise con Gestión de Proyectos Reales,
 * Botón de Carga de Datasets, Modal de Eliminación y Coincidencia Visual Medallion.
 */
import { ref } from 'vue'
import { useUiStore } from '@/stores/ui_store'
import { useProjectStore } from '@/stores/project_store'
import UploadDatasetModal from '@/components/modals/UploadDatasetModal.vue'

defineProps<{ isOpen: boolean }>()
const emit = defineEmits<{(e: 'close'): void; (e: 'open-config'): void}>()

const ui = useUiStore()
const store = useProjectStore()
const projectToDelete = ref<string | null>(null)
const isDeleting = ref(false)
const showUploadModal = ref(false)

function selectTab(tab: 'bronze' | 'silver' | 'gold' | 'audit'): void {
  ui.setActiveTab(tab)
  emit('close')
}

function promptDelete(projectId: string, event: Event): void {
  event.stopPropagation()
  projectToDelete.value = projectId
}

async function confirmDelete(): Promise<void> {
  if (!projectToDelete.value) return
  isDeleting.value = true
  await store.removeProject(projectToDelete.value)
  projectToDelete.value = null
  isDeleting.value = false
  store.initializeSmartNavigation()
}
</script>

<template>
  <Teleport to="body">
    <div v-if="isOpen" class="drawer-backdrop" @click="emit('close')"></div>

    <aside class="drawer-panel" :class="{ 'is-open': isOpen }">
      <!-- Header -->
      <div class="drawer-header">
        <div class="drawer-brand">
          <span class="brand-icon">🛡️</span>
          <div>
            <h3 class="brand-title">Auditoría Forense</h3>
            <span class="brand-sub">Medallion Command Center</span>
          </div>
        </div>
        <button class="btn-close" @click="emit('close')">✕</button>
      </div>

      <!-- Sección 1: Proyectos Reales Activos & Carga -->
      <div class="drawer-section">
        <div class="section-header-row">
          <h4 class="section-title">📁 Proyectos Reales</h4>
          <button class="btn-new-dataset" title="Cargar Nuevo Dataset" @click="showUploadModal = true">+ Cargar Data</button>
        </div>

        <div class="project-list">
          <div v-for="proj in store.availableProjects" :key="proj.id" class="project-item" :class="{ selected: store.projectId === proj.id }" @click="store.projectId = proj.id; store.initializeSmartNavigation()">
            <span class="project-icon">🏛️</span>
            <div class="project-info">
              <span class="project-name">{{ proj.name }}</span>
              <span class="project-id">{{ proj.id }}</span>
            </div>
            <button class="btn-delete" title="Eliminar Proyecto" @click="promptDelete(proj.id, $event)">🗑️</button>
          </div>
          <div v-if="store.availableProjects.length === 0" class="no-projects">No hay proyectos creados.</div>
        </div>
      </div>

      <!-- Sección 2: Flujo Medallion con Coincidencia Cromática -->
      <div class="drawer-section">
        <h4 class="section-title">📊 Arquitectura de Datos</h4>
        <nav class="medallion-nav">
          <button class="nav-item item-bronze" :class="{ active: ui.activeTab === 'bronze' }" @click="selectTab('bronze')">
            <span class="item-icon">🥉</span>
            <span class="item-label">Capa Bronce (Data Lake)</span>
            <span class="status-badge badge-bronze">Data Cruda</span>
          </button>

          <button class="nav-item item-silver" :class="{ active: ui.activeTab === 'silver' }" @click="selectTab('silver')">
            <span class="item-icon">🥈</span>
            <span class="item-label">Capa Plata (Limpia)</span>
            <span class="status-badge" :class="store.hasSilverData ? 'badge-silver-ready' : 'badge-pending'">
              {{ store.hasSilverData ? '🟢 Procesado' : '⚪ Pendiente' }}
            </span>
          </button>

          <button class="nav-item item-gold" :class="{ active: ui.activeTab === 'gold' }" @click="selectTab('gold')">
            <span class="item-icon">🥇</span>
            <span class="item-label">Capa Oro (Marts)</span>
            <span class="status-badge badge-pending">⚪ Pendiente</span>
          </button>

          <button class="nav-item item-audit" :class="{ active: ui.activeTab === 'audit' }" @click="selectTab('audit')">
            <span class="item-icon">🛡️</span>
            <span class="item-label">Dashboard Auditoría</span>
            <span class="status-badge badge-audit">Command Center</span>
          </button>
        </nav>
      </div>
    </aside>

    <!-- Modal de Carga de Datasets -->
    <UploadDatasetModal v-if="showUploadModal" @close="showUploadModal = false" @success="emit('close')" />

    <!-- Modal de Confirmación de Eliminación -->
    <div v-if="projectToDelete" class="modal-backdrop">
      <div class="modal-card glass-card">
        <h3 class="modal-title">⚠️ Confirmación de Eliminación</h3>
        <p class="modal-desc">
          ¿Estás seguro de eliminar permanentemente el proyecto <strong>'{{ projectToDelete }}'</strong>? Se borrarán sus parquets, manifiestos y recetas de forma irreversible.
        </p>
        <div class="modal-actions">
          <button class="btn-cancel" @click="projectToDelete = null">Cancelar</button>
          <button class="btn-confirm-delete" :disabled="isDeleting" @click="confirmDelete">
            {{ isDeleting ? 'Borrando...' : '🗑️ Confirmar Eliminación' }}
          </button>
        </div>
      </div>
    </div>
  </Teleport>
</template>

<style scoped>
.drawer-backdrop { position: fixed; inset: 0; background: rgba(15, 23, 42, 0.7); backdrop-filter: blur(4px); z-index: 998; }
.drawer-panel { position: fixed; top: 0; bottom: 0; left: -320px; width: 300px; background: #0f172a; border-right: 1px solid rgba(255, 255, 255, 0.1); z-index: 999; display: flex; flex-direction: column; gap: 1.25rem; padding: 1.25rem; transition: left 0.3s ease; box-shadow: 10px 0 30px rgba(0,0,0,0.5); }
.drawer-panel.is-open { left: 0; }
.drawer-header { display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid rgba(255, 255, 255, 0.08); padding-bottom: 1rem; }
.drawer-brand { display: flex; align-items: center; gap: 0.75rem; }
.brand-icon { font-size: 1.5rem; }
.brand-title { font-size: 1rem; font-weight: 700; color: #f8fafc; margin: 0; }
.brand-sub { font-size: 0.72rem; color: #94a3b8; }
.btn-close { background: none; border: none; color: #94a3b8; font-size: 1.2rem; cursor: pointer; }

.drawer-section { display: flex; flex-direction: column; gap: 0.6rem; }
.section-header-row { display: flex; justify-content: space-between; align-items: center; }
.section-title { font-size: 0.75rem; font-weight: 700; color: #94a3b8; text-transform: uppercase; letter-spacing: 0.05em; margin: 0; }
.btn-new-dataset { background: rgba(56, 189, 248, 0.15); color: #38bdf8; border: 1px solid #38bdf8; font-size: 0.72rem; font-weight: 700; padding: 0.2rem 0.5rem; border-radius: 6px; cursor: pointer; transition: all 0.2s ease; }
.btn-new-dataset:hover { background: #38bdf8; color: #0f172a; }

.project-list { display: flex; flex-direction: column; gap: 0.4rem; max-height: 180px; overflow-y: auto; }
.project-item { display: flex; align-items: center; justify-content: space-between; gap: 0.5rem; padding: 0.5rem 0.75rem; background: #1e293b; border-radius: 8px; border: 1px solid rgba(255, 255, 255, 0.08); cursor: pointer; transition: all 0.2s ease; }
.project-item.selected { border-color: #38bdf8; background: rgba(56, 189, 248, 0.1); }
.project-info { display: flex; flex-direction: column; flex: 1; overflow: hidden; }
.project-name { font-size: 0.82rem; font-weight: 700; color: #f8fafc; }
.project-id { font-size: 0.7rem; color: #94a3b8; font-family: var(--font-mono); }
.btn-delete { background: none; border: none; cursor: pointer; opacity: 0.6; transition: opacity 0.2s ease; }
.btn-delete:hover { opacity: 1; }
.no-projects { font-size: 0.8rem; color: #94a3b8; font-style: italic; }

.medallion-nav { display: flex; flex-direction: column; gap: 0.4rem; }
.nav-item { display: flex; align-items: center; gap: 0.6rem; padding: 0.6rem 0.75rem; border-radius: 8px; background: rgba(30, 41, 59, 0.4); border: 1px solid transparent; color: #cbd5e1; font-size: 0.85rem; cursor: pointer; text-align: left; }
.nav-item.active.item-bronze { background: rgba(245, 158, 11, 0.15); border-color: #f59e0b; color: #fbbf24; }
.nav-item.active.item-silver { background: rgba(56, 189, 248, 0.15); border-color: #38bdf8; color: #38bdf8; }
.nav-item.active.item-gold { background: rgba(234, 179, 8, 0.15); border-color: #eab308; color: #fde047; }
.nav-item.active.item-audit { background: rgba(239, 68, 68, 0.15); border-color: #ef4444; color: #f87171; }
.item-label { flex: 1; }

.status-badge { font-size: 0.68rem; padding: 0.15rem 0.45rem; border-radius: 4px; font-weight: 600; }
.badge-bronze { background: rgba(245, 158, 11, 0.2); color: #fbbf24; }
.badge-silver-ready { background: rgba(56, 189, 248, 0.2); color: #38bdf8; }
.badge-pending { background: rgba(148, 163, 184, 0.1); color: #94a3b8; }
.badge-audit { background: rgba(239, 68, 68, 0.2); color: #f87171; }

.modal-backdrop { position: fixed; inset: 0; background: rgba(15, 23, 42, 0.8); backdrop-filter: blur(6px); z-index: 1000; display: flex; align-items: center; justify-content: center; padding: 1rem; }
.modal-card { width: 100%; max-width: 400px; padding: 1.5rem; background: #0f172a; border: 1px solid rgba(239, 68, 68, 0.4); border-radius: 12px; }
.modal-title { font-size: 1.1rem; color: #f87171; margin: 0 0 0.75rem 0; font-weight: 700; }
.modal-desc { font-size: 0.88rem; color: #cbd5e1; line-height: 1.4; margin-bottom: 1.25rem; }
.modal-actions { display: flex; justify-content: flex-end; gap: 0.75rem; }
.btn-cancel { background: #334155; color: #f8fafc; border: none; padding: 0.5rem 1rem; border-radius: 6px; cursor: pointer; }
.btn-confirm-delete { background: #ef4444; color: white; border: none; padding: 0.5rem 1rem; border-radius: 6px; font-weight: 700; cursor: pointer; }
</style>
