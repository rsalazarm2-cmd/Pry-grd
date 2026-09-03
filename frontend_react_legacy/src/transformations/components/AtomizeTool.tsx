import React from 'react';
import { SplitSquareHorizontal, Plus } from 'lucide-react';
import type { ColumnProfile } from '../../api/types';
import type { ColumnSplitRule } from '../../api/atomicityApi';
import { useAtomizeToolController } from '../hooks/useAtomizeToolController';
import { AtomizeRuleList } from './AtomizeRuleList';

interface AtomizeToolProps {
  columns: ColumnProfile[];
  splitRules: ColumnSplitRule[];
  onUpdateRules: React.Dispatch<React.SetStateAction<ColumnSplitRule[]>>;
}

export const AtomizeTool: React.FC<AtomizeToolProps> = ({ columns, splitRules, onUpdateRules }) => {
  const ctrl = useAtomizeToolController(columns, splitRules, onUpdateRules);

  return (
    <div style={{ border: '1px solid var(--border-glass)', borderRadius: '12px', backgroundColor: 'rgba(255,255,255,0.02)', padding: '1.25rem' }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginBottom: '1.25rem' }}>
        <div style={{ padding: '0.5rem', borderRadius: '8px', backgroundColor: 'rgba(56, 189, 248, 0.15)', color: 'var(--accent-cyan)' }}>
          <SplitSquareHorizontal size={20} />
        </div>
        <div>
          <h4 style={{ fontSize: '1rem', fontWeight: 600, margin: 0, color: 'var(--text-main)' }}>Atomización de Campos</h4>
          <p style={{ fontSize: '0.8rem', color: 'var(--text-muted)', margin: 0 }}>Divide columnas compuestas usando un delimitador en múltiples partes estructuradas.</p>
        </div>
      </div>

      <div style={{ display: 'flex', gap: '1rem', alignItems: 'flex-end', flexWrap: 'wrap', marginBottom: '1.5rem', paddingBottom: '1.5rem', borderBottom: '1px solid var(--border-glass)' }}>
        <div style={{ flex: 1, minWidth: '200px' }}>
          <label style={{ display: 'block', fontSize: '0.8rem', marginBottom: '0.4rem', color: 'var(--text-muted)' }}>Columna a Atomizar</label>
          <select value={ctrl.selectedCol} onChange={(e) => ctrl.setSelectedCol(e.target.value)} style={{ width: '100%', padding: '0.5rem', borderRadius: '6px', border: '1px solid var(--border-glass)', background: 'var(--bg-card)' }}>
            <option value="">-- Selecciona una columna --</option>
            {ctrl.allColNames.map((col) => (
              <option key={col} value={col}>{col}</option>
            ))}
          </select>
        </div>
        <div style={{ width: '120px' }}>
          <label style={{ display: 'block', fontSize: '0.8rem', marginBottom: '0.4rem', color: 'var(--text-muted)' }}>Delimitador</label>
          <input type="text" value={ctrl.delimiter} onChange={(e) => ctrl.setDelimiter(e.target.value)} placeholder="Ej: - , _" style={{ width: '100%', padding: '0.5rem', borderRadius: '6px', border: '1px solid var(--border-glass)', background: 'var(--bg-card)', color: 'white' }} />
        </div>
        <div style={{ width: '120px' }}>
          <label style={{ display: 'block', fontSize: '0.8rem', marginBottom: '0.4rem', color: 'var(--text-muted)' }}>Nº Partes</label>
          <input type="number" min="2" max="10" value={ctrl.segmentsCount} onChange={(e) => ctrl.setSegmentsCount(parseInt(e.target.value) || 2)} style={{ width: '100%', padding: '0.5rem', borderRadius: '6px', border: '1px solid var(--border-glass)', background: 'var(--bg-card)', color: 'white' }} />
        </div>
        <button onClick={ctrl.handleAddRule} disabled={!ctrl.canAdd} style={{ padding: '0.5rem 1rem', borderRadius: '6px', border: 'none', background: 'linear-gradient(135deg, var(--accent-cyan), var(--accent-indigo))', color: 'white', fontWeight: 600, cursor: !ctrl.canAdd ? 'not-allowed' : 'pointer', opacity: !ctrl.canAdd ? 0.5 : 1, display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
          <Plus size={16} /> Añadir Regla
        </button>
      </div>

      <AtomizeRuleList
        splitRules={splitRules}
        onRemoveRule={ctrl.handleRemoveRule}
        onUpdateSegment={ctrl.handleUpdateSegment}
      />
    </div>
  );
};
