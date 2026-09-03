import type { StateCreator } from 'zustand';
import type { Project } from '../api/client';

export interface MedallionUIState {
  activeTab: 'bronze' | 'silver' | 'gold';
  setActiveTab: (tab: 'bronze' | 'silver' | 'gold') => void;
  themeMode: 'dark' | 'light';
  toggleTheme: () => void;
  activeProject: Project | null;
  setActiveProject: (project: Project | null) => void;
  isProjectModalOpen: boolean;
  setIsProjectModalOpen: (isOpen: boolean) => void;
  isCleaningModalOpen: boolean;
  setIsCleaningModalOpen: (isOpen: boolean) => void;
  isAtomicityModalOpen: boolean;
  setIsAtomicityModalOpen: (isOpen: boolean) => void;
  transformError: string | null;
  setTransformError: (error: string | null) => void;
}

export const createUISlice: StateCreator<MedallionUIState, [], [], MedallionUIState> = (set) => ({
  activeTab: 'bronze',
  setActiveTab: (tab) => set({ activeTab: tab }),
  themeMode: 'dark',
  toggleTheme: () => set((state) => {
    const newTheme = state.themeMode === 'dark' ? 'light' : 'dark';
    if (newTheme === 'light') {
      document.body.classList.add('theme-light');
    } else {
      document.body.classList.remove('theme-light');
    }
    return { themeMode: newTheme };
  }),
  activeProject: null,
  setActiveProject: (project) => set({ activeProject: project }),
  isProjectModalOpen: true,
  setIsProjectModalOpen: (isOpen) => set({ isProjectModalOpen: isOpen }),
  isCleaningModalOpen: false,
  setIsCleaningModalOpen: (isOpen) => set({ isCleaningModalOpen: isOpen }),
  isAtomicityModalOpen: false,
  setIsAtomicityModalOpen: (isOpen) => set({ isAtomicityModalOpen: isOpen }),
  transformError: null,
  setTransformError: (error) => set({ transformError: error }),
});
