import { useState } from 'react';
import type { ColumnProfile, ColumnCombineRule } from '../api/types';

export const useCombineColumnsController = (
  columns: ColumnProfile[],
  onUpdateRules: React.Dispatch<React.SetStateAction<ColumnCombineRule[]>>
) => {
  const [colA, setColA] = useState('');
  const [colB, setColB] = useState('');
  const [operation, setOperation] = useState<string>('SUBTRACT');
  const [resultName, setResultName] = useState('');
  const [dropOriginals, setDropOriginals] = useState(false);
  const [separator, setSeparator] = useState(' - ');

  const allColNames = columns.map((c) => c.column_name);

  const handleAddRule = () => {
    if (!colA || !colB || !resultName.trim()) return;
    if (colA === colB) return;

    const newRule: ColumnCombineRule = {
      enabled: true,
      columns: [colA, colB],
      operation: operation as ColumnCombineRule['operation'],
      result_column: resultName.trim().toUpperCase(),
      separator,
      drop_originals: dropOriginals,
    };

    onUpdateRules((prev) => [...prev, newRule]);
    setColA('');
    setColB('');
    setResultName('');
  };

  const handleRemoveRule = (index: number) => {
    onUpdateRules((prev) => prev.filter((_, i) => i !== index));
  };

  const canAdd = Boolean(colA && colB && resultName.trim() && colA !== colB);

  return {
    colA,
    colB,
    operation,
    resultName,
    dropOriginals,
    separator,
    allColNames,
    canAdd,
    setColA,
    setColB,
    setOperation,
    setResultName,
    setDropOriginals,
    setSeparator,
    handleAddRule,
    handleRemoveRule,
  };
};
