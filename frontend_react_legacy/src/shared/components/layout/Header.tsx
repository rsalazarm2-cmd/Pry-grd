import React from 'react';
import { Database, Sun, Moon } from 'lucide-react';
import type { Project } from '../../api/types';

interface HeaderProps {
  activeProject: Project | null;
  onOpenProjectModal: () => void;
  themeMode: 'dark' | 'light';
  onToggleTheme: () => void;
}

export const Header: React.FC<HeaderProps> = ({
  activeProject,
  onOpenProjectModal,
  themeMode,
  onToggleTheme,
}) => {
  return (
    <header className="app-header">
      <div className="brand">
        <img
          src="/assets/modern_logo_icon.png"
          alt="Medallion Master Emblem"
          style={{ width: 44, height: 44, borderRadius: 12, objectFit: 'cover', boxShadow: '0 0 20px rgba(56, 189, 248, 0.4)' }}
        />
        <div>
          <h1 className="brand-title">Medallion Analytics Master Suite</h1>
          <p className="brand-subtitle">Plataforma Empresarial de Toma de Decisiones y Control de Datos</p>
        </div>
      </div>

      <div style={{ display: 'flex', alignItems: 'center', gap: '0.8rem' }}>
        <button
          onClick={onOpenProjectModal}
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: '0.5rem',
            padding: '0.5rem 1rem',
            borderRadius: '10px',
            backgroundColor: 'rgba(79, 70, 229, 0.15)',
            border: '1px solid rgba(129, 140, 248, 0.4)',
            color: 'var(--accent-indigo)',
            fontWeight: 700,
            fontSize: '0.85rem',
            cursor: 'pointer',
            boxShadow: '0 2px 10px rgba(79, 70, 229, 0.15)',
          }}
        >
          <Database size={16} />
          <span>Proyecto: {activeProject?.name || 'Proyecto Principal'}</span>
          {activeProject?.has_recipe && (
            <span style={{ fontSize: '0.65rem', padding: '0.1rem 0.4rem', borderRadius: '8px', backgroundColor: 'rgba(245, 158, 11, 0.2)', color: 'var(--accent-amber)' }}>
              ⚡ RECETA
            </span>
          )}
        </button>

        <button
          onClick={onToggleTheme}
          className="btn-primary"
          style={{
            background: themeMode === 'dark' ? 'rgba(30, 41, 59, 0.8)' : '#ffffff',
            color: themeMode === 'dark' ? '#f8fafc' : '#0f172a',
            border: `1px solid ${themeMode === 'dark' ? 'var(--border-glass)' : '#cbd5e1'}`,
            boxShadow: '0 2px 8px rgba(0,0,0,0.08)',
            padding: '0.5rem 1rem',
            fontSize: '0.85rem',
            fontWeight: 700,
          }}
        >
          {themeMode === 'dark' ? (
            <>
              <Sun size={15} style={{ color: '#f59e0b' }} /> Modo Claro
            </>
          ) : (
            <>
              <Moon size={15} style={{ color: '#4f46e5' }} /> Modo Oscuro
            </>
          )}
        </button>
      </div>
    </header>
  );
};
