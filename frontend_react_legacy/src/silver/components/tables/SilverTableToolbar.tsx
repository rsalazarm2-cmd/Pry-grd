import React from 'react';
import { ShieldCheck, Search } from 'lucide-react';
import type { DatasetProfile } from '../../api/types';

interface SilverTableToolbarProps {
  profile: DatasetProfile | undefined;
  silverSearch: string;
  onSearchChange: (val: string) => void;
  silverCol: string;
  onColChange: (val: string) => void;
}

export const SilverTableToolbar: React.FC<SilverTableToolbarProps> = ({
  profile,
  silverSearch,
  onSearchChange,
  silverCol,
  onColChange,
}) => {
  return (
    <>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.2rem', flexWrap: 'wrap', gap: '1rem' }}>
        <div>
          <h3 style={{ fontSize: '1.1rem', fontWeight: 700, margin: '0 0 0.3rem 0', color: 'var(--accent-indigo)', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <ShieldCheck size={20} style={{ color: 'var(--accent-indigo)' }} />
            Visor Tabular de Datos Limpios y Tipados (Capa Plata)
          </h3>
          <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)', margin: 0 }}>
            Consulta interactiva sobre datos saneados guardados en <code style={{ color: 'var(--accent-indigo)' }}>silver.parquet</code>.
          </p>
        </div>
      </div>

      <div style={{ display: 'flex', gap: '0.75rem', marginBottom: '1rem', flexWrap: 'wrap' }}>
        <div style={{ position: 'relative', flex: 1, minWidth: '240px' }}>
          <Search size={16} style={{ position: 'absolute', left: '12px', top: '50%', transform: 'translateY(-50%)', color: 'var(--text-muted)' }} />
          <input
            type="text" placeholder="Buscar en registros transformados de Capa Plata..." value={silverSearch}
            onChange={(e) => onSearchChange(e.target.value)}
            style={{ width: '100%', padding: '0.5rem 1rem 0.5rem 2.4rem', borderRadius: '8px', backgroundColor: 'var(--bg-input)', border: '1px solid var(--border-glass)', color: 'var(--text-main)', fontSize: '0.85rem' }}
          />
        </div>

        <select value={silverCol} onChange={(e) => onColChange(e.target.value)} style={{ padding: '0.5rem 1rem', borderRadius: '8px', backgroundColor: 'var(--bg-input-select)', border: '1px solid var(--border-glass)', color: 'var(--text-main)', fontSize: '0.85rem' }}>
          <option value="TODOS">Buscar en Todas las Columnas</option>
          {profile?.columns.map((c) => (
            <option key={c.column_name} value={c.column_name}>{c.column_name}</option>
          ))}
        </select>

        <button
          onClick={() => onSearchChange(silverSearch === 'DUP_' ? '' : 'DUP_')}
          style={{
            display: 'flex', alignItems: 'center', gap: '0.4rem', padding: '0.5rem 1rem', borderRadius: '8px',
            backgroundColor: silverSearch === 'DUP_' ? 'var(--accent-amber)' : 'rgba(245, 158, 11, 0.15)',
            border: '1px solid var(--accent-amber)', color: silverSearch === 'DUP_' ? 'black' : 'var(--accent-amber)',
            fontWeight: 700, fontSize: '0.82rem', cursor: 'pointer',
          }}
        >
          <span>⚠️ {silverSearch === 'DUP_' ? 'Viendo Duplicados (Limpiar)' : 'Ver Solo Duplicados (DUP_)'}</span>
        </button>
      </div>
    </>
  );
};
