import { defineStore } from 'pinia'
import { ref, watch } from 'vue'
import type { DatasetProfileDTO } from '@/types/profiling'
import type { BronzeToSilverRulesDTO, SystemConfigOptionsDTO } from '@/types/bronze'
import { createDefaultRules } from '@/types/bronze'
import { fetchConfigOptions, fetchSuggestMapping, fetchBronzeProfile } from '@/api/bronze_api'
import { fetchSilverRecords } from '@/api/silver_api'
import { fetchProjectsList, deleteProjectApi, type ProjectDTO } from '@/api/projects_api'
import { useUiStore } from '@/stores/ui_store'

export const useProjectStore = defineStore('project', () => {
  const projectId = ref(localStorage.getItem('active_project_id') || 'proyecto-principal')
  const availableProjects = ref<ProjectDTO[]>([])
  const rules = ref<BronzeToSilverRulesDTO>(createDefaultRules())
  const configOptions = ref<SystemConfigOptionsDTO | null>(null)
  const profile = ref<DatasetProfileDTO | null>(null)
  const hasSilverData = ref(false)
  const silverRowCount = ref(0)
  const isLoadingProfile = ref(false)
  const isLoadingSuggestions = ref(false)

  watch(projectId, (newId) => {
    if (newId) {
      localStorage.setItem('active_project_id', newId)
    }
  })

  function selectProject(id: string): void {
    projectId.value = id
    localStorage.setItem('active_project_id', id)
    profile.value = null
    loadProfile(true)
    checkSilverStatus()
  }

  function setSilverStatus(exists: boolean, count: number = 0): void {
    hasSilverData.value = exists
    silverRowCount.value = count
  }

  async function loadProjects(): Promise<void> {
    try {
      const list = await fetchProjectsList()
      availableProjects.value = list
      if (list.length > 0 && !list.some(p => p.id === projectId.value)) {
        selectProject(list[0].id)
      } else if (projectId.value) {
        localStorage.setItem('active_project_id', projectId.value)
      }
    } catch (err) {
      console.error('Error cargando lista de proyectos:', err)
    }
  }

  async function removeProject(id: string): Promise<boolean> {
    try {
      await deleteProjectApi(id)
      rules.value = createDefaultRules()
      profile.value = null
      hasSilverData.value = false
      silverRowCount.value = 0
      await loadProjects()
      if (availableProjects.value.length > 0) {
        selectProject(availableProjects.value[0].id)
      }
      return true
    } catch (err) {
      console.error('Error eliminando proyecto:', err)
      return false
    }
  }

  async function checkSilverStatus(): Promise<void> {
    try {
      const res = await fetchSilverRecords(1)
      if (res && res.total_returned > 0) {
        setSilverStatus(true, res.total_returned)
      } else {
        setSilverStatus(false, 0)
      }
    } catch {
      setSilverStatus(false, 0)
    }
  }

  async function initializeSmartNavigation(): Promise<void> {
    const ui = useUiStore()
    await loadProjects()
    await checkSilverStatus()
    await loadProfile(true)
    if (hasSilverData.value) {
      ui.setActiveTab('silver')
    } else {
      ui.setActiveTab('bronze')
    }
  }

  async function loadProfile(force: boolean = false): Promise<void> {
    if (!force && profile.value) return
    isLoadingProfile.value = true
    try {
      profile.value = await fetchBronzeProfile()
    } catch (err) {
      console.error('Error cargando perfil:', err)
    } finally {
      isLoadingProfile.value = false
    }
  }

  async function loadConfigOptions(): Promise<void> {
    if (configOptions.value) return
    try {
      configOptions.value = await fetchConfigOptions()
    } catch (err) {
      console.error('Error cargando config options:', err)
    }
  }

  async function loadSuggestedMapping(targetLang: string = 'es', force: boolean = false): Promise<void> {
    if (!force && Object.keys(rules.value.column_rules).length > 0) return
    isLoadingSuggestions.value = true
    try {
      rules.value = await fetchSuggestMapping(targetLang, force)
    } catch (err) {
      console.error('Error cargando mapeo sugerido:', err)
    } finally {
      isLoadingSuggestions.value = false
    }
  }


  return {
    projectId,
    availableProjects,
    rules,
    configOptions,
    profile,
    hasSilverData,
    silverRowCount,
    isLoadingProfile,
    isLoadingSuggestions,
    selectProject,
    setSilverStatus,
    checkSilverStatus,
    initializeSmartNavigation,
    loadProjects,
    removeProject,
    loadProfile,
    loadConfigOptions,
    loadSuggestedMapping,
  }
})
