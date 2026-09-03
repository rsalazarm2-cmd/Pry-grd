import React from 'react';
import { ExcelColumnFilter } from "../../../shared/components/tables/ExcelColumnFilter";
import { useVirtualTable } from "../../../shared/hooks/useVirtualTable";

interface BronzeVirtualTableProps {
  bronzeRecords: Record<string, any>[];
  bronzeExcelFilters: Record<string, string[]>;
  onApplyExcelFilter: (colName: string, selectedVals: string[] | undefined) => void;
}

export const BronzeVirtualTable: React.FC<BronzeVirtualTableProps> = ({
  bronzeRecords,
  bronzeExcelFilters,
  onApplyExcelFilter,
}) => {
  const { parentRef, virtualRows, totalSize } = useVirtualTable({
    data: bronzeRecords,
    estimateSize: 40,
    overscan: 8,
  });

  const headers = Object.keys(bronzeRecords[0] || {});
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
                    layer="bronze"
                    columnName={header}
                    selectedValues={bronzeExcelFilters[header]}
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
            const row = bronzeRecords[virtualRow.index];
            return (
              <tr key={virtualRow.index}>
                {headers.map((header) => (
                  <td key={header} style={{ whiteSpace: 'nowrap' }}>
                    {row[header] !== null && row[header] !== undefined ? String(row[header]) : <span style={{ color: 'var(--text-muted)', fontStyle: 'italic' }}>NULL</span>}
                  </td>
                ))}
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
