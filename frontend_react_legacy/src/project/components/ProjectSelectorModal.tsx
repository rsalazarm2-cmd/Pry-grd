import React from 'react';
import { FolderPlus, X } from 'lucide-react';
import type { Project } from '../../shared/api/client';
import { useProjectSelectorController } from '../hooks/useProjectSelectorController';
import { CreateProjectForm } from './CreateProjectForm';
import { ProjectList } from './ProjectList';

interface ProjectSelectorModalProps {
  isOpen: boolean;
  onClose: () => void;
  activeProject: Project | null;
  onSelectProject: (project: Project | null) => void;
}

export const ProjectSelectorModal: React.FC<ProjectSelectorModalProps> = ({
  isOpen,
  onClose,
  activeProject,
  onSelectProject,
}) => {
  const ctrl = useProjectSelectorController(isOpen, activeProject, onSelectProject, onClose);

  if (!isOpen) return null;

  const isMandatorySelection = activeProject === null;

  return (
    <div style={{ position: 'fixed', inset: 0, backgroundColor: 'var(--bg-modal-overlay)', backdropFilter: 'blur(12px)', display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 1000, padding: '1.5rem' }}>
      <div style={{ backgroundColor: 'var(--bg-modal-card)', border: '1px solid var(--border-glass)', borderRadius: '16px', width: '100%', maxWidth: '750px', maxHeight: '90vh', display: 'flex', flexDirection: 'column', boxShadow: 'var(--card-shadow)', overflow: 'hidden' }}>
        <div style={{ padding: '1.25rem 1.5rem', borderBottom: '1px solid var(--border-glass)', display: 'flex', alignItems: 'center', justifyContent: 'space-between', background: 'var(--bg-modal-header)' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
            <div style={{ padding: '0.6rem', borderRadius: '10px', backgroundColor: 'rgba(79, 70, 229, 0.15)', color: 'var(--accent-indigo)', display: 'flex' }}>
              <FolderPlus size={22} />
            </div>
            <div>
              <h2 style={{ fontSize: '1.25rem', fontWeight: 700, margin: 0, color: 'var(--text-main)' }}>Gestor Multi-Proyecto Datamart</h2>
              <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)', margin: 0 }}>
                {isMandatorySelection ? 'Debes seleccionar o crear un espacio de trabajo para iniciar' : 'Selecciona un espacio de trabajo o crea uno nuevo'}
              </p>
            </div>
          </div>

          {!isMandatorySelection && (
            <button onClick={onClose} style={{ background: 'none', border: 'none', color: 'var(--text-muted)', cursor: 'pointer', padding: '0.4rem', borderRadius: '8px' }}>
              <X size={20} />
            </button>
          )}
        </div>

        <div style={{ padding: '1.5rem', overflowY: 'auto', flex: 1 }}>
          {ctrl.showCreateForm ? (
            <CreateProjectForm
              newName={ctrl.newName}
              setNewName={ctrl.setNewName}
              newDesc={ctrl.newDesc}
              setNewDesc={ctrl.setNewDesc}
              newDomain={ctrl.newDomain}
              setNewDomain={ctrl.setNewDomain}
              onSubmit={ctrl.handleCreate}
              onCancel={() => ctrl.setShowCreateForm(false)}
              canCancel={ctrl.projects.length > 0}
            />
          ) : (
            <ProjectList
              projects={ctrl.projects}
              activeProject={activeProject}
              onSelectProject={onSelectProject}
              onDeleteProject={ctrl.handleDelete}
              onShowCreate={() => ctrl.setShowCreateForm(true)}
              onClose={onClose}
            />
          )}
        </div>
      </div>
    </div>
  );
};
