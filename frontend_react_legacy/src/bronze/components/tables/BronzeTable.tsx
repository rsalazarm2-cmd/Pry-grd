import React from 'react';
import { Database } from 'lucide-react';
import type { DatasetProfile } from '../../api/types';
import { BronzeTableToolbar } from "./BronzeTableToolbar";
import { BronzeVirtualTable } from "./BronzeVirtualTable";

interface BronzeTableProps {
  profile: DatasetProfile | undefined;
  showConfig: boolean;
  onToggleConfig: () => void;
  bronzeRecords: Record<string, any>[] | undefined;
  bronzeLoading: boolean;
  bronzeSearch: string;
  onSearchChange: (val: string) => void;
  bronzeCol: string;
  onColChange: (val: string) => void;
  bronzeExcelFilters: Record<string, string[]>;
  onApplyExcelFilter: (colName: string, selectedVals: string[] | undefined) => void;
  bronzeLimit: number;
  onLimitChange: (limit: number) => void;
  onFileUpload: (e: React.ChangeEvent<HTMLInputElement>) => void;
  isUploading: boolean;
  onResetProject: () => void;
  isDeleting?: boolean;
}

export const BronzeTable: React.FC<BronzeTableProps> = (props) => {
  return (
    <div className="tab-pane">
      <div className="glass-card">
        <BronzeTableToolbar {...props} />

        {props.bronzeLoading ? (
          <div style={{ textAlign: 'center', padding: '3rem', color: 'var(--accent-cyan)' }}>
            <Database size={32} className="animate-spin" style={{ margin: '0 auto 1rem auto', display: 'block' }} />
            <span>Consultando archivo Parquet de Capa Bronce con DuckDB...</span>
          </div>
        ) : props.bronzeRecords && props.bronzeRecords.length > 0 ? (
          <BronzeVirtualTable
            bronzeRecords={props.bronzeRecords}
            bronzeExcelFilters={props.bronzeExcelFilters}
            onApplyExcelFilter={props.onApplyExcelFilter}
          />
        ) : (
          <p style={{ color: 'var(--text-muted)' }}>No se encontraron registros en la Capa Bronce. Sube un archivo CSV arriba para comenzar.</p>
        )}
      </div>
    </div>
  );
};
