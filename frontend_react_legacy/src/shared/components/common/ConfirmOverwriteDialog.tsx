import React from 'react';
import { AlertTriangle, X, ShieldAlert } from 'lucide-react';

interface ConfirmOverwriteDialogProps {
  isOpen: boolean;
  title?: string;
  message?: string;
  onConfirm: () => void;
  onCancel?: () => void;
  onClose?: () => void;
  isProcessing?: boolean;
  duplicateNamesList?: string[];
}

export const ConfirmOverwriteDialog: React.FC<ConfirmOverwriteDialogProps> = ({
  isOpen,
  title = "¿Sobrescribir Capa Plata?",
  message = "Esta acción generará un nuevo archivo silver.parquet a partir de las reglas de limpieza seleccionadas.",
  onConfirm,
  onCancel,
  onClose,
  isProcessing = false,
}) => {
  if (!isOpen) return null;

  const handleClose = onCancel || onClose || (() => {});

  return (
    <div style={{
      position: 'fixed',
      top: 0, left: 0, right: 0, bottom: 0,
      backgroundColor: 'var(--bg-modal-overlay)',
      backdropFilter: 'blur(8px)',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      zIndex: 9999,
      padding: '1rem',
    }}>
      <div style={{
        maxWidth: '460px',
        width: '100%',
        margin: '20px',
        border: '1px solid var(--accent-rose)',
        backgroundColor: 'var(--bg-modal-card)',
        borderRadius: '16px',
        padding: '1.5rem',
        boxShadow: 'var(--card-shadow)',
        animation: 'fadeIn 0.2s ease-out'
      }}>
        <div style={{ display: 'flex', alignItems: 'flex-start', gap: '1rem', marginBottom: '1.25rem' }}>
          <div style={{
            padding: '0.75rem',
            borderRadius: '50%',
            backgroundColor: 'rgba(244, 63, 94, 0.15)',
            color: 'var(--accent-rose)',
            flexShrink: 0,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center'
          }}>
            <AlertTriangle size={26} />
          </div>
          <div style={{ flex: 1 }}>
            <h3 style={{ margin: '0 0 0.5rem 0', fontSize: '1.25rem', fontWeight: 700, color: 'var(--text-main)' }}>
              {title}
            </h3>
            <p style={{ margin: 0, color: 'var(--text-muted)', fontSize: '0.925rem', lineHeight: '1.5' }}>
              {message}
            </p>
          </div>
          <button 
            onClick={handleClose}
            disabled={isProcessing}
            style={{ 
              background: 'none', 
              border: 'none', 
              color: 'var(--text-muted)', 
              cursor: 'pointer',
              padding: '0.25rem',
              borderRadius: '6px',
              display: 'flex',
              alignItems: 'center'
            }}
          >
            <X size={20} />
          </button>
        </div>

        <div style={{
          backgroundColor: 'rgba(244, 63, 94, 0.08)',
          padding: '1rem',
          borderRadius: '10px',
          border: '1px dashed var(--accent-rose)',
          marginBottom: '1.5rem',
          display: 'flex',
          gap: '0.75rem',
          alignItems: 'flex-start'
        }}>
          <ShieldAlert size={20} style={{ color: 'var(--accent-rose)', flexShrink: 0, marginTop: '2px' }} />
          <span style={{ fontSize: '0.875rem', color: 'var(--text-main)', lineHeight: '1.45' }}>
            <strong style={{ color: 'var(--accent-rose)' }}>Advertencia:</strong> Esta acción sobrescribirá cualquier archivo anterior y los cambios en la siguiente capa podrían requerir reprocesamiento.
          </span>
        </div>

        <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '0.75rem' }}>
          <button
            onClick={handleClose}
            disabled={isProcessing}
            style={{
              padding: '0.6rem 1.25rem',
              borderRadius: '8px',
              border: '1px solid var(--border-glass)',
              backgroundColor: 'var(--bg-input)',
              color: 'var(--text-main)',
              fontWeight: 600,
              fontSize: '0.88rem',
              cursor: 'pointer'
            }}
          >
            Cancelar
          </button>
          <button
            onClick={onConfirm}
            disabled={isProcessing}
            style={{
              padding: '0.6rem 1.25rem',
              borderRadius: '8px',
              border: 'none',
              background: 'linear-gradient(135deg, var(--accent-rose), #e11d48)',
              color: '#ffffff',
              fontWeight: 600,
              fontSize: '0.88rem',
              cursor: isProcessing ? 'not-allowed' : 'pointer',
              opacity: isProcessing ? 0.7 : 1,
              display: 'flex',
              alignItems: 'center',
              gap: '0.5rem'
            }}
          >
            {isProcessing ? 'Procesando...' : 'Sí, Sobrescribir'}
          </button>
        </div>
      </div>
    </div>
  );
};

