import React from 'react';
import { FileSpreadsheet, CheckCircle2, Sparkles, Trash2 } from 'lucide-react';
import type { Project } from '../../api/types';

interface ProjectCardProps {
  project: Project;
  isActive: boolean;
  canDelete: boolean;
  onSelect: (project: Project) => void;
  onDelete: (e: React.MouseEvent, projectId: string) => void;
}

export const ProjectCard: React.FC<ProjectCardProps> = ({
  project,
  isActive,
  canDelete,
  onSelect,
  onDelete,
}) => {
  return (
    <div
      onClick={() => onSelect(project)}
      style={{
        padding: '1rem 1.25rem',
        borderRadius: '12px',
        border: isActive ? '2px solid var(--accent-indigo)' : '1px solid var(--border-glass)',
        backgroundColor: isActive ? 'rgba(79, 70, 229, 0.1)' : 'var(--bg-card)',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        cursor: 'pointer',
        transition: 'all 0.2s ease',
      }}
    >
      <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
        <div style={{
          padding: '0.6rem',
          borderRadius: '10px',
          backgroundColor: isActive ? 'rgba(99, 102, 241, 0.2)' : 'rgba(148, 163, 184, 0.1)',
          color: isActive ? 'var(--accent-indigo)' : 'var(--text-muted)',
          display: 'flex',
        }}>
          <FileSpreadsheet size={20} />
        </div>

        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.6rem' }}>
            <span style={{ fontWeight: 700, fontSize: '0.95rem', color: 'var(--text-main)' }}>
              {project.name}
            </span>
            {isActive && (
              <span style={{
                fontSize: '0.7rem',
                padding: '0.15rem 0.5rem',
                borderRadius: '12px',
                backgroundColor: 'rgba(16, 185, 129, 0.15)',
                color: 'var(--accent-emerald)',
                border: '1px solid rgba(16, 185, 129, 0.3)',
                display: 'flex',
                alignItems: 'center',
                gap: '0.2rem',
              }}>
                <CheckCircle2 size={12} /> ACTIVO
              </span>
            )}
            {project.has_recipe && (
              <span style={{
                fontSize: '0.7rem',
                padding: '0.15rem 0.5rem',
                borderRadius: '12px',
                backgroundColor: 'rgba(245, 158, 11, 0.15)',
                color: 'var(--accent-amber)',
                border: '1px solid rgba(245, 158, 11, 0.3)',
                display: 'flex',
                alignItems: 'center',
                gap: '0.2rem',
              }} title="Receta de Limpieza Persistente Activa">
                <Sparkles size={12} /> RECETA REUTILIZABLE
              </span>
            )}
          </div>
          <p style={{ fontSize: '0.8rem', color: 'var(--text-muted)', margin: '0.25rem 0 0 0' }}>
            {project.description || 'Sin descripción'} • Dominio: {project.domain}
          </p>
        </div>
      </div>

      <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
        {canDelete && (
          <button
            onClick={(e) => onDelete(e, project.id)}
            title="Eliminar proyecto"
            style={{
              background: 'none',
              border: 'none',
              color: 'var(--accent-rose)',
              cursor: 'pointer',
              padding: '0.4rem',
              borderRadius: '6px',
            }}
          >
            <Trash2 size={18} />
          </button>
        )}
      </div>
    </div>
  );
};
