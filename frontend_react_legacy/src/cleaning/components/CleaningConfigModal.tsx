import React, { useState } from 'react';
import { AlertTriangle, Search } from 'lucide-react';
import type { ColumnProfile, ColumnCleaningRule } from '../../api/types';

import { GlobalCleaningSwitches } from './GlobalCleaningSwitches';
import { ColumnCleaningRow } from './ColumnCleaningRow';
import { DomainFilterPills } from './DomainFilterPills';
import { domainPredicates, type DomainCategoryFilter } from './domainFilters';

import { CleaningModalHeader } from './CleaningModalHeader';
import { CleaningModalFooter } from './CleaningModalFooter';
import { CleaningTableHeader } from './CleaningTableHeader';

interface CleaningConfigModalProps {
  isOpen: boolean;
  onClose: () => void;
  columns: ColumnProfile[];
  columnRules: Record<string, ColumnCleaningRule>;
  updateColumnRule: (colName: string, field: string, value: any) => void;
  globalTrimSpaces: boolean;
  setGlobalTrimSpaces: (val: boolean) => void;
  globalUppercase: boolean;
  setGlobalUppercase: (val: boolean) => void;
  globalCleanSpecialChars: boolean;
  setGlobalCleanSpecialChars: (val: boolean) => void;
  globalCleanAccentsAndN: boolean;
  setGlobalCleanAccentsAndN: (val: boolean) => void;
  globalCleanColons: boolean;
  setGlobalCleanColons: (val: boolean) => void;
  globalCleanDots: boolean;
  setGlobalCleanDots: (val: boolean) => void;
  globalCleanCommas: boolean;
  setGlobalCleanCommas: (val: boolean) => void;
  onApplyTransform: () => Promise<void>;
  isTransforming?: boolean;
  transformError?: string | null;
}

const inferDataType = (colUpper: string): string => {
  if (['ENTERED_DR', 'ENTERED_CR', 'ACCOUNTED_DR', 'ACCOUNTED_CR', 'DEBIT', 'CREDIT', 'AMOUNT', 'VALOR'].some((k) => colUpper.includes(k))) return 'DOUBLE';
  if (['DATE', 'PERIOD', 'CREATION', 'POSTED_DATE'].some((k) => colUpper.includes(k))) return 'DATE';
  if (colUpper === 'CURRENCY' || colUpper.includes('FLAG')) return 'CHAR';
  if (colUpper.includes('HEADER_ID') || colUpper.includes('BATCH_ID')) return 'BIGINT';
  return 'VARCHAR';
};

