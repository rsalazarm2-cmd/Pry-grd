import React from 'react';
import type { ColumnProfile, ColumnCleaningRule } from '../../api/types';

interface ColumnCleaningRowProps {
  col: ColumnProfile;
  rule: ColumnCleaningRule;
  duplicateNamesList: string[];
  onUpdateRule: (colName: string, field: string, value: any) => void;
  onHoverType: (type: string | null) => void;
}

export const ColumnCleaningRow: React.FC<ColumnCleaningRowProps> = ({
  col,
  rule,
  duplicateNamesList,
  onUpdateRule,
  onHoverType,
}) => {
  const currentRawAlias = rule.new_column_name ? rule.new_column_name.trim() : col.column_name;
  const currentFinalNameUpper = currentRawAlias.toUpperCase();
  const isDuplicate = rule.include_in_silver !== false && duplicateNamesList.includes(currentFinalNameUpper);

  const samples = col.sample_values || [];
  const topVals = col.top_frequencies ? col.top_frequencies.map((f) => f.value) : [];
  const allText = [...samples, ...topVals].join(' ');
  const dataTypeUpper = col.data_type ? col.data_type.toUpperCase() : '';

  const hasDots = dataTypeUpper.includes('DOUBLE') || dataTypeUpper.includes('FLOAT') || allText.includes('.');
  const hasCommas = allText.includes(',');

  return (
    <tr style={{ opacity: rule.include_in_silver ? 1 : 0.45, borderBottom: '1px solid var(--border-glass)', transition: 'background 0.15s ease' }}>
      <td style={{ width: '50px', textAlign: 'center', padding: '0.65rem 0.5rem' }}>
        <input
          type="checkbox"
          checked={rule.include_in_silver}
          onChange={(e) => onUpdateRule(col.column_name, 'include_in_silver', e.target.checked)}
          style={{ accentColor: 'var(--accent-purple)', transform: 'scale(1.1)', cursor: 'pointer' }}
        />
      </td>

      <td style={{ minWidth: '200px', padding: '0.65rem 0.85rem', color: 'var(--accent-cyan)', fontWeight: 700, fontFamily: 'var(--font-mono)', fontSize: '0.83rem', whiteSpace: 'nowrap' }}>
        {col.column_name}
      </td>

      <td style={{ minWidth: '270px', padding: '0.65rem 0.85rem' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.6rem' }}>
          <input
            type="checkbox"
            checked={rule.should_translate !== false}
            onChange={(e) => onUpdateRule(col.column_name, 'should_translate', e.target.checked)}
            disabled={!rule.include_in_silver}
            style={{ accentColor: 'var(--accent-purple)', transform: 'scale(1.1)', cursor: 'pointer' }}
            title="Marcar para traducir esta columna con IA o desmarcar para conservar en inglés"
          />
          <div style={{ flex: 1, display: 'flex', flexDirection: 'column', gap: '0.2rem' }}>
            <input
              type="text"
              placeholder={`Alias para: ${col.column_name}`}
              value={rule.new_column_name || ''}
              onChange={(e) => onUpdateRule(col.column_name, 'new_column_name', e.target.value.startsWith(' ') ? e.target.value.trimStart() : e.target.value)}
              onBlur={(e) => onUpdateRule(col.column_name, 'new_column_name', e.target.value.trim())}
              disabled={!rule.include_in_silver}
              style={{
                padding: '0.48rem 0.8rem', borderRadius: '8px', width: '100%', minWidth: '200px', boxSizing: 'border-box',
                background: isDuplicate ? 'rgba(239, 68, 68, 0.15)' : 'var(--bg-input-select)',
                border: isDuplicate ? '2px solid var(--accent-rose)' : '1px solid var(--border-glass)',
                color: isDuplicate ? 'var(--accent-rose)' : 'var(--text-main)', fontSize: '0.85rem', fontWeight: isDuplicate ? 700 : 500,
              }}
            />
            {isDuplicate && (
              <span style={{ fontSize: '0.72rem', color: 'var(--accent-rose)', fontWeight: 700 }}>
                Nombre "{currentFinalNameUpper}" duplicado
              </span>
            )}
          </div>
        </div>
      </td>

      <td style={{ minWidth: '180px', padding: '0.65rem 0.85rem' }}>
        <select
          value={rule.target_data_type || 'VARCHAR'}
          onChange={(e) => onUpdateRule(col.column_name, 'target_data_type', e.target.value)}
          onMouseEnter={(e) => onHoverType((e.target as HTMLSelectElement).value)}
          disabled={!rule.include_in_silver}
          style={{
            padding: '0.48rem 0.75rem', borderRadius: '8px', background: 'var(--bg-input-select)', border: '1px solid var(--border-glass)',
            color: 'var(--accent-cyan)', fontWeight: 600, fontSize: '0.82rem', width: '100%', minWidth: '160px',
          }}
        >
          <option value="VARCHAR">VARCHAR (Texto Largo)</option>
          <option value="CHAR">CHAR (Texto Corto Fijo - ej: COP, USD)</option>
          <option value="DOUBLE">DOUBLE (Decimal / Montos)</option>
          <option value="INTEGER">INTEGER (Entero)</option>
          <option value="BIGINT">BIGINT (Entero Grande 64-bit / IDs)</option>
          <option value="BOOLEAN">BOOLEAN (Verdadero / Falso)</option>
          <option value="DATE">DATE (Fecha sin hora)</option>
          <option value="TIMESTAMP">TIMESTAMP (Fecha y Hora)</option>
        </select>
      </td>

      <td style={{ minWidth: '80px', textAlign: 'center', padding: '0.65rem 0.5rem' }}>
        <label style={{ display: 'inline-flex', alignItems: 'center', gap: '0.3rem', cursor: rule.include_in_silver ? 'pointer' : 'not-allowed', fontSize: '0.82rem', fontWeight: 600, color: rule.convert_to_category ? 'var(--accent-cyan)' : 'var(--text-muted)' }} onMouseEnter={() => onHoverType('ENUM')}>
          <input
            type="checkbox"
            checked={!!rule.convert_to_category}
            onChange={(e) => onUpdateRule(col.column_name, 'convert_to_category', e.target.checked)}
            disabled={!rule.include_in_silver}
            style={{ accentColor: 'var(--accent-purple)', cursor: 'pointer' }}
          />
          Sí
        </label>
      </td>

      <td style={{ minWidth: '240px', padding: '0.65rem 0.85rem' }}>
        <select
          value={rule.null_imputation}
          onChange={(e) => onUpdateRule(col.column_name, 'null_imputation', e.target.value)}
          disabled={!rule.include_in_silver}
          style={{
            padding: '0.48rem 0.75rem', borderRadius: '8px', background: 'var(--bg-input-select)', border: '1px solid var(--border-glass)',
            color: rule.null_imputation?.startsWith('ADVANCED') ? 'var(--accent-amber)' : 'var(--text-main)',
            fontWeight: rule.null_imputation?.startsWith('ADVANCED') ? 700 : 400, fontSize: '0.82rem', width: '100%', minWidth: '230px',
          }}
        >
          <option value="DEFAULT">Valor por Defecto (0 / NO_REGISTRADO)</option>
          <option value="NULL">Mantener NULL explícito [Auditoría]</option>
          <option value="ADVANCED_MEAN">Imputación Avanzada: Media (AVG)</option>
          <option value="ADVANCED_MEDIAN">Imputación Avanzada: Mediana</option>
          <option value="ADVANCED_MODE">Imputación Avanzada: Moda</option>
        </select>
      </td>

      <td style={{ minWidth: '70px', textAlign: 'center', padding: '0.65rem 0.5rem' }}>
        <input
          type="checkbox"
          checked={hasDots && rule.clean_dots === true}
          onChange={(e) => onUpdateRule(col.column_name, 'clean_dots', e.target.checked)}
          disabled={!rule.include_in_silver || !hasDots}
          style={{ accentColor: 'var(--accent-purple)', cursor: hasDots && rule.include_in_silver ? 'pointer' : 'not-allowed', opacity: hasDots ? 1 : 0.3 }}
          title={hasDots ? 'Remover puntos en esta columna' : 'No hay puntos en los datos crudos de esta columna'}
        />
      </td>

      <td style={{ minWidth: '70px', textAlign: 'center', padding: '0.65rem 0.5rem' }}>
        <input
          type="checkbox"
          checked={hasCommas && rule.clean_commas === true}
          onChange={(e) => onUpdateRule(col.column_name, 'clean_commas', e.target.checked)}
          disabled={!rule.include_in_silver || !hasCommas}
          style={{ accentColor: 'var(--accent-purple)', cursor: hasCommas && rule.include_in_silver ? 'pointer' : 'not-allowed', opacity: hasCommas ? 1 : 0.3 }}
          title={hasCommas ? 'Remover comas en esta columna' : 'No hay comas en los datos crudos de esta columna'}
        />
      </td>
    </tr>
  );
};
