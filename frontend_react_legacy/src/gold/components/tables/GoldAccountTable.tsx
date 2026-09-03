import React from 'react';
import { Search, Award } from 'lucide-react';
import { ExcelColumnFilter } from "../../../shared/components/tables/ExcelColumnFilter";

interface GoldAccountTableProps {
  goldAccountBalances: Record<string, any>[] | undefined;
  goldAccountLoading: boolean;
  goldAccountSearch: string;
  onSearchChange: (val: string) => void;
  goldAccountCol: string;
  onColChange: (val: string) => void;
  goldAccountExcelFilters: Record<string, string[]>;
  onApplyExcelFilter: (colName: string, selectedVals: string[] | undefined) => void;
}

export const GoldAccountTable: React.FC<GoldAccountTableProps> = ({
  goldAccountBalances,
  goldAccountLoading,
  goldAccountSearch,
  onSearchChange,
  goldAccountCol,
  onColChange,
  goldAccountExcelFilters,
  onApplyExcelFilter,
}) => {
  const standardCols = ['ACCOUNT_SEGMENT', 'TOTAL_TRANSACTIONS', 'TOTAL_DEBIT', 'TOTAL_CREDIT', 'NET_BALANCE'];
  const dynamicCols = goldAccountBalances && goldAccountBalances.length > 0
    ? Object.keys(goldAccountBalances[0]).filter(k => !standardCols.includes(k))
    : [];

  return (
    <div>
      <div className="glass-card">
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem', flexWrap: 'wrap', gap: '1rem' }}>
          <div>
            <h4 style={{ fontSize: '1rem', fontWeight: 700, margin: '0 0 0.2rem 0', color: 'var(--accent-emerald)', display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
              <Award size={18} style={{ color: 'var(--accent-emerald)' }} />
              Datamart 2: Balances por Cuenta Contable y Segmentos Atomizados
            </h4>
            <p style={{ fontSize: '0.8rem', color: 'var(--text-muted)', margin: 0 }}>
              Generado automáticamente en <code style={{ color: 'var(--accent-emerald)' }}>gold_balance_by_account.parquet</code>
            </p>
          </div>

          <div style={{ display: 'flex', gap: '0.5rem' }}>
            <div style={{ position: 'relative', width: '220px' }}>
              <Search size={14} style={{ position: 'absolute', left: '10px', top: '50%', transform: 'translateY(-50%)', color: 'var(--text-muted)' }} />
              <input
                type="text"
                placeholder="Buscar por segmento de cuenta..."
                value={goldAccountSearch}
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
              value={goldAccountCol}
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
              <option value="ACCOUNT_SEGMENT">Segmento Cuenta Principal</option>
              {dynamicCols.map(col => (
                <option key={col} value={col}>{col}</option>
              ))}
            </select>
          </div>
        </div>

        {goldAccountLoading ? (
          <p style={{ color: 'var(--text-muted)' }}>Cargando balances de cuentas contables...</p>
        ) : goldAccountBalances && goldAccountBalances.length > 0 ? (
          <div style={{ overflowX: 'auto', border: '1px solid var(--border-glass)', borderRadius: '8px' }}>
            <table className="medallion-table">
              <thead>
                <tr>
                  <th>
                    <div style={{ display: 'inline-flex', alignItems: 'center' }}>
                      <span>Segmento Cuenta Principal</span>
                      <ExcelColumnFilter layer="gold_account" columnName="ACCOUNT_SEGMENT" selectedValues={goldAccountExcelFilters['ACCOUNT_SEGMENT']} onApplyFilter={onApplyExcelFilter} />
                    </div>
                  </th>
                  {dynamicCols.map(col => (
                    <th key={col}>
                      <div style={{ display: 'inline-flex', alignItems: 'center' }}>
                        <span>{col}</span>
                        <ExcelColumnFilter layer="gold_account" columnName={col} selectedValues={goldAccountExcelFilters[col]} onApplyFilter={onApplyExcelFilter} />
                      </div>
                    </th>
                  ))}
                  <th>Total Transacciones</th>
                  <th>Débitos</th>
                  <th>Créditos</th>
                  <th>Saldo Neto Cuenta</th>
                </tr>
              </thead>
              <tbody>
                {goldAccountBalances.map((item: any, index: number) => (
                  <tr key={index}>
                    <td style={{ color: 'var(--accent-cyan)', fontWeight: 700, fontFamily: 'var(--font-mono)' }}>{item.ACCOUNT_SEGMENT}</td>
                    {dynamicCols.map(col => (
                      <td key={col} style={{ color: 'var(--text-main)', fontFamily: 'var(--font-mono)', fontSize: '0.85rem' }}>
                        {item[col]}
                      </td>
                    ))}
                    <td>{item.TOTAL_TRANSACTIONS ? item.TOTAL_TRANSACTIONS.toLocaleString() : 0}</td>
                    <td>${Number(item.TOTAL_DEBIT || 0).toLocaleString('es-CO', { minimumFractionDigits: 2 })}</td>
                    <td>${Number(item.TOTAL_CREDIT || 0).toLocaleString('es-CO', { minimumFractionDigits: 2 })}</td>
                    <td style={{ color: Number(item.NET_BALANCE || 0) < 0 ? 'var(--accent-rose)' : 'var(--accent-emerald)', fontWeight: 700 }}>
                      ${Number(item.NET_BALANCE || 0).toLocaleString('es-CO', { minimumFractionDigits: 2 })}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : (
          <p style={{ color: 'var(--text-muted)' }}>{goldAccountSearch ? `No se encontraron coincidencias para "${goldAccountSearch}".` : 'Genera la Capa Oro para visualizar el resumen por cuenta.'}</p>
        )}
      </div>
    </div>
  );
};
