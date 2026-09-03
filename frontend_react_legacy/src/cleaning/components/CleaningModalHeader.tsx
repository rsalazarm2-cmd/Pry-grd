import React from 'react';
import { Sliders, RotateCcw, Sparkles, X } from 'lucide-react';

interface CleaningModalHeaderProps {
  isAnyColumnIncluded: boolean;
  onToggleAutoConfig: () => void;
  onClose: () => void;
}

export const CleaningModalHeader: React.FC<CleaningModalHeaderProps> = ({
  isAnyColumnIncluded,
  onToggleAutoConfig,
  onClose,
}) => {
  return (
    <div style={{
      padding: '1.25rem 1.5rem',
      borderBottom: '1px solid var(--border-glass)',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'space-between',
      background: 'var(--bg-modal-header)',
    }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
        <div style={{ padding: '0.6rem', borderRadius: '10px', backgroundColor: 'rgba(79, 70, 229, 0.15)', color: 'var(--accent-indigo)', display: 'flex' }}>
          <Sliders size={22} />
        </div>
        <div>
          <h2 style={{ fontSize: '1.25rem', fontWeight: 700, margin: 0, color: 'var(--text-main)' }}>
            Configuración de Limpieza, Renombrado e Imputación
          </h2>
          <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)', margin: 0 }}>
            Ajusta las reglas de la Capa Plata y guarda tu receta reutilizable
          </p>
        </div>
      </div>

      <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
        <button
          onClick={onToggleAutoConfig}
          title={isAnyColumnIncluded ? 'Clic para desmarcar todas las columnas' : 'Clic para auto-configurar recomendados'}
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: '0.4rem',
            padding: '0.5rem 1rem',
            borderRadius: '8px',
            backgroundColor: isAnyColumnIncluded ? 'rgba(234, 179, 8, 0.15)' : 'rgba(99, 102, 241, 0.15)',
            border: isAnyColumnIncluded ? '1px solid rgba(245, 158, 11, 0.4)' : '1px solid rgba(99, 102, 241, 0.4)',
            color: isAnyColumnIncluded ? 'var(--accent-amber)' : 'var(--accent-indigo)',
            fontWeight: 700,
            fontSize: '0.82rem',
            cursor: 'pointer',
            transition: 'all 0.2s ease',
          }}
        >
          {isAnyColumnIncluded ? (
            <>
              <RotateCcw size={16} /> Auto-Configurado (Desmarcar Todo)
            </>
          ) : (
            <>
              <Sparkles size={16} /> Auto-Configurar Recomendados
            </>
          )}
        </button>
        <button onClick={onClose} style={{ background: 'none', border: 'none', color: 'var(--text-muted)', cursor: 'pointer' }}>
          <X size={20} />
        </button>
      </div>
    </div>
  );
};
