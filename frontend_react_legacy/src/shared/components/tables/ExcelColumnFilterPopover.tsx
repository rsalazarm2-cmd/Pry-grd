import React from 'react';
import { Search, X, Loader2 } from 'lucide-react';

interface ExcelColumnFilterPopoverProps {
  columnName: string;
  popoverRef: React.RefObject<HTMLDivElement | null>;
  loading: boolean;
  searchTerm: string;
  setSearchTerm: (val: string) => void;
  filteredItems: { value: string; count: number }[];
  checkedValues: string[];
  distinctValuesCount: number;
  isAllChecked: boolean;
  onToggleAll: () => void;
  onToggleItem: (val: string) => void;
  onApply: () => void;
  onClear: () => void;
  onClose: () => void;
}

export const ExcelColumnFilterPopover: React.FC<ExcelColumnFilterPopoverProps> = ({
  columnName,
  popoverRef,
  loading,
  searchTerm,
  setSearchTerm,
  filteredItems,
  checkedValues,
  distinctValuesCount,
  isAllChecked,
  onToggleAll,
  onToggleItem,
  onApply,
  onClear,
  onClose,
}) => {
  return (
    <div
      ref={popoverRef}
      onClick={(e) => e.stopPropagation()}
      style={{
        position: 'absolute', top: '100%', left: 0, marginTop: '6px', width: '260px',
        backgroundColor: 'var(--bg-popover)', border: '1px solid var(--border-glass)', borderRadius: '8px',
        boxShadow: 'var(--popover-shadow)', zIndex: 9999, padding: '10px', display: 'flex', flexDirection: 'column', gap: '8px',
      }}
    >
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <span style={{ fontSize: '0.8rem', fontWeight: 700, color: 'var(--text-main)' }}>
          Filtro Excel: <span style={{ color: 'var(--accent-cyan)' }}>{columnName}</span>
        </span>
        <button onClick={onClose} style={{ background: 'none', border: 'none', color: 'var(--text-muted)', cursor: 'pointer', padding: 0 }}>
          <X size={14} />
        </button>
      </div>

      <div style={{ position: 'relative' }}>
        <Search size={12} style={{ position: 'absolute', left: '8px', top: '50%', transform: 'translateY(-50%)', color: 'var(--text-muted)' }} />
        <input
          type="text" placeholder="Buscar valor..." value={searchTerm} onChange={(e) => setSearchTerm(e.target.value)}
          style={{ width: '100%', padding: '4px 8px 4px 24px', fontSize: '0.75rem', borderRadius: '4px', border: '1px solid var(--border-glass)', backgroundColor: 'var(--bg-input)', color: 'var(--text-main)', boxSizing: 'border-box' }}
        />
      </div>

      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '2px 0', borderBottom: '1px solid var(--border-glass)' }}>
        <label style={{ fontSize: '0.75rem', display: 'flex', alignItems: 'center', gap: '6px', cursor: 'pointer', color: 'var(--text-muted)' }}>
          <input type="checkbox" checked={isAllChecked} onChange={onToggleAll} style={{ cursor: 'pointer' }} />
          <span>(Seleccionar Todo)</span>
        </label>
        <span style={{ fontSize: '0.7rem', color: 'var(--text-dim)' }}>{checkedValues.length} de {distinctValuesCount}</span>
      </div>

      <div style={{ maxHeight: '180px', overflowY: 'auto', display: 'flex', flexDirection: 'column', gap: '4px' }}>
        {loading ? (
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', padding: '15px', color: 'var(--text-muted)', fontSize: '0.75rem', gap: '6px' }}>
            <Loader2 size={14} className="animate-spin" /> Cargando valores...
          </div>
        ) : filteredItems.length > 0 ? (
          filteredItems.map((item, idx) => {
            const valStr = item.value !== null && item.value !== undefined ? String(item.value) : '(Vacío / NULL)';
            const isChecked = checkedValues.includes(item.value);

            return (
              <label
                key={idx}
                style={{ fontSize: '0.75rem', display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '3px 4px', borderRadius: '4px', cursor: 'pointer', backgroundColor: isChecked ? 'rgba(56, 189, 248, 0.1)' : 'transparent' }}
              >
                <div style={{ display: 'flex', alignItems: 'center', gap: '6px', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                  <input type="checkbox" checked={isChecked} onChange={() => onToggleItem(item.value)} style={{ cursor: 'pointer' }} />
                  <span style={{ color: isChecked ? 'var(--text-main)' : 'var(--text-muted)', overflow: 'hidden', textOverflow: 'ellipsis' }}>{valStr}</span>
                </div>
                <span style={{ fontSize: '0.68rem', color: 'var(--text-dim)', paddingLeft: '6px' }}>({item.count})</span>
              </label>
            );
          })
        ) : (
          <div style={{ fontSize: '0.75rem', color: 'var(--text-dim)', textAlign: 'center', padding: '10px' }}>Sin resultados</div>
        )}
      </div>

      <div style={{ display: 'flex', gap: '6px', marginTop: '4px', borderTop: '1px solid var(--border-glass)', paddingTop: '8px' }}>
        <button onClick={onClear} style={{ flex: 1, padding: '4px', fontSize: '0.72rem', borderRadius: '4px', border: '1px solid var(--border-glass)', backgroundColor: 'transparent', color: 'var(--text-muted)', cursor: 'pointer' }}>Borrar Filtro</button>
        <button onClick={onApply} style={{ flex: 1, padding: '4px', fontSize: '0.72rem', borderRadius: '4px', border: 'none', backgroundColor: 'var(--accent-indigo)', color: 'white', fontWeight: 700, cursor: 'pointer' }}>Aplicar</button>
      </div>
    </div>
  );
};
