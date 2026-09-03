<script setup lang="ts">
/**
 * Header principal de la aplicación.
 * Muestra branding, botón de Menú Hamburguesa (Drawer) y toggle de tema dark/light.
 */
import { ref } from 'vue'
import { Sun, Moon, Shield, Menu } from '@lucide/vue'
import { useUiStore } from '@/stores/ui_store'
import { useProjectStore } from '@/stores/project_store'
import NavDrawer from '@/components/layout/NavDrawer.vue'

const ui = useUiStore()
const store = useProjectStore()
const isDrawerOpen = ref(false)

function toggleDrawer(): void {
  isDrawerOpen.value = !isDrawerOpen.value
}
</script>

<template>
  <header class="app-header">
    <div class="header-left">
      <button class="btn-hamburger" @click="toggleDrawer" title="Menú Principal (Drawer)">
        <Menu :size="22" />
      </button>
      
      <div class="brand">
        <div class="brand-icon">
          <Shield :size="22" />
        </div>
        <div>
          <h1 class="brand-title">Auditoría Forense</h1>
          <div class="brand-subtitle">
            Medallion Architecture · {{ store.projectId.toUpperCase() }}
          </div>
        </div>
      </div>
    </div>

    <div class="header-right">
      <button class="btn-icon" @click="ui.toggleTheme()" :title="ui.themeMode === 'dark' ? 'Modo Claro' : 'Modo Oscuro'">
        <Sun v-if="ui.themeMode === 'dark'" :size="20" />
        <Moon v-else :size="20" />
      </button>
    </div>

    <!-- Menú Lateral (Drawer) -->
    <NavDrawer :is-open="isDrawerOpen" @close="isDrawerOpen = false" />
  </header>
</template>

<style scoped>
.app-header { display: flex; justify-content: space-between; align-items: center; padding: 0.85rem 1.5rem; border-bottom: 1px solid var(--border-glass); background: rgba(15, 23, 42, 0.4); }
.header-left { display: flex; align-items: center; gap: 1rem; }
.btn-hamburger { background: rgba(30, 41, 59, 0.6); border: 1px solid var(--border-glass); border-radius: 8px; padding: 0.45rem 0.65rem; color: #f8fafc; cursor: pointer; transition: all 0.2s ease; display: flex; align-items: center; justify-content: center; }
.btn-hamburger:hover { background: rgba(99, 102, 241, 0.2); border-color: #818cf8; color: #38bdf8; }

.brand { display: flex; align-items: center; gap: 0.75rem; }
.brand-icon { width: 36px; height: 36px; display: flex; align-items: center; justify-content: center; background: linear-gradient(135deg, var(--accent-indigo), var(--accent-purple)); border-radius: 9px; color: white; }
.brand-title { font-size: 1.15rem; font-weight: 800; color: var(--text-main); margin: 0; line-height: 1.2; }
.brand-subtitle { font-size: 0.72rem; color: var(--text-muted); font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em; }

.header-right { display: flex; align-items: center; gap: 0.5rem; }
.btn-icon { background: var(--bg-card); border: 1px solid var(--border-glass); border-radius: 8px; padding: 0.45rem; color: var(--text-muted); cursor: pointer; transition: all 0.2s ease; }
.btn-icon:hover { color: var(--accent-cyan); border-color: var(--accent-cyan); background: var(--bg-card-hover); }
</style>
