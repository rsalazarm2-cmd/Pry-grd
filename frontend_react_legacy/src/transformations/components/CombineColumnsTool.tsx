import React from 'react';
import { Combine } from 'lucide-react';
import type { ColumnProfile, ColumnCombineRule } from '../api/types';
import { useCombineColumnsController } from '../hooks/useCombineColumnsController';
import { CombineColumnsForm } from './CombineColumnsForm';
import { CombineColumnsRuleList } from './CombineColumnsRuleList';

interface CombineColumnsToolProps {
  columns: ColumnProfile[];
  combineRules: ColumnCombineRule[];
  onUpdateRules: React.Dispatch<React.SetStateAction<ColumnCombineRule[]>>;
}

export const CombineColumnsTool: React.FC<CombineColumnsToolProps> = ({
  columns,
  combineRules,
  onUpdateRules,
}) => {
  const ctrl = useCombineColumnsController(columns, onUpdateRules);

  return (
    <div style={{ border: '1px solid var(--border-glass)', borderRadius: '12px', backgroundColor: 'rgba(255,255,255,0.02)', padding: '1.25rem' }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginBottom: '1.25rem' }}>
        <div style={{ padding: '0.5rem', borderRadius: '8px', backgroundColor: 'rgba(99, 102, 241, 0.15)', color: 'var(--accent-indigo)' }}>
          <Combine size={20} />
        </div>
        <div>
          <h4 style={{ fontSize: '1rem', fontWeight: 600, margin: 0, color: 'var(--text-main)' }}>Combinar Columnas</h4>
          <p style={{ fontSize: '0.8rem', color: 'var(--text-muted)', margin: 0 }}>Fusiona dos columnas con operaciones aritméticas o concatenación.</p>
        </div>
      </div>

      <CombineColumnsForm
        colA={ctrl.colA}
        colB={ctrl.colB}
        operation={ctrl.operation}
        resultName={ctrl.resultName}
        separator={ctrl.separator}
        allColNames={ctrl.allColNames}
        canAdd={ctrl.canAdd}
        onColAChange={ctrl.setColA}
        onColBChange={ctrl.setColB}
        onOperationChange={ctrl.setOperation}
        onResultNameChange={ctrl.setResultName}
        onSeparatorChange={ctrl.setSeparator}
        onAddRule={ctrl.handleAddRule}
      />

      <CombineColumnsRuleList
        combineRules={combineRules}
        onRemoveRule={ctrl.handleRemoveRule}
      />
    </div>
  );
};
