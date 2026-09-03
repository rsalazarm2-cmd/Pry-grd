import React from 'react';
import { Scissors, Wand2, CircleDot, FileText, Hash, ShieldAlert } from 'lucide-react';

interface GlobalCleaningSwitchesProps {
  globalTrimSpaces: boolean;
  onToggleTrim: (val: boolean) => void;
  globalCleanSpecialChars: boolean;
  onToggleSpecialChars: (val: boolean) => void;
  globalCleanAccentsAndN: boolean;
  onToggleAccentsAndN: (val: boolean) => void;
  globalCleanColons: boolean;
  onToggleColons: (val: boolean) => void;
  globalCleanDots: boolean;
  onToggleDots: (val: boolean) => void;
  globalCleanCommas: boolean;
  onToggleCommas: (val: boolean) => void;
  duplicateActionMode?: string;
  onDuplicateActionModeChange?: (mode: string) => void;
}

export const GlobalCleaningSwitches: React.FC<GlobalCleaningSwitchesProps> = ({
  globalTrimSpaces,
  onToggleTrim,
  globalCleanSpecialChars,
  onToggleSpecialChars,
  globalCleanAccentsAndN,
  onToggleAccentsAndN,
  globalCleanColons,
  onToggleColons,
  globalCleanDots,
  onToggleDots,
  globalCleanCommas,
  onToggleCommas,
  duplicateActionMode = 'FLAG_QUARANTINE',
  onDuplicateActionModeChange,
}) => {
  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '0.85rem' }}>
      <div style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))',
        gap: '0.75rem',
        padding: '1rem',
        backgroundColor: 'var(--bg-input)',
        borderRadius: '12px',
        border: '1px solid var(--border-glass)',
      }}>
        <label style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', cursor: 'pointer', fontSize: '0.82rem', color: 'var(--text-main)', fontWeight: 600 }}>
          <input type="checkbox" checked={globalTrimSpaces} onChange={(e) => onToggleTrim(e.target.checked)} />
          <Scissors size={15} style={{ color: 'var(--accent-cyan)' }} />
          <span>TRIM Global Espacios</span>
        </label>

        <label style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', cursor: 'pointer', fontSize: '0.82rem', color: 'var(--text-main)', fontWeight: 600 }}>
          <input type="checkbox" checked={globalCleanAccentsAndN} onChange={(e) => onToggleAccentsAndN(e.target.checked)} />
          <FileText size={15} style={{ color: 'var(--accent-purple)' }} />
          <span>Normalizar Tildes & Ñ</span>
        </label>

        <label style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', cursor: 'pointer', fontSize: '0.82rem', color: 'var(--text-main)', fontWeight: 600 }}>
          <input type="checkbox" checked={globalCleanSpecialChars} onChange={(e) => onToggleSpecialChars(e.target.checked)} />
          <Wand2 size={15} style={{ color: 'var(--accent-pink)' }} />
          <span>Quitar Símbolos ( () /&%$#"!; )</span>
        </label>

        <label style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', cursor: 'pointer', fontSize: '0.82rem', color: 'var(--text-main)', fontWeight: 600 }}>
          <input type="checkbox" checked={globalCleanColons} onChange={(e) => onToggleColons(e.target.checked)} />
          <Hash size={15} style={{ color: 'var(--accent-amber)' }} />
          <span>Quitar Dos Puntos (:)</span>
        </label>

        <label style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', cursor: 'pointer', fontSize: '0.82rem', color: 'var(--text-main)', fontWeight: 600 }}>
          <input type="checkbox" checked={globalCleanDots} onChange={(e) => onToggleDots(e.target.checked)} />
          <CircleDot size={15} style={{ color: 'var(--accent-rose)' }} />
          <span>Quitar Puntos (.) Global</span>
        </label>

        <label style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', cursor: 'pointer', fontSize: '0.82rem', color: 'var(--text-main)', fontWeight: 600 }}>
          <input type="checkbox" checked={globalCleanCommas} onChange={(e) => onToggleCommas(e.target.checked)} />
          <CircleDot size={15} style={{ color: 'var(--accent-amber)' }} />
          <span>Quitar Comas (,) Global</span>
        </label>
      </div>

      {/* Control Forense de Tratamiento de Datos Trampa y Duplicados */}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '0.75rem 1rem', borderRadius: '10px', backgroundColor: 'rgba(245, 158, 11, 0.08)', border: '1px solid var(--accent-amber)', flexWrap: 'wrap', gap: '0.75rem' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', color: 'var(--accent-amber)', fontWeight: 700, fontSize: '0.85rem' }}>
          <ShieldAlert size={18} />
          <span>Tratamiento Forense de Duplicados & Datos Trampa:</span>
        </div>
        <select
          value={duplicateActionMode}
          onChange={(e) => onDuplicateActionModeChange && onDuplicateActionModeChange(e.target.value)}
          style={{ padding: '0.45rem 0.8rem', borderRadius: '6px', backgroundColor: 'var(--bg-input-select)', border: '1px solid var(--accent-amber)', color: 'var(--text-main)', fontWeight: 600, fontSize: '0.82rem' }}
        >
          <option value="FLAG_QUARANTINE">🏷️ Modo 1: Marcar en Cuarentena (Recomendado Auditoría)</option>
          <option value="PREFIX_DUP">🏷️ Modo 2: Renombrar Asientos con Prefijo DUP_ [Identificación Visual]</option>
          <option value="PURGE_DELETE">🗑️ Modo 3: Purga Controlada (Eliminar en Plata con copia en Cuarentena)</option>
        </select>
      </div>
    </div>
  );
};
