import { useState, useEffect, useRef } from 'react';
import { apiClient } from '../api/client';

export const useExcelColumnFilterController = (
  layer: 'bronze' | 'silver' | 'gold_ledger' | 'gold_account',
  columnName: string,
  projectId?: string,
  selectedValues?: string[],
  onApplyFilter?: (columnName: string, selectedValues: string[] | undefined) => void
) => {
  const [isOpen, setIsOpen] = useState(false);
  const [loading, setLoading] = useState(false);
  const [distinctValues, setDistinctValues] = useState<{ value: string; count: number }[]>([]);
  const [searchTerm, setSearchTerm] = useState('');
  const [checkedValues, setCheckedValues] = useState<string[]>([]);
  const popoverRef = useRef<HTMLDivElement>(null);

  const isActive = Boolean(selectedValues && selectedValues.length > 0);

  useEffect(() => {
    if (isOpen) {
      setLoading(true);
      apiClient
        .getDistinctValues(layer, columnName, projectId)
        .then((items) => {
          setDistinctValues(items);
          if (selectedValues && selectedValues.length > 0) {
            setCheckedValues([...selectedValues]);
          } else {
            setCheckedValues(items.map((i) => i.value));
          }
        })
        .catch((err) => {
          console.error('Error cargando valores únicos:', err);
        })
        .finally(() => {
          setLoading(false);
        });
    }
  }, [isOpen, layer, columnName, projectId]);

  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (popoverRef.current && !popoverRef.current.contains(event.target as Node)) {
        setIsOpen(false);
      }
    };
    if (isOpen) {
      document.addEventListener('mousedown', handleClickOutside);
    }
    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, [isOpen]);

  const filteredItems = distinctValues.filter((item) =>
    (item.value || '').toLowerCase().includes(searchTerm.toLowerCase())
  );

  const isAllChecked =
    distinctValues.length > 0 && checkedValues.length === distinctValues.length;

  const handleToggleAll = () => {
    if (isAllChecked) {
      setCheckedValues([]);
    } else {
      setCheckedValues(distinctValues.map((i) => i.value));
    }
  };

  const handleToggleItem = (val: string) => {
    setCheckedValues((prev) =>
      prev.includes(val) ? prev.filter((v) => v !== val) : [...prev, val]
    );
  };

  const handleApply = () => {
    if (onApplyFilter) {
      if (checkedValues.length === distinctValues.length || checkedValues.length === 0) {
        onApplyFilter(columnName, undefined);
      } else {
        onApplyFilter(columnName, checkedValues);
      }
    }
    setIsOpen(false);
  };

  const handleClear = () => {
    setCheckedValues(distinctValues.map((i) => i.value));
    if (onApplyFilter) {
      onApplyFilter(columnName, undefined);
    }
    setIsOpen(false);
  };

  return {
    isOpen,
    setIsOpen,
    loading,
    distinctValues,
    searchTerm,
    setSearchTerm,
    checkedValues,
    popoverRef,
    isActive,
    filteredItems,
    isAllChecked,
    handleToggleAll,
    handleToggleItem,
    handleApply,
    handleClear,
  };
};