export const CleaningConfigModal: React.FC<CleaningConfigModalProps> = ({
  isOpen,
  onClose,
  columns,
  columnRules,
  updateColumnRule,
  globalTrimSpaces,
  setGlobalTrimSpaces,
  globalUppercase,
  setGlobalUppercase,
  globalCleanSpecialChars,
  setGlobalCleanSpecialChars,
  globalCleanAccentsAndN,
  setGlobalCleanAccentsAndN,
  globalCleanColons,
  setGlobalCleanColons,
  globalCleanDots,
  setGlobalCleanDots,
  globalCleanCommas,
  setGlobalCleanCommas,
  onApplyTransform,
  isTransforming = false,
  transformError = null,
}) => {
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedDomain, setSelectedDomain] = useState<DomainCategoryFilter>('ALL');
  const [hoveredType, setHoveredType] = useState<string | null>(null);

  if (!isOpen) return null;

  const isAnyColumnIncluded = columns.some((col) => {
    const rule = columnRules[col.column_name];
    return rule ? rule.include_in_silver !== false : true;
  });

  const activeNamesCount: Record<string, number> = {};
  columns.forEach((col) => {
    const rule = columnRules[col.column_name];
    if (rule && rule.include_in_silver !== false) {
      const rawAlias = rule.new_column_name ? rule.new_column_name.trim() : col.column_name;
      activeNamesCount[rawAlias.toUpperCase()] = (activeNamesCount[rawAlias.toUpperCase()] || 0) + 1;
    }
  });

  const duplicateNamesList = Object.keys(activeNamesCount).filter((name) => activeNamesCount[name] > 1);
  const hasDuplicateNames = duplicateNamesList.length > 0;

  const filteredColumns = columns.filter((col) => {
    const alias = columnRules[col.column_name]?.new_column_name || '';
    const matchesSearch = col.column_name.toLowerCase().includes(searchTerm.toLowerCase()) || alias.toLowerCase().includes(searchTerm.toLowerCase());
    if (!matchesSearch) return false;
    return domainPredicates[selectedDomain](col);
  });

  const handleToggleAutoConfig = () => {
    columns.forEach((col) => {
      if (isAnyColumnIncluded) {
        updateColumnRule(col.column_name, 'include_in_silver', false);
      } else {
        const isConstant = col.unique_count === 1 || col.null_percentage >= 100.0;
        updateColumnRule(col.column_name, 'include_in_silver', !isConstant);
        if (!isConstant) {
          const targetType = inferDataType(col.column_name.toUpperCase());
          updateColumnRule(col.column_name, 'target_data_type', targetType);
          if (targetType === 'DOUBLE') updateColumnRule(col.column_name, 'null_imputation', 'DEFAULT');
          const isCategory = ['CURRENCY', 'JE_SOURCE', 'JE_CATEGORY', 'LEDGER_NAME', 'STATUS', 'QUALITY_STATUS', 'USER'].some((k) => col.column_name.toUpperCase().includes(k)) || col.uniqueness_ratio < 0.05;
          updateColumnRule(col.column_name, 'convert_to_category', isCategory);
        }
      }
    });
  };

  return (
    <div style={{ position: 'fixed', inset: 0, backgroundColor: 'var(--bg-modal-overlay)', backdropFilter: 'blur(12px)', display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 1000, padding: '1.5rem' }}>
      <div style={{ backgroundColor: 'var(--bg-modal-card)', border: '1px solid var(--border-glass)', borderRadius: '16px', width: '95vw', maxWidth: '1400px', maxHeight: '92vh', display: 'flex', flexDirection: 'column', boxShadow: 'var(--card-shadow)', overflow: 'hidden' }}>
        <CleaningModalHeader isAnyColumnIncluded={isAnyColumnIncluded} onToggleAutoConfig={handleToggleAutoConfig} onClose={onClose} />

        <div style={{ padding: '1.25rem 1.5rem', overflowY: 'auto', flex: 1, display: 'flex', flexDirection: 'column', gap: '1rem' }}>
          {transformError && (
            <div style={{ padding: '0.85rem 1.25rem', borderRadius: '10px', backgroundColor: 'rgba(244, 63, 94, 0.15)', border: '1px solid var(--accent-rose)', color: 'var(--accent-rose)', fontSize: '0.88rem', fontWeight: 600, display: 'flex', alignItems: 'center', gap: '0.6rem' }}>
              <AlertTriangle size={20} style={{ flexShrink: 0 }} />
              <span>{transformError}</span>
            </div>
          )}

          <GlobalCleaningSwitches
            globalTrimSpaces={globalTrimSpaces} onToggleTrim={setGlobalTrimSpaces}
            globalUppercase={globalUppercase} onToggleUppercase={setGlobalUppercase}
            globalCleanSpecialChars={globalCleanSpecialChars} onToggleSpecialChars={setGlobalCleanSpecialChars}
            globalCleanAccentsAndN={globalCleanAccentsAndN} onToggleAccentsAndN={setGlobalCleanAccentsAndN}
            globalCleanColons={globalCleanColons} onToggleColons={setGlobalCleanColons}
            globalCleanDots={globalCleanDots} onToggleDots={setGlobalCleanDots}
            globalCleanCommas={globalCleanCommas} onToggleCommas={setGlobalCleanCommas}
          />

          <DomainFilterPills columns={columns} selectedDomain={selectedDomain} onSelectDomain={setSelectedDomain} />

          <div style={{ position: 'relative' }}>
            <Search size={16} style={{ position: 'absolute', left: '12px', top: '50%', transform: 'translateY(-50%)', color: 'var(--text-muted)' }} />
            <input
              type="text" placeholder="Filtrar por nombre original o alias..." value={searchTerm} onChange={(e) => setSearchTerm(e.target.value)}
              style={{ width: '100%', padding: '0.5rem 1rem 0.5rem 2.4rem', borderRadius: '8px', backgroundColor: 'var(--bg-input)', border: '1px solid var(--border-glass)', color: 'var(--text-main)', fontSize: '0.85rem' }}
            />
          </div>

          <div style={{ overflowX: 'auto', overflowY: 'visible', flex: 1, border: '1px solid var(--border-glass)', borderRadius: '8px' }}>
            <table className="data-table" style={{ width: '100%', borderCollapse: 'separate', borderSpacing: 0 }}>
              <CleaningTableHeader />
              <tbody>
                {filteredColumns.map((col) => {
                  const rule = columnRules[col.column_name] || { include_in_silver: true, new_column_name: '', target_data_type: 'VARCHAR', null_imputation: 'DEFAULT', convert_to_category: false };
                  return (
                    <ColumnCleaningRow
                      key={col.column_name} col={col} rule={rule} duplicateNamesList={duplicateNamesList}
                      onUpdateRule={updateColumnRule} onHoverType={setHoveredType}
                    />
                  );
                })}
              </tbody>
            </table>
          </div>
        </div>

        <CleaningModalFooter hasDuplicateNames={hasDuplicateNames} isTransforming={isTransforming} onClose={onClose} onSaveAndProcess={onApplyTransform} />
      </div>
    </div>
  );
};
