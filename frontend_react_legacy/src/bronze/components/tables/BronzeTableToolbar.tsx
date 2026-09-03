import React from 'react';
import { Database, Search, Upload, Trash2, Sliders } from 'lucide-react';
import type { DatasetProfile } from '../../api/types';

interface BronzeTableToolbarProps {
  profile: DatasetProfile | undefined;
  showConfig: boolean;
  onToggleConfig: () => void;
  bronzeSearch: string;
  onSearchChange: (val: string) => void;
  bronzeCol: string;
  onColChange: (val: string) => void;
  bronzeLimit: number;
  onLimitChange: (limit: number) => void;
  onFileUpload: (e: React.ChangeEvent<HTMLInputElement>) => void;
  isUploading: boolean;
  onResetProject: () => void;
  isDeleting?: boolean;
}

export const BronzeTableToolbar: React.FC<BronzeTableToolbarProps> = ({
  profile,
  showConfig,
  onToggleConfig,
  bronzeSearch,
  onSearchChange,
  bronzeCol,
  onColChange,
  bronzeLimit,
  onLimitChange,
  onFileUpload,
  isUploading,
  onResetProject,
  isDeleting,
}) => {
  return (
    <>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.2rem', flexWrap: 'wrap', gap: '1rem' }}>
        <div>
          <h3 style={{ fontSize: '1.1rem', fontWeight: 700, margin: '0 0 0.3rem 0', color: 'var(--accent-cyan)', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <Database size={20} style={{ color: 'var(--accent-amber)' }} />
            Visor Tabular de Registros Crudos (Capa Bronce)
          </h3>
          <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)', margin: 0 }}>
            Consulta en tiempo real procesada por el motor in-memory DuckDB directamente sobre <code style={{ color: 'var(--accent-cyan)' }}>bronze.parquet</code>.
          </p>
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', flexWrap: 'wrap' }}>
          <button
            onClick={onToggleConfig}
            style={{
              display: 'flex', alignItems: 'center', gap: '0.5rem', padding: '0.55rem 1.1rem', borderRadius: '8px',
              backgroundColor: showConfig ? 'var(--accent-indigo)' : 'rgba(99, 102, 241, 0.15)',
              border: '1px solid var(--accent-indigo)', color: 'white',
              fontWeight: 700, fontSize: '0.82rem', cursor: 'pointer',
            }}
          >
            <Sliders size={16} />
            <span>{showConfig ? 'Ocultar Panel Limpieza' : '⚙️ Configurar Limpieza (Bronce ➔ Plata)'}</span>
          </button>

          <button
            onClick={onResetProject}
            disabled={isDeleting || isUploading}
            title="Eliminar todos los archivos Parquet e iniciar desde cero"
            style={{
              display: 'flex', alignItems: 'center', gap: '0.5rem', padding: '0.55rem 1.1rem', borderRadius: '8px',
              backgroundColor: 'rgba(239, 68, 68, 0.15)', border: '1px solid rgba(239, 68, 68, 0.35)', color: 'var(--accent-rose, #ef4444)',
              fontWeight: 700, fontSize: '0.82rem', cursor: (isDeleting || isUploading) ? 'not-allowed' : 'pointer',
            }}
          >
            <Trash2 size={16} />
            <span>{isDeleting ? 'Limpiando...' : 'Limpiar Datos'}</span>
          </button>

          <label
            style={{
              display: 'flex', alignItems: 'center', gap: '0.5rem', padding: '0.55rem 1.1rem', borderRadius: '8px',
              backgroundColor: 'rgba(56, 189, 248, 0.15)', border: '1px solid rgba(56, 189, 248, 0.35)', color: 'var(--accent-cyan)',
              fontWeight: 700, fontSize: '0.82rem', cursor: isUploading ? 'not-allowed' : 'pointer',
            }}
          >
            <Upload size={16} />
            <span>{isUploading ? 'Ingestando CSV...' : 'Subir e Ingestar CSV'}</span>
            <input type="file" accept=".csv" onChange={onFileUpload} style={{ display: 'none' }} disabled={isUploading} />
          </label>
        </div>
      </div>

      <div style={{ display: 'flex', gap: '0.75rem', marginBottom: '1rem', flexWrap: 'wrap' }}>
        <div style={{ position: 'relative', flex: 1, minWidth: '240px' }}>
          <Search size={16} style={{ position: 'absolute', left: '12px', top: '50%', transform: 'translateY(-50%)', color: 'var(--text-muted)' }} />
          <input
            type="text" placeholder="Buscar cualquier valor en los registros de Bronce..." value={bronzeSearch}
            onChange={(e) => onSearchChange(e.target.value)}
            style={{ width: '100%', padding: '0.5rem 1rem 0.5rem 2.4rem', borderRadius: '8px', backgroundColor: 'var(--bg-input)', border: '1px solid var(--border-glass)', color: 'var(--text-main)', fontSize: '0.85rem' }}
          />
        </div>

        <select value={bronzeCol} onChange={(e) => onColChange(e.target.value)} style={{ padding: '0.5rem 1rem', borderRadius: '8px', backgroundColor: 'var(--bg-input-select)', border: '1px solid var(--border-glass)', color: 'var(--text-main)', fontSize: '0.85rem' }}>
          <option value="TODOS">Buscar en Todas las Columnas</option>
          {profile?.columns.map((c) => (
            <option key={c.column_name} value={c.column_name}>{c.column_name}</option>
          ))}
        </select>

        <select value={bronzeLimit} onChange={(e) => onLimitChange(Number(e.target.value))} style={{ padding: '0.5rem 1rem', borderRadius: '8px', backgroundColor: 'var(--bg-input-select)', border: '1px solid var(--border-glass)', color: 'var(--text-main)', fontSize: '0.85rem' }}>
          <option value={25}>Mostrar 25 filas</option>
          <option value={50}>Mostrar 50 filas</option>
          <option value={100}>Mostrar 100 filas</option>
          <option value={500}>Mostrar 500 filas</option>
        </select>
      </div>
    </>
  );
};
