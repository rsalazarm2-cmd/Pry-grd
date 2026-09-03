<script setup lang="ts">
/**
 * Navegación por tabs del Medallion Architecture.
 * Tabs: Bronce, Plata, Oro, Auditoría.
 */
import { useUiStore, type MedallionTab } from '@/stores/ui_store'

const ui = useUiStore()

const tabs: { id: MedallionTab; label: string; emoji: string }[] = [
  { id: 'bronze', label: 'Capa Bronce', emoji: '🥉' },
  { id: 'silver', label: 'Capa Plata', emoji: '🥈' },
  { id: 'gold', label: 'Capa Oro', emoji: '🥇' },
  { id: 'audit', label: 'Auditoría', emoji: '🛡️' },
]
</script>

<template>
  <nav class="tabs-nav">
    <button
      v-for="tab in tabs"
      :key="tab.id"
      :class="['tab-btn', { active: ui.activeTab === tab.id }]"
      @click="ui.setActiveTab(tab.id)"
    >
      <span class="tab-emoji">{{ tab.emoji }}</span>
      {{ tab.label }}
    </button>
  </nav>
</template>

<style scoped>
.tabs-nav {
  display: flex;
  gap: 0.25rem;
  padding: 0 1.5rem;
  border-bottom: 1px solid var(--border-glass);
}

.tab-btn {
  display: flex;
  align-items: center;
  gap: 0.4rem;
  padding: 0.75rem 1.25rem;
  background: transparent;
  border: none;
  border-bottom: 2px solid transparent;
  color: var(--text-muted);
  font-family: var(--font-sans);
  font-size: 0.9rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
}

.tab-btn:hover {
  color: var(--text-main);
  background: var(--bg-card-hover);
}

.tab-btn.active {
  color: var(--accent-cyan);
  border-bottom-color: var(--accent-cyan);
}

.tab-emoji {
  font-size: 1rem;
}
</style>
