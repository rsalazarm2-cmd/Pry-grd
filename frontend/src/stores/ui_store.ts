/**
 * Store de UI: tab activo y tema visual (dark/light).
 * Equivalente a ui_store.rs de Dioxus (Signals → Pinia).
 */

import { defineStore } from 'pinia'
import { ref } from 'vue'

export type MedallionTab = 'bronze' | 'silver' | 'gold' | 'audit'
export type ThemeMode = 'dark' | 'light'

export const useUiStore = defineStore('ui', () => {
  const activeTab = ref<MedallionTab>('bronze')
  const themeMode = ref<ThemeMode>('dark')

  /** Cambia el tab activo del workspace Medallion. */
  function setActiveTab(tab: MedallionTab): void {
    activeTab.value = tab
  }

  /** Alterna entre tema oscuro y claro. */
  function toggleTheme(): void {
    themeMode.value = themeMode.value === 'dark' ? 'light' : 'dark'
    document.body.classList.toggle('theme-light', themeMode.value === 'light')
  }

  return { activeTab, themeMode, setActiveTab, toggleTheme }
})
