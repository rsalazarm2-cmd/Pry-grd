import React from 'react';
import { Calculator } from 'lucide-react';
import type { ColumnProfile, CalculatedFieldRule } from '../api/types';
import { useCalculatedFieldsController } from '../hooks/useCalculatedFieldsController';
import { CalculatedFieldsForm } from './CalculatedFieldsForm';
import { CalculatedFieldsRuleList } from './CalculatedFieldsRuleList';

interface CalculatedFieldsToolProps {
  columns: ColumnProfile[];
  calculatedFieldRules: CalculatedFieldRule[];
  onUpdateRules: React.Dispatch<React.SetStateAction<CalculatedFieldRule[]>>;
}

export const CalculatedFieldsTool: React.FC<CalculatedFieldsToolProps> = ({
  columns,
  calculatedFieldRules,
  onUpdateRules,
}) => {
  const ctrl = useCalculatedFieldsController(columns, calculatedFieldRules, onUpdateRules);

  return (
    <div style={{ border: '1px solid var(--border-glass)', borderRadius: '12px', backgroundColor: 'rgba(255,255,255,0.02)', padding: '1.25rem' }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginBottom: '1.25rem' }}>
        <div style={{ padding: '0.5rem', borderRadius: '8px', backgroundColor: 'rgba(16, 185, 129, 0.15)', color: 'var(--accent-emerald)' }}>
          <Calculator size={20} />
        </div>
        <div>
          <h4 style={{ fontSize: '1rem', fontWeight: 600, margin: 0, color: 'var(--text-main)' }}>Campos Calculados</h4>
          <p style={{ fontSize: '0.8rem', color: 'var(--text-muted)', margin: 0 }}>Crea columnas derivadas como días transcurridos, día de la semana, mes o año.</p>
        </div>
      </div>

      <CalculatedFieldsForm
        selectedFunc={ctrl.selectedFunc}
        colA={ctrl.colA}
        colB={ctrl.colB}
        resultName={ctrl.resultName}
        allColNames={ctrl.allColNames}
        funcConfig={ctrl.funcConfig}
        canAdd={ctrl.canAdd}
        onFuncChange={ctrl.handleFuncChange}
        onColAChange={ctrl.setColA}
        onColBChange={ctrl.setColB}
        onResultNameChange={ctrl.setResultName}
        onAddRule={ctrl.handleAddRule}
      />

      <CalculatedFieldsRuleList
        calculatedFieldRules={calculatedFieldRules}
        onRemoveRule={ctrl.handleRemoveRule}
      />
    </div>
  );
};
