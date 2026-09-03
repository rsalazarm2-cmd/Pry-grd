import React from 'react';
import { Pencil, Zap, CircleDot } from 'lucide-react';

export const CleaningTableHeader: React.FC = () => {
  return (
    <thead>
      <tr>
        <th style={{ width: '60px', textAlign: 'center' }}>INCLUIR</th>
        <th style={{ minWidth: '220px' }}>COLUMNA ORIGINAL</th>
        <th style={{ minWidth: '250px' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
            <Pencil size={14} style={{ color: 'var(--accent-cyan)' }} />
            <span>ALIAS (RENOMBRADO ÚNICO)</span>
          </div>
        </th>
        <th style={{ minWidth: '180px' }}>TIPO DATO PLATA</th>
        <th style={{ minWidth: '120px', textAlign: 'center' }}>
          <div style={{ display: 'inline-flex', alignItems: 'center', justifyContent: 'center', gap: '4px' }}>
            <Zap size={14} style={{ color: 'var(--accent-amber)' }} />
            <span>CATEGORÍA ENUM</span>
          </div>
        </th>
        <th style={{ minWidth: '260px' }}>TRATAMIENTO DE NULOS</th>
        <th style={{ minWidth: '90px', textAlign: 'center' }}>
          <div style={{ display: 'inline-flex', alignItems: 'center', justifyContent: 'center', gap: '4px' }}>
            <CircleDot size={14} style={{ color: 'var(--accent-rose)' }} />
            <span>Puntos (.)</span>
          </div>
        </th>
        <th style={{ minWidth: '90px', textAlign: 'center' }}>
          <div style={{ display: 'inline-flex', alignItems: 'center', justifyContent: 'center', gap: '4px' }}>
            <CircleDot size={14} style={{ color: 'var(--accent-amber)' }} />
            <span>Comas (,)</span>
          </div>
        </th>
      </tr>
    </thead>
  );
};
