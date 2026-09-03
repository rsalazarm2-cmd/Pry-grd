import React from 'react';
import { Plus } from 'lucide-react';
import { COMBINE_OPERATIONS } from '../config/transformationConfig';

interface CombineColumnsFormProps {
  colA: string;
  colB: string;
  operation: string;
  resultName: string;
  separator: string;
  allColNames: string[];
  canAdd: boolean;
  onColAChange: (val: string) => void;
  onColBChange: (val: string) => void;
  onOperationChange: (val: string) => void;
  onResultNameChange: (val: string) => void;
  onSeparatorChange: (val: string) => void;
  onAddRule: () => void;
}

export const CombineColumnsForm: React.FC<CombineColumnsFormProps> = ({
  colA,
  colB,
  operation,
  resultName,
  separator,
  allColNames,
  canAdd,
  onColAChange,
  onColBChange,
  onOperationChange,
  onResultNameChange,
  onSeparatorChange,
  onAddRule,
}) => {
  return (
    <div style={{ display: 'flex', gap: '0.75rem', alignItems: 'flex-end', flexWrap: 'wrap', marginBottom: '1.5rem', paddingBottom: '1.5rem', borderBottom: '1px solid var(--border-glass)' }}>
      <div style={{ flex: 1, minWidth: '160px' }}>
        <label style={{ display: 'block', fontSize: '0.78rem', marginBottom: '0.3rem', color: 'var(--text-muted)', fontWeight: 600 }}>Columna A</label>
        <select value={colA} onChange={(e) => onColAChange(e.target.value)} style={{ width: '100%', padding: '0.45rem', borderRadius: '6px', border: '1px solid var(--border-glass)', background: 'var(--bg-card)', color: 'var(--text-main)', fontSize: '0.82rem' }}>
          <option value="">-- Seleccionar --</option>
          {allColNames.map((n) => (
            <option key={`a-${n}`} value={n}>{n}</option>
          ))}
        </select>
      </div>

      <div style={{ width: '180px' }}>
        <label style={{ display: 'block', fontSize: '0.78rem', marginBottom: '0.3rem', color: 'var(--text-muted)', fontWeight: 600 }}>Operación</label>
        <select value={operation} onChange={(e) => onOperationChange(e.target.value)} style={{ width: '100%', padding: '0.45rem', borderRadius: '6px', border: '1px solid var(--border-glass)', background: 'var(--bg-card)', color: 'var(--accent-indigo)', fontWeight: 600, fontSize: '0.82rem' }}>
          {COMBINE_OPERATIONS.map((op) => (
            <option key={op.value} value={op.value}>{op.label}</option>
          ))}
        </select>
      </div>

      <div style={{ flex: 1, minWidth: '160px' }}>
        <label style={{ display: 'block', fontSize: '0.78rem', marginBottom: '0.3rem', color: 'var(--text-muted)', fontWeight: 600 }}>Columna B</label>
        <select value={colB} onChange={(e) => onColBChange(e.target.value)} style={{ width: '100%', padding: '0.45rem', borderRadius: '6px', border: '1px solid var(--border-glass)', background: 'var(--bg-card)', color: 'var(--text-main)', fontSize: '0.82rem' }}>
          <option value="">-- Seleccionar --</option>
          {allColNames.map((n) => (
            <option key={`b-${n}`} value={n}>{n}</option>
          ))}
        </select>
      </div>

      <div style={{ width: '160px' }}>
        <label style={{ display: 'block', fontSize: '0.78rem', marginBottom: '0.3rem', color: 'var(--text-muted)', fontWeight: 600 }}>Columna Resultante</label>
        <input type="text" value={resultName} onChange={(e) => onResultNameChange(e.target.value)} placeholder="Ej: MONTO_NETO" style={{ width: '100%', padding: '0.45rem', borderRadius: '6px', border: '1px solid var(--accent-indigo)', background: 'rgba(99, 102, 241, 0.05)', color: 'white', fontSize: '0.82rem', boxSizing: 'border-box' }} />
      </div>

      {operation === 'CONCAT' && (
        <div style={{ width: '100px' }}>
          <label style={{ display: 'block', fontSize: '0.78rem', marginBottom: '0.3rem', color: 'var(--text-muted)', fontWeight: 600 }}>Separador</label>
          <input type="text" value={separator} onChange={(e) => onSeparatorChange(e.target.value)} style={{ width: '100%', padding: '0.45rem', borderRadius: '6px', border: '1px solid var(--border-glass)', background: 'var(--bg-card)', color: 'white', fontSize: '0.82rem', textAlign: 'center', boxSizing: 'border-box' }} />
        </div>
      )}

      <button onClick={onAddRule} disabled={!canAdd} style={{ padding: '0.45rem 1rem', borderRadius: '6px', border: 'none', background: 'linear-gradient(135deg, var(--accent-indigo), var(--accent-purple))', color: 'white', fontWeight: 600, cursor: !canAdd ? 'not-allowed' : 'pointer', opacity: !canAdd ? 0.5 : 1, display: 'flex', alignItems: 'center', gap: '0.4rem', fontSize: '0.82rem', whiteSpace: 'nowrap' }}>
        <Plus size={16} /> Añadir
      </button>
    </div>
  );
};
