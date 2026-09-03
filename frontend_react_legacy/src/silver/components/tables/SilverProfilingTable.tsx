import React from 'react';
import type { ColumnProfile } from '../../../shared/api/types';

interface SilverProfilingTableProps {
  filteredColumns: ColumnProfile[];
}

export const SilverProfilingTable: React.FC<SilverProfilingTableProps> = ({ filteredColumns }) => {
  return (
    <div style={{ overflowX: 'auto', border: '1px solid var(--border-glass)', borderRadius: '10px', maxHeight: '420px', overflowY: 'auto' }}>
      <table className="medallion-table" style={{ margin: 0 }}>
        <thead style={{ position: 'sticky', top: 0, zIndex: 10 }}>
          <tr>
            <th>Alias / Columna en Plata</th>
            <th>Tipo Dato Final</th>
            <th>Valores Únicos (% Varianza)</th>
            <th>Valores de Muestra / Frecuentes</th>
          </tr>
        </thead>
        <tbody>
          {filteredColumns.map((col) => {
            const isConstant = col.unique_count === 1 || col.null_percentage >= 100;
            const sampleText = col.sample_values && col.sample_values.length > 0
              ? col.sample_values.slice(0, 4).join(', ')
              : 'Sin muestra';

            return (
              <tr key={col.column_name} style={{ backgroundColor: isConstant ? 'rgba(245, 158, 11, 0.04)' : undefined }}>
                <td style={{ fontWeight: 700, fontFamily: 'var(--font-mono)', fontSize: '0.83rem', whiteSpace: 'nowrap' }}>
                  <span style={{ color: 'var(--text-main)' }}>{col.column_name}</span>
                  {isConstant && (
                    <span style={{
                      marginLeft: '0.5rem', fontSize: '0.68rem', padding: '0.15rem 0.4rem', borderRadius: '6px',
                      backgroundColor: 'rgba(245, 158, 11, 0.15)', color: 'var(--accent-amber)', border: '1px solid rgba(245, 158, 11, 0.3)',
                      fontWeight: 700, display: 'inline-flex', alignItems: 'center', gap: '0.2rem',
                    }}>
                      ⚡ CONSTANTE (1 valor)
                    </span>
                  )}
                </td>
                <td>
                  <span style={{ fontSize: '0.75rem', padding: '0.15rem 0.45rem', borderRadius: '4px', backgroundColor: 'rgba(148, 163, 184, 0.15)', color: 'var(--text-main)', fontFamily: 'var(--font-mono)', fontWeight: 600 }}>
                    {col.data_type}
                  </span>
                </td>
                <td style={{ fontWeight: 600, fontSize: '0.82rem' }}>
                  <span style={{ color: 'var(--text-main)' }}>{col.unique_count.toLocaleString()}</span>{' '}
                  <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>({(col.uniqueness_ratio * 100).toFixed(1)}%)</span>
                </td>
                <td style={{ fontSize: '0.78rem', color: 'var(--text-muted)', maxWidth: '340px', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                  <code style={{ fontSize: '0.75rem', color: 'var(--text-main)' }}>{sampleText}</code>
                </td>
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
};

