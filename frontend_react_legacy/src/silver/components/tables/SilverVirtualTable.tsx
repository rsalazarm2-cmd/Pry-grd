import React from 'react';
import { ExcelColumnFilter } from "../../../shared/components/tables/ExcelColumnFilter";
import { useVirtualTable } from "../../../shared/hooks/useVirtualTable";
import { DuplicateInspectorPopover } from "../../../shared/components/tables/DuplicateInspectorPopover";

interface SilverVirtualTableProps {
  silverRecords: Record<string, any>[];
  silverExcelFilters: Record<string, string[]>;
  onApplyExcelFilter: (colName: string, selectedVals: string[] | undefined) => void;
  projectId?: string;
}

export const SilverVirtualTable: React.FC<SilverVirtualTableProps> = ({
  silverRecords,
  silverExcelFilters,
  onApplyExcelFilter,
  projectId,
}) => {
  const { parentRef, virtualRows, totalSize } = useVirtualTable({
    data: silverRecords,
    estimateSize: 40,
    overscan: 8,
  });

  const headers = Object.keys(silverRecords[0] || {});
  const paddingTop = virtualRows.length > 0 ? virtualRows[0].start : 0;
  const paddingBottom = virtualRows.length > 0 ? totalSize - virtualRows[virtualRows.length - 1].end : 0;

  return (
    <div
      ref={parentRef}
      style={{
        maxHeight: '550px',
        overflowY: 'auto',
        overflowX: 'auto',
        border: '1px solid var(--border-glass)',
        borderRadius: '10px',
        position: 'relative',
      }}
    >
      <table className="medallion-table" style={{ width: '100%' }}>
        <thead style={{ position: 'sticky', top: 0, zIndex: 10, backgroundColor: 'var(--bg-card, #1e293b)' }}>
          <tr>
            {headers.map((header) => (
              <th key={header} style={{ whiteSpace: 'nowrap' }}>
                <div style={{ display: 'inline-flex', alignItems: 'center' }}>
                  <span>{header}</span>
                  <ExcelColumnFilter
                    layer="silver"
                    columnName={header}
                    projectId={projectId}
                    selectedValues={silverExcelFilters[header]}
                    onApplyFilter={onApplyExcelFilter}
                  />
                </div>
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {paddingTop > 0 && (
            <tr>
              <td colSpan={headers.length} style={{ height: `${paddingTop}px`, padding: 0 }} />
            </tr>
          )}
          {virtualRows.map((virtualRow) => {
            const row = silverRecords[virtualRow.index];
            const isDupRow = row['_DUPLICATE_INDEX'] > 1 || Object.values(row).some(v => typeof v === 'string' && v.startsWith('DUP_'));
            const dupIndex = row['_DUPLICATE_INDEX'] || (isDupRow ? 2 : 1);
            const matchedRow = row['_DUPLICATE_MATCHED_ROW'] || (virtualRow.index > 0 ? virtualRow.index : 1);

            return (
              <tr key={virtualRow.index} style={{ backgroundColor: isDupRow ? 'rgba(245, 158, 11, 0.08)' : undefined }}>
                {headers.map((header, colIdx) => {
                  const val = row[header];
                  const isDupCol = typeof val === 'string' && val.startsWith('DUP_');
                  return (
                    <td key={header} style={{ whiteSpace: 'nowrap' }}>
                      {colIdx === 0 && isDupRow && (
                        <span style={{ marginRight: '0.4rem' }}>
                          <DuplicateInspectorPopover dupIndex={dupIndex} matchedRow={matchedRow} />
                        </span>
                      )}
                      {val !== null && val !== undefined ? String(val) : <span style={{ color: 'var(--text-muted)', fontStyle: 'italic' }}>NULL</span>}
                    </td>
                  );
                })}
              </tr>
            );
          })}
          {paddingBottom > 0 && (
            <tr>
              <td colSpan={headers.length} style={{ height: `${paddingBottom}px`, padding: 0 }} />
            </tr>
          )}
        </tbody>
      </table>
    </div>
  );
};
