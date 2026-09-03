import React from 'react';
import { AlertTriangle, Loader2 } from 'lucide-react';

interface CleaningModalFooterProps {
  hasDuplicateNames: boolean;
  isTransforming: boolean;
  onClose: () => void;
  onSaveAndProcess: () => void;
}

export const CleaningModalFooter: React.FC<CleaningModalFooterProps> = ({
  hasDuplicateNames,
  isTransforming,
  onClose,
  onSaveAndProcess,
}) => {
  return (
    <div style={{
      padding: '1rem 1.5rem',
      borderTop: '1px solid var(--border-glass)',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'space-between',
      backgroundColor: 'var(--bg-modal-footer)',
    }}>
      {hasDuplicateNames ? (
        <span style={{ fontSize: '0.85rem', color: 'var(--accent-rose)', fontWeight: 700, display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
          <AlertTriangle size={18} /> Revisa la tabla: existen alias duplicados.
        </span>
      ) : (
        <span style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>
          Se guardará la receta en <code style={{ color: 'var(--accent-indigo)' }}>recipe.json</code> para cargas automáticas futuras
        </span>
      )}

      <div style={{ display: 'flex', gap: '0.75rem' }}>
        <button
          onClick={onClose}
          disabled={isTransforming}
          style={{
            padding: '0.6rem 1.25rem',
            borderRadius: '8px',
            border: '1px solid var(--border-glass)',
            background: 'transparent',
            color: 'var(--text-muted)',
            cursor: isTransforming ? 'not-allowed' : 'pointer',
          }}
        >
          Cancelar
        </button>
        <button
          onClick={onSaveAndProcess}
          disabled={hasDuplicateNames || isTransforming}
          style={{
            padding: '0.6rem 1.25rem',
            borderRadius: '8px',
            border: 'none',
            background: (hasDuplicateNames || isTransforming) ? 'gray' : 'linear-gradient(135deg, var(--accent-indigo), var(--accent-purple))',
            color: 'white',
            fontWeight: 700,
            cursor: (hasDuplicateNames || isTransforming) ? 'not-allowed' : 'pointer',
            display: 'flex',
            alignItems: 'center',
            gap: '0.5rem',
          }}
        >
          {isTransforming ? (
            <>
              <Loader2 size={16} className="spin" /> Procesando Capa Plata...
            </>
          ) : (
            'Guardar y Procesar Capa Plata'
          )}
        </button>
      </div>
    </div>
  );
};
