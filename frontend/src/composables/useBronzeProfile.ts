import { computed, onMounted } from 'vue'
import { useProjectStore } from '@/stores/project_store'

export function useBronzeProfile() {
  const store = useProjectStore()

  onMounted(() => {
    store.loadProfile()
  })

  return {
    profile: computed(() => store.profile),
    isLoading: computed(() => store.isLoadingProfile),
    reload: (force: boolean = true) => store.loadProfile(force),
  }
}
