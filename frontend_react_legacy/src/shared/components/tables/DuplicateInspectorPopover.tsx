import React, { useState } from 'react';
import { Copy, AlertTriangle, CheckCircle2, ShieldAlert } from 'lucide-react';

interface DuplicateInspectorPopoverProps {
  dupIndex: number;
  matchedRow: number | string;
  matchedFields?: string[];
  reason?: string;
}

export const DuplicateInspectorPopover: React.FC<DuplicateInspectorPopoverProps> = ({
  dupIndex,
  matchedRow,
  matchedFields = ['FOLIO_ASIENTO', 'CARGO_MONEDA_FUNCIONAL', 'CUENTA_CONTABLE'],
  reason = 'Coincidencia 100% en monto y cuenta contable',
}) => {
  const [isOpen, setIsOpen] = useState(false);

  return (
    <div style={{ position: 'relative', display: 'inline-block' }}>
      <button
        onClick={() => setIsOpen(!isOpen)}
        onMouseEnter={() => setIsOpen(true)}
        onMouseLeave={() => setIsOpen(false)}
        style={{
          display: 'inline-flex',
          alignItems: 'center',
          gap: '0.3rem',
          padding: '0.2rem 0.55rem',
          borderRadius: '12px',
          backgroundColor: dupIndex > 1 ? 'rgba(239, 68, 68, 0.18)' : 'rgba(245, 158, 11, 0.18)',
          border: dupIndex > 1 ? '1px solid var(--accent-rose)' : '1px solid var(--accent-amber)',
          color: dupIndex > 1 ? 'var(--accent-rose)' : 'var(--accent-amber)',
          fontWeight: 700,
          fontSize: '0.72rem',
          cursor: 'pointer',
        }}
      >
        <Copy size={12} />
        <span>DUP #{dupIndex}</span>
      </button>

      {isOpen && (
        <div
          style={{
            position: 'absolute',
            bottom: '125%',
            left: '50%',
            transform: 'translateX(-50%)',
            width: '260px',
            padding: '0.85rem',
            borderRadius: '10px',
            backgroundColor: 'var(--bg-card)',
            border: '1px solid var(--accent-amber)',
            boxShadow: '0 10px 25px rgba(0,0,0,0.5)',
            zIndex: 9999,
            fontSize: '0.78rem',
            color: 'var(--text-main)',
          }}
        >
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem', fontWeight: 700, color: 'var(--accent-amber)', marginBottom: '0.5rem', borderBottom: '1px solid var(--border-glass)', paddingBottom: '0.4rem' }}>
            <ShieldAlert size={16} />
            <span>Inspector Forense de Duplicados</span>
          </div>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.35rem' }}>
            <div>
              <span style={{ color: 'var(--text-muted)' }}>Registro Original: </span>
              <strong style={{ color: 'var(--accent-cyan)' }}>Fila #{matchedRow}</strong>
            </div>

            <div>
              <span style={{ color: 'var(--text-muted)' }}>Campos Idénticos:</span>
              <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.2rem', marginTop: '0.2rem' }}>
                {matchedFields.map((f) => (
                  <span key={f} style={{ padding: '0.1rem 0.4rem', borderRadius: '4px', backgroundColor: 'rgba(56, 189, 248, 0.15)', color: 'var(--accent-cyan)', fontSize: '0.7rem', fontWeight: 600 }}>
                    {f}
                  </span>
                ))}
              </div>
            </div>

            <div style={{ marginTop: '0.3rem', fontSize: '0.73rem', color: 'var(--text-muted)', fontStyle: 'italic' }}>
              💡 {reason}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
