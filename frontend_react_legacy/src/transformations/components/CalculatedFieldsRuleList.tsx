import React from 'react';
import { X, ArrowRight } from 'lucide-react';
import type { CalculatedFieldRule } from '../api/types';
import { CALCULATED_FUNCTIONS, CALCULATED_FUNC_ICONS } from '../config/transformationConfig';

interface CalculatedFieldsRuleListProps {
  calculatedFieldRules: CalculatedFieldRule[];
  onRemoveRule: (index: number) => void;
}

export const CalculatedFieldsRuleList: React.FC<CalculatedFieldsRuleListProps> = ({
  calculatedFieldRules,
  onRemoveRule,
}) => {
  if (calculatedFieldRules.length === 0) {
    return (
      <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)', fontStyle: 'italic', margin: 0 }}>
        No hay campos calculados configurados.
      </p>
    );
  }

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
      {calculatedFieldRules.map((rule, idx) => {
        const icon = CALCULATED_FUNC_ICONS[rule.function_name] || '🔧';
        const funcLabel = CALCULATED_FUNCTIONS.find((f) => f.value === rule.function_name)?.label || rule.function_name;

        return (
          <div key={idx} style={{ padding: '0.85rem 1rem', borderRadius: '8px', backgroundColor: 'rgba(16, 185, 129, 0.06)', border: '1px solid rgba(16, 185, 129, 0.2)', display: 'flex', alignItems: 'center', justifyContent: 'space-between', gap: '1rem' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.6rem', flexWrap: 'wrap' }}>
              <span style={{ fontSize: '1.1rem' }}>{icon}</span>
              <span style={{ fontSize: '0.82rem', color: 'var(--text-muted)', fontWeight: 600 }}>{funcLabel.replace(/^[^\s]+\s/, '')}</span>
              <span style={{ fontSize: '0.78rem', color: 'var(--text-muted)' }}>(</span>
              {rule.source_columns.map((sc, si) => (
                <React.Fragment key={si}>
                  {si > 0 && <span style={{ color: 'var(--text-muted)', fontSize: '0.78rem' }}>,</span>}
                  <code style={{ color: 'var(--accent-cyan)', fontWeight: 700, fontSize: '0.83rem' }}>{sc}</code>
                </React.Fragment>
              ))}
              <span style={{ fontSize: '0.78rem', color: 'var(--text-muted)' }}>)</span>
              <ArrowRight size={16} style={{ color: 'var(--text-muted)' }} />
              <code style={{ color: 'var(--accent-emerald)', fontWeight: 800, fontSize: '0.85rem', padding: '0.15rem 0.5rem', borderRadius: '4px', backgroundColor: 'rgba(16, 185, 129, 0.12)' }}>
                {rule.result_column}
              </code>
              <span style={{ fontSize: '0.7rem', color: 'var(--text-muted)', backgroundColor: 'rgba(148, 163, 184, 0.12)', padding: '0.1rem 0.35rem', borderRadius: '3px' }}>
                {rule.result_type}
              </span>
            </div>
            <button onClick={() => onRemoveRule(idx)} style={{ background: 'none', border: 'none', color: 'var(--accent-rose)', cursor: 'pointer', display: 'flex' }} title="Eliminar campo calculado">
              <X size={18} />
            </button>
          </div>
        );
      })}
    </div>
  );
};
