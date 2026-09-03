import React, { useMemo } from 'react';
import { Layers } from 'lucide-react';
import type { ColumnProfile } from '../../shared/api/types';

interface SilverDimensionsToolProps {
  columns: ColumnProfile[];
  silverRecords: Record<string, any>[] | undefined;
  goldDimensions: string[];
  onUpdateDimensions: (dims: string[]) => void;
  onClose?: () => void;
}

export const SilverDimensionsTool: React.FC<SilverDimensionsToolProps> = ({
  columns,
  silverRecords,
  goldDimensions,
  onUpdateDimensions,
}) => {
  const availableColumns = useMemo(() => {
    if (silverRecords && silverRecords.length > 0) {
      return Object.keys(silverRecords[0]);
    }
    return columns.map(c => c.column_name);
  }, [columns, silverRecords]);

  const handleToggleColumn = (col: string) => {
    if (goldDimensions.includes(col)) {
      onUpdateDimensions(goldDimensions.filter(d => d !== col));
    } else {
      onUpdateDimensions([...goldDimensions, col]);
    }
  };

  const handleSelectAll = () => {
    onUpdateDimensions(availableColumns);
  };

  const handleClearAll = () => {
    onUpdateDimensions([]);
  };

  return (
    <div style={{
      border: '1px solid var(--border-glass)',
      borderRadius: '12px',
      backgroundColor: 'rgba(255,255,255,0.02)',
      padding: '1.25rem'
    }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginBottom: '1.25rem' }}>
        <div style={{ padding: '0.5rem', borderRadius: '8px', backgroundColor: 'rgba(56, 189, 248, 0.15)', color: 'var(--accent-cyan)' }}>
          <Layers size={20} />
        </div>
        <div>
          <h4 style={{ fontSize: '1rem', fontWeight: 600, margin: 0, color: 'var(--text-main)' }}>Dimensiones de Segmentación Plata</h4>
          <p style={{ fontSize: '0.8rem', color: 'var(--text-muted)', margin: 0 }}>Selecciona qué columnas de Plata forman la matriz multidimensional para análisis de auditoría.</p>
        </div>
      </div>

      <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '1rem', marginBottom: '1rem' }}>
        <button onClick={handleSelectAll} style={{ background: 'none', border: 'none', color: 'var(--accent-cyan)', cursor: 'pointer', fontSize: '0.8rem' }}>Marcar Todas</button>
        <button onClick={handleClearAll} style={{ background: 'none', border: 'none', color: 'var(--accent-rose)', cursor: 'pointer', fontSize: '0.8rem' }}>Desmarcar Todas</button>
      </div>

      <div style={{ 
        display: 'grid', 
        gridTemplateColumns: 'repeat(auto-fill, minmax(200px, 1fr))', 
        gap: '0.8rem',
        maxHeight: '300px',
        overflowY: 'auto',
        padding: '0.5rem',
        backgroundColor: 'var(--bg-input)',
        borderRadius: '8px',
        border: '1px solid var(--border-glass)'
      }}>
        {availableColumns.map(col => {
          const isSelected = goldDimensions.includes(col);
          return (
            <label 
              key={col} 
              style={{
                display: 'flex', 
                alignItems: 'center', 
                gap: '0.5rem', 
                padding: '0.5rem', 
                borderRadius: '6px',
                backgroundColor: isSelected ? 'rgba(56, 189, 248, 0.1)' : 'transparent',
                border: isSelected ? '1px solid var(--accent-cyan)' : '1px solid transparent',
                cursor: 'pointer',
                transition: 'all 0.2s',
                fontSize: '0.85rem'
              }}
            >
              <input 
                type="checkbox" 
                checked={isSelected} 
                onChange={() => handleToggleColumn(col)}
                style={{ cursor: 'pointer' }}
              />
              <span style={{ 
                color: isSelected ? 'var(--text-main)' : 'var(--text-muted)',
                whiteSpace: 'nowrap',
                overflow: 'hidden',
                textOverflow: 'ellipsis'
              }}>
                {col}
              </span>
            </label>
          );
        })}
      </div>
    </div>
  );
};
