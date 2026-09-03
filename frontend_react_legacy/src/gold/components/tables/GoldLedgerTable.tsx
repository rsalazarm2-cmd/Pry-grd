import React from 'react';
import { Search, Award } from 'lucide-react';
import type { GoldBalanceItem } from '../../api/types';
import { ExcelColumnFilter } from "../../../shared/components/tables/ExcelColumnFilter";

interface GoldLedgerTableProps {
  goldBalances: GoldBalanceItem[] | undefined;
  goldLoading: boolean;
  goldSearch: string;
  onSearchChange: (val: string) => void;
  goldCol: string;
  onColChange: (val: string) => void;
  goldLedgerExcelFilters: Record<string, string[]>;
  onApplyExcelFilter: (colName: string, selectedVals: string[] | undefined) => void;
}

export const GoldLedgerTable: React.FC<GoldLedgerTableProps> = ({
  goldBalances,
  goldLoading,
  goldSearch,
  onSearchChange,
  goldCol,
  onColChange,
  goldLedgerExcelFilters,
  onApplyExcelFilter,
}) => {
  return (
    <div style={{ marginBottom: '2rem' }}>
      <div className="glass-card">
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem', flexWrap: 'wrap', gap: '1rem' }}>
          <div>
            <h4 style={{ fontSize: '1rem', fontWeight: 700, margin: '0 0 0.2rem 0', color: 'var(--accent-amber)', display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
              <Award size={18} style={{ color: 'var(--accent-amber)' }} />
              Datamart 1: Balances Agregados por Libro Contable y Moneda
            </h4>
            <p style={{ fontSize: '0.8rem', color: 'var(--text-muted)', margin: 0 }}>
              Generado automáticamente en <code style={{ color: 'var(--accent-amber)' }}>gold_balance_by_ledger.parquet</code>
            </p>
          </div>

          <div style={{ display: 'flex', gap: '0.5rem' }}>
            <div style={{ position: 'relative', width: '220px' }}>
              <Search size={14} style={{ position: 'absolute', left: '10px', top: '50%', transform: 'translateY(-50%)', color: 'var(--text-muted)' }} />
              <input
                type="text"
                placeholder="Buscar en Libros/Monedas..."
                value={goldSearch}
                onChange={(e) => onSearchChange(e.target.value)}
                style={{
                  width: '100%',
                  padding: '0.4rem 0.6rem 0.4rem 2rem',
                  borderRadius: '6px',
                  backgroundColor: 'var(--bg-input)',
                  border: '1px solid var(--border-glass)',
                  color: 'var(--text-main)',
                  fontSize: '0.8rem',
                }}
              />
            </div>
            <select
              value={goldCol}
              onChange={(e) => onColChange(e.target.value)}
              style={{
                padding: '0.4rem 0.6rem',
                borderRadius: '6px',
                backgroundColor: 'var(--bg-input-select)',
                border: '1px solid var(--border-glass)',
                color: 'var(--text-main)',
                fontSize: '0.8rem',
              }}
            >
              <option value="TODOS">Todas las Columnas</option>
              <option value="LEDGER_NAME">Libro Contable</option>
              <option value="CURRENCY">Moneda</option>
            </select>
          </div>
        </div>

        {goldLoading ? (
          <p style={{ color: 'var(--text-muted)' }}>Cargando balances de libro...</p>
        ) : goldBalances && goldBalances.length > 0 ? (
          <div style={{ overflowX: 'auto', border: '1px solid var(--border-glass)', borderRadius: '8px' }}>
            <table className="medallion-table">
              <thead>
                <tr>
                  <th>
                    <div style={{ display: 'inline-flex', alignItems: 'center' }}>
                      <span>Libro Contable ERP</span>
                      <ExcelColumnFilter layer="gold_ledger" columnName="LEDGER_NAME" selectedValues={goldLedgerExcelFilters['LEDGER_NAME']} onApplyFilter={onApplyExcelFilter} />
                    </div>
                  </th>
                  <th>
                    <div style={{ display: 'inline-flex', alignItems: 'center' }}>
                      <span>Moneda ISO</span>
                      <ExcelColumnFilter layer="gold_ledger" columnName="CURRENCY" selectedValues={goldLedgerExcelFilters['CURRENCY']} onApplyFilter={onApplyExcelFilter} />
                    </div>
                  </th>
                  <th>Líneas Asientos</th>
                  <th>Total Débitos</th>
                  <th>Total Créditos</th>
                  <th>Saldo Neto Contable</th>
                </tr>
              </thead>
              <tbody>
                {goldBalances.map((item, index) => (
                  <tr key={index}>
                    <td style={{ fontWeight: 700, color: 'var(--accent-cyan)' }}>{item.LEDGER_NAME}</td>
                    <td><span className="kpi-badge badge-info">{item.CURRENCY}</span></td>
                    <td>{item.TOTAL_JOURNAL_LINES ? item.TOTAL_JOURNAL_LINES.toLocaleString() : 0}</td>
                    <td>${Number(item.TOTAL_ENTERED_DR || 0).toLocaleString('es-CO', { minimumFractionDigits: 2 })}</td>
                    <td>${Number(item.TOTAL_ENTERED_CR || 0).toLocaleString('es-CO', { minimumFractionDigits: 2 })}</td>
                    <td style={{ color: Number(item.NET_ACCOUNTED_BALANCE || 0) < 0 ? 'var(--accent-rose)' : 'var(--accent-emerald)', fontWeight: 700 }}>
                      ${Number(item.NET_ACCOUNTED_BALANCE || 0).toLocaleString('es-CO', { minimumFractionDigits: 2 })}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : (
          <p style={{ color: 'var(--text-muted)' }}>{goldSearch ? `No se encontraron coincidencias para "${goldSearch}".` : 'Genera la Capa Oro para visualizar el resumen por libro.'}</p>
        )}
      </div>
    </div>
  );
};
