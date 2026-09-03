import React from 'react';
import { Filter } from 'lucide-react';
import { useExcelColumnFilterController } from '../../hooks/useExcelColumnFilterController';
import { ExcelColumnFilterPopover } from './ExcelColumnFilterPopover';

interface ExcelColumnFilterProps {
  layer: 'bronze' | 'silver' | 'gold_ledger' | 'gold_account';
  columnName: string;
  projectId?: string;
  selectedValues?: string[];
  onApplyFilter: (columnName: string, selectedValues: string[] | undefined) => void;
}

export const ExcelColumnFilter: React.FC<ExcelColumnFilterProps> = ({
  layer,
  columnName,
  projectId,
  selectedValues,
  onApplyFilter,
}) => {
  const ctrl = useExcelColumnFilterController(layer, columnName, projectId, selectedValues, onApplyFilter);

  return (
    <div style={{ position: 'relative', display: 'inline-block', marginLeft: '6px' }}>
      <button
        onClick={(e) => {
          e.stopPropagation();
          ctrl.setIsOpen(!ctrl.isOpen);
        }}
        title={`Filtrar por ${columnName} (Estilo Excel)`}
        style={{
          background: ctrl.isActive ? 'var(--accent-amber)' : 'rgba(148, 163, 184, 0.15)',
          color: ctrl.isActive ? '#ffffff' : 'var(--text-muted)',
          border: ctrl.isActive ? '1px solid var(--accent-amber)' : '1px solid var(--border-glass)',
          borderRadius: '4px',
          padding: '2px 5px',
          cursor: 'pointer',
          display: 'inline-flex',
          alignItems: 'center',
          justifyContent: 'center',
          fontSize: '0.75rem',
        }}
      >
        <Filter size={12} style={{ strokeWidth: ctrl.isActive ? 2.5 : 1.8 }} />
      </button>

      {ctrl.isOpen && (
        <ExcelColumnFilterPopover
          columnName={columnName}
          popoverRef={ctrl.popoverRef}
          loading={ctrl.loading}
          searchTerm={ctrl.searchTerm}
          setSearchTerm={ctrl.setSearchTerm}
          filteredItems={ctrl.filteredItems}
          checkedValues={ctrl.checkedValues}
          distinctValuesCount={ctrl.distinctValues.length}
          isAllChecked={ctrl.isAllChecked}
          onToggleAll={ctrl.handleToggleAll}
          onToggleItem={ctrl.handleToggleItem}
          onApply={ctrl.handleApply}
          onClear={ctrl.handleClear}
          onClose={() => ctrl.setIsOpen(false)}
        />
      )}
    </div>
  );
};
