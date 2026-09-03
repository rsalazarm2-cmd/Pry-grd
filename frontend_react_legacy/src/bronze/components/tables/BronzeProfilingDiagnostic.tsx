import React from 'react';
import { Activity, Search, Sparkles, ChevronDown, ChevronUp } from 'lucide-react';
import type { DatasetProfile } from '../../../shared/api/types';
import { useBronzeProfilingController } from '../../hooks/useBronzeProfilingController';
import { BronzeProfilingKPIs } from './BronzeProfilingKPIs';
import { BronzeProfilingTable } from './BronzeProfilingTable';

interface BronzeProfilingDiagnosticProps {
  profile: DatasetProfile | undefined;
  onOpenCleaningModal: () => void;
}

export const BronzeProfilingDiagnostic: React.FC<BronzeProfilingDiagnosticProps> = ({
  profile,
  onOpenCleaningModal,
}) => {
  const {
    searchTerm,
    setSearchTerm,
    filterType,
    setFilterType,
    isExpanded,
    setIsExpanded,
    columns,
    constantCols,
    nullCols,
    perfectCols,
    filteredColumns,
  } = useBronzeProfilingController(profile);

  if (!profile || !profile.columns || profile.columns.length === 0) {
    return null;
  }

  return (
    <div className="glass-card" style={{ marginBottom: '1.5rem' }}>
      {/* Header del Diagnóstico Exploratorio */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '1rem', marginBottom: isExpanded ? '1rem' : 0 }}>
        <div>
          <h3 style={{ fontSize: '1.1rem', fontWeight: 700, margin: '0 0 0.3rem 0', color: 'var(--accent-cyan)', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <Activity size={20} style={{ color: 'var(--accent-cyan)' }} />
            Diagnóstico Exploratorio y Profiling Columnar de Calidad (Capa Bronce)
          </h3>
          <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)', margin: 0 }}>
            Análisis de varianza, nulos y unicidad en vivo sobre los {profile.total_rows.toLocaleString()} registros ingestados.
          </p>
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
          <button
            onClick={onOpenCleaningModal}
            className="btn-primary"
            style={{
              padding: '0.5rem 1rem',
              fontSize: '0.82rem',
              fontWeight: 700,
              background: 'linear-gradient(135deg, var(--accent-indigo), var(--accent-purple))',
              boxShadow: '0 4px 12px rgba(99, 102, 241, 0.25)',
            }}
          >
            <Sparkles size={16} /> Configurar Limpieza y Renombrado
          </button>

          <button
            onClick={() => setIsExpanded(!isExpanded)}
            style={{
              background: 'none',
              border: '1px solid var(--border-glass)',
              borderRadius: '8px',
              color: 'var(--text-muted)',
              cursor: 'pointer',
              padding: '0.4rem 0.6rem',
              display: 'flex',
              alignItems: 'center',
              gap: '0.3rem',
              fontSize: '0.8rem',
            }}
          >
            {isExpanded ? <ChevronUp size={16} /> : <ChevronDown size={16} />}
            <span>{isExpanded ? 'Plegar' : 'Desplegar'}</span>
          </button>
        </div>
      </div>

      {isExpanded && (
        <>
          {/* Tarjetas KPI Sub-componente */}
          <BronzeProfilingKPIs
            totalColumnsCount={columns.length}
            constantCols={constantCols}
            nullCols={nullCols}
            perfectCols={perfectCols}
            filterType={filterType}
            onSelectFilter={setFilterType}
          />

          {/* Filtro de Búsqueda de Diagnóstico */}
          <div style={{ display: 'flex', gap: '0.75rem', marginBottom: '1rem', flexWrap: 'wrap' }}>
            <div style={{ position: 'relative', flex: 1, minWidth: '240px' }}>
              <Search size={15} style={{ position: 'absolute', left: '12px', top: '50%', transform: 'translateY(-50%)', color: 'var(--text-muted)' }} />
              <input
                type="text"
                placeholder="Filtrar columnas por nombre..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                style={{
                  width: '100%',
                  padding: '0.45rem 1rem 0.45rem 2.4rem',
                  borderRadius: '8px',
                  backgroundColor: 'var(--bg-input)',
                  border: '1px solid var(--border-glass)',
                  color: 'var(--text-main)',
                  fontSize: '0.83rem',
                }}
              />
            </div>

            {filterType !== 'ALL' && (
              <button
                onClick={() => setFilterType('ALL')}
                style={{
                  padding: '0.45rem 0.8rem',
                  borderRadius: '8px',
                  border: '1px solid var(--border-glass)',
                  background: 'transparent',
                  color: 'var(--accent-cyan)',
                  fontSize: '0.8rem',
                  fontWeight: 600,
                  cursor: 'pointer',
                }}
              >
                Ver Todas ({columns.length})
              </button>
            )}
          </div>

          {/* Tabla Sub-componente */}
          <BronzeProfilingTable filteredColumns={filteredColumns} />
        </>
      )}
    </div>
  );
};
