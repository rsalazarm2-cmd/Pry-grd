import React from 'react';
import { AlertCircle, CheckCircle2, Layers, Database } from 'lucide-react';
import type { ColumnProfile } from '../../../shared/api/types';

interface SilverProfilingCardsProps {
  totalColumns: number;
  totalRows: number;
  constantCols: ColumnProfile[];
  perfectCols: ColumnProfile[];
  filterType: 'ALL' | 'CONSTANTS' | 'PERFECT';
  onFilterChange: (type: 'ALL' | 'CONSTANTS' | 'PERFECT') => void;
}

export const SilverProfilingCards: React.FC<SilverProfilingCardsProps> = ({
  totalColumns,
  totalRows,
  constantCols,
  perfectCols,
  filterType,
  onFilterChange,
}) => {
  return (
    <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))', gap: '0.75rem', marginBottom: '1.2rem' }}>
      <div
        onClick={() => onFilterChange('ALL')}
        style={{
          padding: '0.75rem 1rem',
          borderRadius: '10px',
          backgroundColor: filterType === 'ALL' ? 'rgba(56, 189, 248, 0.15)' : 'var(--bg-input)',
          border: filterType === 'ALL' ? '1px solid var(--accent-cyan)' : '1px solid var(--border-glass)',
          cursor: 'pointer',
          transition: 'all 0.2s ease',
        }}
      >
        <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', fontWeight: 600, display: 'flex', alignItems: 'center', gap: '0.3rem' }}>
          <Layers size={14} style={{ color: 'var(--accent-cyan)' }} />
          Total Columnas Plata
        </div>
        <div style={{ fontSize: '1.4rem', fontWeight: 800, color: 'var(--accent-cyan)' }}>{totalColumns}</div>
      </div>

      <div
        onClick={() => onFilterChange('CONSTANTS')}
        style={{
          padding: '0.75rem 1rem',
          borderRadius: '10px',
          backgroundColor: filterType === 'CONSTANTS' ? 'rgba(245, 158, 11, 0.15)' : 'var(--bg-input)',
          border: filterType === 'CONSTANTS' ? '1px solid var(--accent-amber)' : '1px solid var(--border-glass)',
          cursor: 'pointer',
          transition: 'all 0.2s ease',
        }}
      >
        <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', fontWeight: 600, display: 'flex', alignItems: 'center', gap: '0.3rem' }}>
          <AlertCircle size={14} style={{ color: 'var(--accent-amber)' }} />
          Varianza 0 (Constantes)
        </div>
        <div style={{ fontSize: '1.4rem', fontWeight: 800, color: 'var(--accent-amber)' }}>{constantCols.length}</div>
      </div>

      <div
        onClick={() => onFilterChange('PERFECT')}
        style={{
          padding: '0.75rem 1rem',
          borderRadius: '10px',
          backgroundColor: filterType === 'PERFECT' ? 'rgba(16, 185, 129, 0.15)' : 'var(--bg-input)',
          border: filterType === 'PERFECT' ? '1px solid var(--accent-emerald)' : '1px solid var(--border-glass)',
          cursor: 'pointer',
          transition: 'all 0.2s ease',
        }}
      >
        <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', fontWeight: 600, display: 'flex', alignItems: 'center', gap: '0.3rem' }}>
          <CheckCircle2 size={14} style={{ color: 'var(--accent-emerald)' }} />
          Columnas Saneadas (100%)
        </div>
        <div style={{ fontSize: '1.4rem', fontWeight: 800, color: 'var(--accent-emerald)' }}>{perfectCols.length}</div>
      </div>

      <div
        style={{
          padding: '0.75rem 1rem',
          borderRadius: '10px',
          backgroundColor: 'var(--bg-input)',
          border: '1px solid var(--border-glass)',
        }}
      >
        <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', fontWeight: 600, display: 'flex', alignItems: 'center', gap: '0.3rem' }}>
          <Database size={14} style={{ color: 'var(--accent-indigo)' }} />
          Registros en Plata
        </div>
        <div style={{ fontSize: '1.4rem', fontWeight: 800, color: 'var(--accent-indigo)' }}>
          {totalRows.toLocaleString()}
        </div>
      </div>
    </div>
  );
};
