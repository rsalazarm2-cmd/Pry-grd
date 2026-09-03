import { useState } from 'react';
import type { ColumnProfile, CalculatedFieldRule } from '../api/types';
import { CALCULATED_FUNCTIONS } from '../config/transformationConfig';

export const useCalculatedFieldsController = (
  columns: ColumnProfile[],
  calculatedFieldRules: CalculatedFieldRule[],
  onUpdateRules: React.Dispatch<React.SetStateAction<CalculatedFieldRule[]>>
) => {
  const [selectedFunc, setSelectedFunc] = useState('');
  const [colA, setColA] = useState('');
  const [colB, setColB] = useState('');
  const [resultName, setResultName] = useState('');

  const allColNames = columns.map((c) => c.column_name);
  const funcConfig = CALCULATED_FUNCTIONS.find((f) => f.value === selectedFunc);

  const handleFuncChange = (value: string) => {
    setSelectedFunc(value);
    setColA('');
    setColB('');
    const config = CALCULATED_FUNCTIONS.find((f) => f.value === value);
    if (config) {
      setResultName(config.defaultAlias);
    }
  };

  const handleAddRule = () => {
    if (!funcConfig || !colA || !resultName.trim()) return;
    if (funcConfig.requiredCols >= 2 && !colB) return;

    const sourceCols = funcConfig.requiredCols >= 2 ? [colA, colB] : [colA];

    const newRule: CalculatedFieldRule = {
      enabled: true,
      function_name: funcConfig.value as CalculatedFieldRule['function_name'],
      source_columns: sourceCols,
      result_column: resultName.trim().toUpperCase(),
      result_type: funcConfig.resultType,
    };

    onUpdateRules((prev) => [...prev, newRule]);
    setSelectedFunc('');
    setColA('');
    setColB('');
    setResultName('');
  };

  const handleRemoveRule = (index: number) => {
    onUpdateRules((prev) => prev.filter((_, i) => i !== index));
  };

  const canAdd = Boolean(
    selectedFunc && colA && resultName.trim() && (funcConfig?.requiredCols === 1 || colB)
  );

  return {
    selectedFunc,
    colA,
    colB,
    resultName,
    allColNames,
    funcConfig,
    canAdd,
    setColA,
    setColB,
    setResultName,
    handleFuncChange,
    handleAddRule,
    handleRemoveRule,
  };
};
