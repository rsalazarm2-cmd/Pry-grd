import React from 'react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';

import { useMedallionStore } from './shared/store/medallionStore';
import { useMedallionQueries } from './shared/hooks/useMedallionQueries';

import { Header } from './shared/components/layout/Header';
import { KpiCards } from './shared/components/layout/KpiCards';
import { TabNavigation } from './shared/components/layout/TabNavigation';
import { EmptyProjectState } from './project/components/layout/EmptyProjectState';
import { ProjectSelectorModal } from './project/components/ProjectSelectorModal';

import { BronzeWorkspace } from './bronze/components/BronzeWorkspace';
import { SilverWorkspace } from './silver/components/SilverWorkspace';
import { GoldWorkspace } from './gold/components/GoldWorkspace';

const queryClient = new QueryClient();

export function AppContent() {
  const state = useMedallionStore();
  const { profile } = useMedallionQueries();

  return (
    <div className="app-container">
      <Header
        activeProject={state.activeProject}
        onOpenProjectModal={() => state.setIsProjectModalOpen(true)}
        themeMode={state.themeMode}
        onToggleTheme={state.toggleTheme}
      />

      <KpiCards
        profile={profile}
        activeProject={state.activeProject}
        onOpenCleaningModal={() => state.setActiveTab('bronze')}
      />

      <TabNavigation
        activeTab={state.activeTab}
        onTabChange={state.setActiveTab}
      />

      {!state.activeProject ? (
        <EmptyProjectState onOpenProjectModal={() => state.setIsProjectModalOpen(true)} />
      ) : (
        <>
          {state.activeTab === 'bronze' && <BronzeWorkspace />}
          {state.activeTab === 'silver' && <SilverWorkspace />}
          {state.activeTab === 'gold' && <GoldWorkspace />}
        </>
      )}

      <ProjectSelectorModal
        isOpen={state.isProjectModalOpen}
        onClose={() => state.setIsProjectModalOpen(false)}
        activeProject={state.activeProject}
        onSelectProject={(proj) => {
          state.setActiveProject(proj);
          if (proj) {
            state.setIsProjectModalOpen(false);
            state.loadRecipe(proj.id);
          }
        }}
      />
    </div>
  );
}

export default function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <AppContent />
    </QueryClientProvider>
  );
}
