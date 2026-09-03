import React from 'react';
import { AlertCircle, ShieldAlert, CheckCircle2, Copy } from 'lucide-react';
import type { ColumnProfile } from '../../../shared/api/types';

interface BronzeProfilingKPIsProps {
  totalColumnsCount: number;
  constantCols: ColumnProfile[];
  nullCols: ColumnProfile[];
  perfectCols: ColumnProfile[];
  duplicateCount?: number;
  filterType: 'ALL' | 'CONSTANTS' | 'HAS_NULLS';
  onSelectFilter: (filter: 'ALL' | 'CONSTANTS' | 'HAS_NULLS') => void;
}

export const BronzeProfilingKPIs: React.FC<BronzeProfilingKPIsProps> = ({
  totalColumnsCount,
  constantCols,
  nullCols,
  perfectCols,
  duplicateCount = 0,
  filterType,
  onSelectFilter,
}) => {
  return (
    <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(170px, 1fr))', gap: '0.75rem', marginBottom: '1.2rem' }}>
      <div
        onClick={() => onSelectFilter('ALL')}
        style={{
          padding: '0.75rem 1rem',
          borderRadius: '10px',
          backgroundColor: filterType === 'ALL' ? 'rgba(56, 189, 248, 0.15)' : 'var(--bg-input)',
          border: filterType === 'ALL' ? '1px solid var(--accent-cyan)' : '1px solid var(--border-glass)',
          cursor: 'pointer',
        }}
      >
        <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', fontWeight: 600 }}>Total Columnas ERP</div>
        <div style={{ fontSize: '1.35rem', fontWeight: 800, color: 'var(--accent-cyan)' }}>{totalColumnsCount}</div>
      </div>

      <div
        onClick={() => onSelectFilter('CONSTANTS')}
        style={{
          padding: '0.75rem 1rem',
          borderRadius: '10px',
          backgroundColor: filterType === 'CONSTANTS' ? 'rgba(245, 158, 11, 0.15)' : 'var(--bg-input)',
          border: filterType === 'CONSTANTS' ? '1px solid var(--accent-amber)' : '1px solid var(--border-glass)',
          cursor: 'pointer',
        }}
      >
        <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', fontWeight: 600, display: 'flex', alignItems: 'center', gap: '0.3rem' }}>
          <AlertCircle size={14} style={{ color: 'var(--accent-amber)' }} />
          Constantes
        </div>
        <div style={{ fontSize: '1.35rem', fontWeight: 800, color: 'var(--accent-amber)' }}>{constantCols.length}</div>
      </div>

      <div
        onClick={() => onSelectFilter('HAS_NULLS')}
        style={{
          padding: '0.75rem 1rem',
          borderRadius: '10px',
          backgroundColor: filterType === 'HAS_NULLS' ? 'rgba(244, 63, 94, 0.15)' : 'var(--bg-input)',
          border: filterType === 'HAS_NULLS' ? '1px solid var(--accent-rose)' : '1px solid var(--border-glass)',
          cursor: 'pointer',
        }}
      >
        <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', fontWeight: 600, display: 'flex', alignItems: 'center', gap: '0.3rem' }}>
          <ShieldAlert size={14} style={{ color: 'var(--accent-rose)' }} />
          Con Nulos
        </div>
        <div style={{ fontSize: '1.35rem', fontWeight: 800, color: 'var(--accent-rose)' }}>{nullCols.length}</div>
      </div>

      {/* Tarjeta KPI de Estado de Duplicados */}
      <div
        style={{
          padding: '0.75rem 1rem',
          borderRadius: '10px',
          backgroundColor: duplicateCount > 0 ? 'rgba(245, 158, 11, 0.12)' : 'rgba(16, 185, 129, 0.12)',
          border: duplicateCount > 0 ? '1px solid var(--accent-amber)' : '1px solid var(--accent-emerald)',
        }}
      >
        <div style={{ fontSize: '0.75rem', color: duplicateCount > 0 ? 'var(--accent-amber)' : 'var(--accent-emerald)', fontWeight: 700, display: 'flex', alignItems: 'center', gap: '0.3rem' }}>
          {duplicateCount > 0 ? <Copy size={14} /> : <CheckCircle2 size={14} />}
          {duplicateCount > 0 ? 'Duplicados Detectados' : 'Dataset Único'}
        </div>
        <div style={{ fontSize: '1.35rem', fontWeight: 800, color: duplicateCount > 0 ? 'var(--accent-amber)' : 'var(--accent-emerald)' }}>
          {duplicateCount > 0 ? `${duplicateCount} filas` : '✅ 0 (100% Único)'}
        </div>
      </div>
    </div>
  );
};
