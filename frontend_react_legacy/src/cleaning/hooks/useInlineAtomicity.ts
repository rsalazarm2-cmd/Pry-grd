import { useState, useEffect } from 'react';
import type { ColumnProfile } from '../../api/types';
import type { ColumnSplitRule } from '../../api/atomicityApi';
import type { AtomicityColumnConfig, AtomicitySegmentConfig } from './ColumnCleaningRow';

const getInitialAtomicityConfigs = (columns: ColumnProfile[]): Record<string, AtomicityColumnConfig> => {
  return {};
};

export function useInlineAtomicity(isOpen: boolean, columns: ColumnProfile[]) {
  const [atomicityConfigs, setAtomicityConfigs] = useState<Record<string, AtomicityColumnConfig>>({});

  useEffect(() => {
    if (isOpen && columns.length > 0) {
      setAtomicityConfigs((prev) => {
        if (Object.keys(prev).length === 0) {
          return getInitialAtomicityConfigs(columns);
        }
        return prev;
      });
    }
  }, [isOpen, columns]);

  const handleToggleAtomicity = (colName: string, enabled: boolean) => {
    setAtomicityConfigs((prev) => {
      const colCfg = prev[colName];
      if (!colCfg) return prev;
      return {
        ...prev,
        [colName]: { ...colCfg, enabled },
      };
    });
  };

  const handleUpdateSegment = (
    colName: string,
    segIndex: number,
    field: keyof AtomicitySegmentConfig,
    val: any
  ) => {
    setAtomicityConfigs((prev) => {
      const colCfg = prev[colName];
      if (!colCfg) return prev;
      const updatedSegments = colCfg.segments.map((seg) =>
        seg.index === segIndex ? { ...seg, [field]: val } : seg
      );
      return {
        ...prev,
        [colName]: { ...colCfg, segments: updatedSegments },
      };
    });
  };

  const getSplitRules = (): ColumnSplitRule[] => {
    return Object.entries(atomicityConfigs)
      .filter(([_, cfg]) => cfg.isAtomizable && cfg.enabled)
      .map(([colName, cfg]) => ({
        column_name: colName,
        enabled: cfg.enabled,
        delimiter: cfg.delimiter,
        keep_original: true,
        segments: cfg.segments
          .filter((s) => s.enabled)
          .map((s) => ({
            index: s.index,
            suggested_alias: s.alias,
          })),
      }));
  };

  return {
    atomicityConfigs,
    handleToggleAtomicity,
    handleUpdateSegment,
    getSplitRules,
  };
}
