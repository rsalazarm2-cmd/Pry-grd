import React from 'react';
import { Plus } from 'lucide-react';
import { CALCULATED_FUNCTIONS } from '../config/transformationConfig';

interface CalculatedFieldsFormProps {
  selectedFunc: string;
  colA: string;
  colB: string;
  resultName: string;
  allColNames: string[];
  funcConfig: any;
  canAdd: boolean;
  onFuncChange: (val: string) => void;
  onColAChange: (val: string) => void;
  onColBChange: (val: string) => void;
  onResultNameChange: (val: string) => void;
  onAddRule: () => void;
}

export const CalculatedFieldsForm: React.FC<CalculatedFieldsFormProps> = ({
  selectedFunc,
  colA,
  colB,
  resultName,
  allColNames,
  funcConfig,
  canAdd,
  onFuncChange,
  onColAChange,
  onColBChange,
  onResultNameChange,
  onAddRule,
}) => {
  return (
    <>
      <div style={{ display: 'flex', gap: '0.75rem', alignItems: 'flex-end', flexWrap: 'wrap', marginBottom: '1.5rem', paddingBottom: '1.5rem', borderBottom: '1px solid var(--border-glass)' }}>
        <div style={{ flex: 1, minWidth: '200px' }}>
          <label style={{ display: 'block', fontSize: '0.78rem', marginBottom: '0.3rem', color: 'var(--text-muted)', fontWeight: 600 }}>Función</label>
          <select value={selectedFunc} onChange={(e) => onFuncChange(e.target.value)} style={{ width: '100%', padding: '0.45rem', borderRadius: '6px', border: '1px solid var(--border-glass)', background: 'var(--bg-card)', color: 'var(--accent-emerald)', fontWeight: 600, fontSize: '0.82rem' }}>
            <option value="">-- Seleccionar Función --</option>
            {CALCULATED_FUNCTIONS.map((f) => (
              <option key={f.value} value={f.value}>{f.label}</option>
            ))}
          </select>
        </div>

        {funcConfig && (
          <>
            <div style={{ flex: 1, minWidth: '160px' }}>
              <label style={{ display: 'block', fontSize: '0.78rem', marginBottom: '0.3rem', color: 'var(--text-muted)', fontWeight: 600 }}>{funcConfig.colLabel[0]}</label>
              <select value={colA} onChange={(e) => onColAChange(e.target.value)} style={{ width: '100%', padding: '0.45rem', borderRadius: '6px', border: '1px solid var(--border-glass)', background: 'var(--bg-card)', color: 'var(--text-main)', fontSize: '0.82rem' }}>
                <option value="">-- Seleccionar --</option>
                {allColNames.map((n) => (
                  <option key={`ca-${n}`} value={n}>{n}</option>
                ))}
              </select>
            </div>

            {funcConfig.requiredCols >= 2 && (
              <div style={{ flex: 1, minWidth: '160px' }}>
                <label style={{ display: 'block', fontSize: '0.78rem', marginBottom: '0.3rem', color: 'var(--text-muted)', fontWeight: 600 }}>{funcConfig.colLabel[1]}</label>
                <select value={colB} onChange={(e) => onColBChange(e.target.value)} style={{ width: '100%', padding: '0.45rem', borderRadius: '6px', border: '1px solid var(--border-glass)', background: 'var(--bg-card)', color: 'var(--text-main)', fontSize: '0.82rem' }}>
                  <option value="">-- Seleccionar --</option>
                  {allColNames.map((n) => (
                    <option key={`cb-${n}`} value={n}>{n}</option>
                  ))}
                </select>
              </div>
            )}

            <div style={{ width: '180px' }}>
              <label style={{ display: 'block', fontSize: '0.78rem', marginBottom: '0.3rem', color: 'var(--text-muted)', fontWeight: 600 }}>Columna Resultante</label>
              <input type="text" value={resultName} onChange={(e) => onResultNameChange(e.target.value)} style={{ width: '100%', padding: '0.45rem', borderRadius: '6px', border: '1px solid var(--accent-emerald)', background: 'rgba(16, 185, 129, 0.05)', color: 'white', fontSize: '0.82rem', boxSizing: 'border-box' }} />
            </div>
          </>
        )}

        <button onClick={onAddRule} disabled={!canAdd} style={{ padding: '0.45rem 1rem', borderRadius: '6px', border: 'none', background: 'linear-gradient(135deg, var(--accent-emerald), var(--accent-teal, #14b8a6))', color: 'white', fontWeight: 600, cursor: !canAdd ? 'not-allowed' : 'pointer', opacity: !canAdd ? 0.5 : 1, display: 'flex', alignItems: 'center', gap: '0.4rem', fontSize: '0.82rem', whiteSpace: 'nowrap' }}>
          <Plus size={16} /> Añadir
        </button>
      </div>

      {funcConfig && (
        <div style={{ padding: '0.6rem 0.9rem', borderRadius: '6px', backgroundColor: 'rgba(16, 185, 129, 0.06)', border: '1px solid rgba(16, 185, 129, 0.15)', marginBottom: '1rem', fontSize: '0.8rem', color: 'var(--text-muted)' }}>
          💡 {funcConfig.description}
          <span style={{ marginLeft: '0.5rem', color: 'var(--accent-emerald)', fontWeight: 600 }}>→ Tipo resultado: {funcConfig.resultType}</span>
        </div>
      )}
    </>
  );
};
