import { useState } from 'react';
import type { DatasetProfile, ColumnProfile } from '../../shared/api/types';

export const useBronzeProfilingController = (profile: DatasetProfile | undefined) => {
  const [searchTerm, setSearchTerm] = useState('');
  const [filterType, setFilterType] = useState<'ALL' | 'CONSTANTS' | 'HAS_NULLS'>('ALL');
  const [isExpanded, setIsExpanded] = useState(true);

  const columns: ColumnProfile[] = profile?.columns || [];
  const constantCols = columns.filter((c) => c.unique_count === 1 || c.null_percentage >= 100);
  const nullCols = columns.filter((c) => c.null_count > 0);
  const perfectCols = columns.filter((c) => c.null_count === 0 && c.unique_count > 1);

  const filteredColumns = columns.filter((col) => {
    const matchesSearch = col.column_name.toLowerCase().includes(searchTerm.toLowerCase());

    if (!matchesSearch) return false;

    if (filterType === 'CONSTANTS') {
      return col.unique_count === 1 || col.null_percentage >= 100;
    }
    if (filterType === 'HAS_NULLS') {
      return col.null_count > 0;
    }
    return true;
  });

  return {
    searchTerm,
    setSearchTerm,
    filterType,
    setFilterType,
    isExpanded,
    setIsExpanded,
    columns,
    constantCols,
    nullCols,
    perfectCols,
    filteredColumns,
  };
};
