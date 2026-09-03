import React from 'react';
import { Plus } from 'lucide-react';
import type { Project } from '../../shared/api/client';
import { ProjectCard } from './ProjectCard';

interface ProjectListProps {
  projects: Project[];
  activeProject: Project | null;
  onSelectProject: (project: Project | null) => void;
  onDeleteProject: (e: React.MouseEvent, projectId: string) => void;
  onShowCreate: () => void;
  onClose: () => void;
}

export const ProjectList: React.FC<ProjectListProps> = ({
  projects,
  activeProject,
  onSelectProject,
  onDeleteProject,
  onShowCreate,
  onClose,
}) => {
  return (
    <>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
        <span style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>
          {projects.length} Proyectos Registrados
        </span>
        <button
          onClick={onShowCreate}
          style={{
            display: 'flex', alignItems: 'center', gap: '0.4rem', padding: '0.5rem 1rem', borderRadius: '8px',
            backgroundColor: 'rgba(79, 70, 229, 0.15)', border: '1px solid rgba(129, 140, 248, 0.3)', color: 'var(--accent-indigo)',
            cursor: 'pointer', fontSize: '0.85rem', fontWeight: 600,
          }}
        >
          <Plus size={16} /> Crear Nuevo Proyecto
        </button>
      </div>

      <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
        {projects.map((proj) => (
          <ProjectCard
            key={proj.id}
            project={proj}
            isActive={activeProject?.id === proj.id}
            canDelete={true}
            onSelect={(p) => {
              onSelectProject(p);
              onClose();
            }}
            onDelete={onDeleteProject}
          />
        ))}
      </div>
    </>
  );
};
