import React from 'react';
import { ShieldCheck } from 'lucide-react';
import type { DatasetProfile } from '../../api/types';
import { SilverTableToolbar } from "./SilverTableToolbar";
import { SilverVirtualTable } from "./SilverVirtualTable";

interface SilverTableProps {
  profile: DatasetProfile | undefined;
  silverRecords: Record<string, any>[] | undefined;
  silverLoading: boolean;
  silverFilterStatus: string;
  onStatusChange: (val: string) => void;
  silverSearch: string;
  onSearchChange: (val: string) => void;
  silverCol: string;
  onColChange: (val: string) => void;
  silverExcelFilters: Record<string, string[]>;
  onApplyExcelFilter: (colName: string, selectedVals: string[] | undefined) => void;
  projectId?: string;
}

export const SilverTable: React.FC<SilverTableProps> = (props) => {
  return (
    <div className="tab-pane">
      <div className="glass-card">
        <SilverTableToolbar {...props} />

        {props.silverLoading ? (
          <div style={{ textAlign: 'center', padding: '3rem', color: 'var(--accent-indigo)' }}>
            <ShieldCheck size={32} className="animate-spin" style={{ margin: '0 auto 1rem auto', display: 'block' }} />
            <span>Consultando datos transformados en Capa Plata...</span>
          </div>
        ) : props.silverRecords && props.silverRecords.length > 0 ? (
          <SilverVirtualTable
            silverRecords={props.silverRecords}
            silverExcelFilters={props.silverExcelFilters}
            onApplyExcelFilter={props.onApplyExcelFilter}
            projectId={props.projectId}
          />
        ) : (
          <p style={{ color: 'var(--text-muted)' }}>Procesa la Capa Bronce para visualizar los registros limpios en Plata.</p>
        )}
      </div>
    </div>
  );
};
