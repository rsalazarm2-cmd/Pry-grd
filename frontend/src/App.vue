<script setup lang="ts">
/**
 * Root component de la aplicación.
 * Orquesta: Header (con Hamburguesa Drawer) → Workspace activo.
 * Ejecuta Smart First-Load para posicionar al auditor en la capa más madura (Plata/Oro).
 */
import { onMounted } from 'vue'
import { useUiStore } from '@/stores/ui_store'
import { useProjectStore } from '@/stores/project_store'
import AppHeader from '@/components/layout/AppHeader.vue'
import BronzeWorkspace from '@/views/BronzeWorkspace.vue'
import SilverWorkspace from '@/views/SilverWorkspace.vue'
import GoldWorkspace from '@/views/GoldWorkspace.vue'
import AuditWorkspace from '@/views/AuditWorkspace.vue'

const ui = useUiStore()
const store = useProjectStore()

onMounted(() => {
  store.initializeSmartNavigation()
})
</script>

<template>
  <div class="app-container">
    <AppHeader />

    <main class="workspace-area">
      <BronzeWorkspace v-if="ui.activeTab === 'bronze'" />
      <SilverWorkspace v-else-if="ui.activeTab === 'silver'" />
      <GoldWorkspace v-else-if="ui.activeTab === 'gold'" />
      <AuditWorkspace v-else-if="ui.activeTab === 'audit'" />
    </main>
  </div>
</template>

<style scoped>
.app-container {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

.workspace-area {
  flex: 1;
}
</style>
