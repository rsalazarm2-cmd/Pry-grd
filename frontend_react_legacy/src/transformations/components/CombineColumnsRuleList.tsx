import React from 'react';
import { X, ArrowRight } from 'lucide-react';
import type { ColumnCombineRule } from '../api/types';
import { COMBINE_OPERATION_SYMBOLS } from '../config/transformationConfig';

interface CombineColumnsRuleListProps {
  combineRules: ColumnCombineRule[];
  onRemoveRule: (index: number) => void;
}

export const CombineColumnsRuleList: React.FC<CombineColumnsRuleListProps> = ({
  combineRules,
  onRemoveRule,
}) => {
  if (combineRules.length === 0) {
    return (
      <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)', fontStyle: 'italic', margin: 0 }}>
        No hay reglas de combinación configuradas.
      </p>
    );
  }

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
      {combineRules.map((rule, idx) => (
        <div key={idx} style={{ padding: '0.85rem 1rem', borderRadius: '8px', backgroundColor: 'rgba(99, 102, 241, 0.06)', border: '1px solid rgba(99, 102, 241, 0.2)', display: 'flex', alignItems: 'center', justifyContent: 'space-between', gap: '1rem' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.6rem', flexWrap: 'wrap' }}>
            <code style={{ color: 'var(--accent-cyan)', fontWeight: 700, fontSize: '0.85rem' }}>{rule.columns[0]}</code>
            <span style={{ fontWeight: 800, fontSize: '1.1rem', color: 'var(--accent-indigo)' }}>{COMBINE_OPERATION_SYMBOLS[rule.operation] || '?'}</span>
            <code style={{ color: 'var(--accent-cyan)', fontWeight: 700, fontSize: '0.85rem' }}>{rule.columns[1]}</code>
            <ArrowRight size={16} style={{ color: 'var(--text-muted)' }} />
            <code style={{ color: 'var(--accent-indigo)', fontWeight: 800, fontSize: '0.85rem', padding: '0.15rem 0.5rem', borderRadius: '4px', backgroundColor: 'rgba(99, 102, 241, 0.12)' }}>
              {rule.result_column}
            </code>
            {rule.drop_originals && (
              <span style={{ fontSize: '0.7rem', color: 'var(--accent-amber)', fontWeight: 600 }}>(descarta originales)</span>
            )}
          </div>
          <button onClick={() => onRemoveRule(idx)} style={{ background: 'none', border: 'none', color: 'var(--accent-rose)', cursor: 'pointer', display: 'flex' }} title="Eliminar regla">
            <X size={18} />
          </button>
        </div>
      ))}
    </div>
  );
};
