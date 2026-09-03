import React from 'react';
import { FolderPlus } from 'lucide-react';

interface EmptyProjectStateProps {
  onOpenProjectModal: () => void;
}

export const EmptyProjectState: React.FC<EmptyProjectStateProps> = ({ onOpenProjectModal }) => {
  return (
    <div className="glass-card" style={{ textAlign: 'center', padding: '4rem 2rem' }}>
      <div style={{
        width: '64px',
        height: '64px',
        borderRadius: '16px',
        backgroundColor: 'rgba(79, 70, 229, 0.15)',
        color: 'var(--accent-indigo)',
        display: 'inline-flex',
        alignItems: 'center',
        justifyContent: 'center',
        marginBottom: '1.2rem',
      }}>
        <FolderPlus size={32} />
      </div>
      <h3 style={{ fontSize: '1.4rem', fontWeight: 700, margin: '0 0 0.5rem 0', color: 'var(--text-main)' }}>
        Ningún Espacio de Trabajo Seleccionado
      </h3>
      <p style={{ fontSize: '0.95rem', color: 'var(--text-muted)', maxWidth: '500px', margin: '0 auto 1.5rem auto' }}>
        Para comenzar a procesar la analítica Medallion (Bronce, Plata, Oro), debes seleccionar un proyecto existente o crear uno nuevo.
      </p>
      <button
        onClick={onOpenProjectModal}
        className="btn-primary"
        style={{ padding: '0.75rem 1.8rem', fontSize: '0.95rem' }}
      >
        Abrir Gestor de Proyectos
      </button>
    </div>
  );
};
