import React, { useState } from 'react';
import { Activity, Search, Sparkles, ChevronDown, ChevronUp } from 'lucide-react';
import type { DatasetProfile } from '../../../shared/api/types';
import { SilverProfilingCards } from './SilverProfilingCards';
import { SilverProfilingTable } from './SilverProfilingTable';

interface SilverProfilingDiagnosticProps {
  profile: DatasetProfile | undefined;
  onOpenValueTools: () => void;
}

export const SilverProfilingDiagnostic: React.FC<SilverProfilingDiagnosticProps> = ({
  profile,
  onOpenValueTools,
}) => {
  const [searchTerm, setSearchTerm] = useState('');
  const [filterType, setFilterType] = useState<'ALL' | 'CONSTANTS' | 'PERFECT'>('ALL');
  const [isExpanded, setIsExpanded] = useState(true);

  if (!profile || !profile.columns || profile.columns.length === 0) return null;

  const columns = profile.columns;
  const constantCols = columns.filter((c) => c.unique_count === 1 || c.null_percentage >= 100);
  const perfectCols = columns.filter((c) => c.null_count === 0 && c.unique_count > 1);

  const filteredColumns = columns.filter((col) => {
    const matchesSearch = col.column_name.toLowerCase().includes(searchTerm.toLowerCase());
    if (!matchesSearch) return false;
    if (filterType === 'CONSTANTS') return col.unique_count === 1 || col.null_percentage >= 100;
    if (filterType === 'PERFECT') return col.null_count === 0 && col.unique_count > 1;
    return true;
  });

  return (
    <div className="glass-card" style={{ marginBottom: '1.5rem' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '1rem', marginBottom: isExpanded ? '1rem' : 0 }}>
        <div>
          <h3 style={{ fontSize: '1.1rem', fontWeight: 700, margin: '0 0 0.3rem 0', color: 'var(--accent-amber)', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <Activity size={20} style={{ color: 'var(--accent-amber)' }} /> Diagnóstico Exploratorio y Profiling Columnar (Capa Plata)
          </h3>
          <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)', margin: 0 }}>
            Análisis de calidad post-limpieza sobre los {profile.total_rows.toLocaleString()} registros tipados.
          </p>
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
          <button onClick={onOpenValueTools} className="btn-primary" style={{ padding: '0.5rem 1rem', fontSize: '0.82rem', fontWeight: 700, background: 'linear-gradient(135deg, var(--accent-amber), var(--accent-orange, #f97316))' }}>
            <Sparkles size={16} /> Configurar Funcionalidades de Valor
          </button>
          <button onClick={() => setIsExpanded(!isExpanded)} style={{ background: 'none', border: '1px solid var(--border-glass)', borderRadius: '8px', color: 'var(--text-muted)', cursor: 'pointer', padding: '0.4rem 0.6rem', display: 'flex', alignItems: 'center', gap: '0.3rem', fontSize: '0.8rem' }}>
            {isExpanded ? <ChevronUp size={16} /> : <ChevronDown size={16} />}
            <span>{isExpanded ? 'Plegar' : 'Desplegar'}</span>
          </button>
        </div>
      </div>

      {isExpanded && (
        <>
          <SilverProfilingCards
            totalColumns={columns.length}
            totalRows={profile.total_rows}
            constantCols={constantCols}
            perfectCols={perfectCols}
            filterType={filterType}
            onFilterChange={setFilterType}
          />

          <div style={{ display: 'flex', gap: '0.75rem', marginBottom: '1rem', flexWrap: 'wrap' }}>
            <div style={{ position: 'relative', flex: 1, minWidth: '240px' }}>
              <Search size={15} style={{ position: 'absolute', left: '12px', top: '50%', transform: 'translateY(-50%)', color: 'var(--text-muted)' }} />
              <input type="text" placeholder="Filtrar columnas en plata por nombre..." value={searchTerm} onChange={(e) => setSearchTerm(e.target.value)} style={{ width: '100%', padding: '0.45rem 1rem 0.45rem 2.4rem', borderRadius: '8px', backgroundColor: 'var(--bg-input)', border: '1px solid var(--border-glass)', color: 'var(--text-main)', fontSize: '0.83rem' }} />
            </div>
            {filterType !== 'ALL' && (
              <button onClick={() => setFilterType('ALL')} style={{ padding: '0.45rem 0.8rem', borderRadius: '8px', border: '1px solid var(--border-glass)', background: 'transparent', color: 'var(--accent-amber)', fontSize: '0.8rem', fontWeight: 600, cursor: 'pointer' }}>
                Ver Todas ({columns.length})
              </button>
            )}
          </div>

          <SilverProfilingTable filteredColumns={filteredColumns} />
        </>
      )}
    </div>
  );
};
