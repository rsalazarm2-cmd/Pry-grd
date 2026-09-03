import { useState } from 'react';
import type { ColumnProfile } from '../../api/types';
import type { ColumnSplitRule, SegmentDefinition } from '../../api/atomicityApi';

export const useAtomizeToolController = (
  columns: ColumnProfile[],
  splitRules: ColumnSplitRule[],
  onUpdateRules: React.Dispatch<React.SetStateAction<ColumnSplitRule[]>>
) => {
  const [selectedCol, setSelectedCol] = useState<string>('');
  const [delimiter, setDelimiter] = useState<string>('-');
  const [segmentsCount, setSegmentsCount] = useState<number>(2);

  const handleAddRule = () => {
    if (!selectedCol || !delimiter || segmentsCount < 2) return;
    if (splitRules.some((r) => r.column_name === selectedCol)) return;

    const newSegments: SegmentDefinition[] = Array.from({ length: segmentsCount }).map((_, i) => ({
      index: i,
      suggested_alias: `${selectedCol}_parte_${i + 1}`,
    }));

    const newRule: ColumnSplitRule = {
      column_name: selectedCol,
      enabled: true,
      delimiter: delimiter,
      keep_original: true,
      segments: newSegments,
    };

    onUpdateRules((prev) => [...prev, newRule]);
    setSelectedCol('');
  };

  const handleRemoveRule = (colName: string) => {
    onUpdateRules((prev) => prev.filter((r) => r.column_name !== colName));
  };

  const handleUpdateSegment = (colName: string, index: number, newAlias: string) => {
    onUpdateRules((prev) =>
      prev.map((rule) => {
        if (rule.column_name !== colName) return rule;
        const updatedSegments = rule.segments.map((seg) =>
          seg.index === index ? { ...seg, suggested_alias: newAlias } : seg
        );
        return { ...rule, segments: updatedSegments };
      })
    );
  };

  const allColNames = columns.map((c) => c.column_name);
  const canAdd = Boolean(selectedCol && delimiter && segmentsCount >= 2);

  return {
    selectedCol,
    setSelectedCol,
    delimiter,
    setDelimiter,
    segmentsCount,
    setSegmentsCount,
    allColNames,
    canAdd,
    handleAddRule,
    handleRemoveRule,
    handleUpdateSegment,
  };
};
