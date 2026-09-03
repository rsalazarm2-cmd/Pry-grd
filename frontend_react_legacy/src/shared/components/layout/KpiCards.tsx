import React from 'react';
import { Database, Layers, ShieldCheck, AlertTriangle } from 'lucide-react';
import type { DatasetProfile, Project } from '../../api/types';

interface KpiCardsProps {
  profile: DatasetProfile | undefined;
  activeProject: Project | null;
  onOpenCleaningModal: () => void;
}

export const KpiCards: React.FC<KpiCardsProps> = ({
  profile,
  activeProject,
  onOpenCleaningModal,
}) => {
  const totalAnomalies = profile?.anomaly_matrix
    ? Object.values(profile.anomaly_matrix).reduce((acc, curr) => acc + curr, 0)
    : 0;

  return (
    <div className="grid-kpi">
      <div className="glass-card" style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
        <div style={{ padding: '0.8rem', borderRadius: '12px', backgroundColor: 'rgba(56, 189, 248, 0.15)', color: 'var(--accent-cyan)', display: 'flex' }}>
          <Database size={24} />
        </div>
        <div>
          <div className="kpi-title">Volumen Total Registros</div>
          <div className="kpi-value">{profile?.total_rows ? profile.total_rows.toLocaleString() : '0'}</div>
        </div>
      </div>

      <div className="glass-card" style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
        <div style={{ padding: '0.8rem', borderRadius: '12px', backgroundColor: 'rgba(99, 102, 241, 0.15)', color: 'var(--accent-indigo)', display: 'flex' }}>
          <Layers size={24} />
        </div>
        <div>
          <div className="kpi-title">Estructura Columnar</div>
          <div className="kpi-value">{profile?.total_columns || 0} Columnas ERP</div>
        </div>
      </div>

      <div className="glass-card" style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
        <div style={{ padding: '0.8rem', borderRadius: '12px', backgroundColor: 'rgba(34, 197, 94, 0.15)', color: 'var(--accent-emerald)', display: 'flex' }}>
          <ShieldCheck size={24} />
        </div>
        <div>
          <div className="kpi-title">Espacio de Trabajo Activo</div>
          <div className="kpi-value" style={{ fontSize: '1.2rem', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap', maxWidth: '200px' }}>
            {activeProject?.name || 'Proyecto Principal'}
          </div>
        </div>
      </div>

      <div
        className="glass-card"
        onClick={onOpenCleaningModal}
        style={{
          display: 'flex',
          alignItems: 'center',
          gap: '1rem',
          cursor: 'pointer',
          border: totalAnomalies > 0 ? '1px solid rgba(248, 113, 113, 0.5)' : undefined,
        }}
      >
        <div style={{ padding: '0.8rem', borderRadius: '12px', backgroundColor: totalAnomalies > 0 ? 'rgba(248, 113, 113, 0.2)' : 'rgba(234, 179, 8, 0.15)', color: totalAnomalies > 0 ? '#f87171' : 'var(--accent-amber)', display: 'flex' }}>
          <AlertTriangle size={24} />
        </div>
        <div>
          <div className="kpi-title">Matriz de Anomalías A1..A6</div>
          <div className="kpi-value" style={{ color: totalAnomalies > 0 ? '#f87171' : undefined }}>
            {totalAnomalies > 0 ? `${totalAnomalies} Anomalías` : '0 Anomalías'}
          </div>
        </div>
      </div>
    </div>
  );
};
