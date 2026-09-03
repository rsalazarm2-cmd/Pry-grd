import React from 'react';
import { Settings2, X, ArrowRight } from 'lucide-react';
import type { ColumnSplitRule } from '../../api/atomicityApi';

interface AtomizeRuleListProps {
  splitRules: ColumnSplitRule[];
  onRemoveRule: (colName: string) => void;
  onUpdateSegment: (colName: string, index: number, newAlias: string) => void;
}

export const AtomizeRuleList: React.FC<AtomizeRuleListProps> = ({
  splitRules,
  onRemoveRule,
  onUpdateSegment,
}) => {
  if (splitRules.length === 0) {
    return (
      <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)', fontStyle: 'italic', margin: 0 }}>
        No hay reglas de atomización configuradas.
      </p>
    );
  }

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
      {splitRules.map((rule) => (
        <div key={rule.column_name} style={{ padding: '1rem', borderRadius: '8px', backgroundColor: 'rgba(255,255,255,0.03)', border: '1px solid var(--border-glass)' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', fontWeight: 600, color: 'var(--accent-cyan)' }}>
              <Settings2 size={16} />
              <span>{rule.column_name}</span>
              <span style={{ color: 'var(--text-muted)', fontSize: '0.8rem', fontWeight: 400 }}>
                (Delimitador: <code>"{rule.delimiter}"</code>)
              </span>
            </div>
            <button onClick={() => onRemoveRule(rule.column_name)} style={{ background: 'none', border: 'none', color: 'var(--accent-rose)', cursor: 'pointer', display: 'flex' }} title="Eliminar regla">
              <X size={18} />
            </button>
          </div>

          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', flexWrap: 'wrap' }}>
            <div style={{ padding: '0.4rem 0.8rem', borderRadius: '4px', backgroundColor: 'var(--bg-body)', fontSize: '0.8rem', border: '1px dashed var(--border-glass)' }}>
              {rule.column_name}
            </div>
            <ArrowRight size={16} style={{ color: 'var(--text-muted)' }} />

            {rule.segments.map((seg) => (
              <div key={seg.index} style={{ display: 'flex', flexDirection: 'column', gap: '0.3rem' }}>
                <label style={{ fontSize: '0.7rem', color: 'var(--text-muted)', textAlign: 'center' }}>Parte {seg.index + 1}</label>
                <input
                  type="text"
                  value={seg.suggested_alias}
                  onChange={(e) => onUpdateSegment(rule.column_name, seg.index, e.target.value)}
                  style={{ padding: '0.3rem 0.6rem', borderRadius: '4px', border: '1px solid var(--accent-cyan)', background: 'rgba(56, 189, 248, 0.05)', color: 'white', fontSize: '0.8rem', width: '120px', textAlign: 'center' }}
                />
              </div>
            ))}
          </div>
        </div>
      ))}
    </div>
  );
};
