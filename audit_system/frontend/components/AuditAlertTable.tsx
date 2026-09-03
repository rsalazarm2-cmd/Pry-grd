import React from 'react';
import { AlertTriangle, ShieldAlert, CheckCircle, RefreshCw } from 'lucide-react';
import { useAuditIntegrity } from '../hooks/useAuditIntegrity';

interface AuditAlertTableProps {
  parquetPath: string;
}

export const AuditAlertTable: React.FC<AuditAlertTableProps> = ({ parquetPath }) => {
  const { report, isLoading, isError, refetch } = useAuditIntegrity(parquetPath);

  if (isLoading) {
    return (
      <div style={{ textAlign: 'center', padding: '2rem', color: 'var(--accent-amber)' }}>
        <RefreshCw size={24} className="spin" style={{ margin: '0 auto 0.5rem auto' }} />
        <p>Analizando integridad de asientos contables en DuckDB...</p>
      </div>
    );
  }

  if (isError || !report) {
    return (
      <div style={{ padding: '1rem', borderRadius: '8px', backgroundColor: 'rgba(239, 68, 68, 0.1)', color: 'var(--accent-rose)' }}>
        <p>⚠️ No se pudo ejecutar el diagnóstico forense sobre {parquetPath}.</p>
      </div>
    );
  }

  return (
    <div style={{ border: '1px solid var(--border-glass)', borderRadius: '12px', padding: '1.25rem', backgroundColor: 'var(--bg-card)' }}>
      {/* Resumen KPIs */}
      <div style={{ display: 'flex', gap: '1rem', marginBottom: '1.25rem', flexWrap: 'wrap' }}>
        <div style={{ flex: 1, padding: '0.75rem', borderRadius: '8px', backgroundColor: 'rgba(56, 189, 248, 0.1)', border: '1px solid var(--accent-cyan)' }}>
          <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>Asientos Analizados</span>
          <h4 style={{ margin: 0, fontSize: '1.2rem', color: 'var(--accent-cyan)' }}>{report.total_asientos_analizados.toLocaleString()}</h4>
        </div>
        <div style={{ flex: 1, padding: '0.75rem', borderRadius: '8px', backgroundColor: 'rgba(245, 158, 11, 0.1)', border: '1px solid var(--accent-amber)' }}>
          <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>Descuadres Partida Doble</span>
          <h4 style={{ margin: 0, fontSize: '1.2rem', color: 'var(--accent-amber)' }}>{report.total_descuadres_detectados}</h4>
        </div>
        <div style={{ flex: 1, padding: '0.75rem', borderRadius: '8px', backgroundColor: 'rgba(239, 68, 68, 0.1)', border: '1px solid var(--accent-rose)' }}>
          <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>Violaciones SoD (Maker=Checker)</span>
          <h4 style={{ margin: 0, fontSize: '1.2rem', color: 'var(--accent-rose)' }}>{report.total_violaciones_sod}</h4>
        </div>
      </div>

      {/* Tabla de Alertas de Descuadre */}
      <h4 style={{ fontSize: '0.95rem', fontWeight: 700, color: 'var(--accent-amber)', marginBottom: '0.75rem', display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
        <AlertTriangle size={18} /> Asientos Descuadrados Detectados
      </h4>

      {report.alertas_descuadre.length === 0 ? (
        <div style={{ padding: '0.75rem', color: 'var(--accent-emerald)', display: 'flex', alignItems: 'center', gap: '0.5rem', fontSize: '0.85rem' }}>
          <CheckCircle size={16} /> 100% de la muestra cumple la integridad de partida doble y coincidencia de cabecera.
        </div>
      ) : (
        <div style={{ overflowX: 'auto', marginBottom: '1.5rem' }}>
          <table className="medallion-table" style={{ width: '100%', fontSize: '0.82rem' }}>
            <thead>
              <tr>
                <th>FOLIO_ASIENTO</th>
                <th>PERIODO</th>
                <th>CARGOS (DEBE)</th>
                <th>ABONOS (HABER)</th>
                <th>DIFERENCIA</th>
              </tr>
            </thead>
            <tbody>
              {report.alertas_descuadre.map((d, idx) => (
                <tr key={idx}>
                  <td style={{ fontWeight: 700 }}>{d.FOLIO_ASIENTO}</td>
                  <td>{d.PERIODO_CONTABLE}</td>
                  <td>${Number(d.TOTAL_CARGOS_CALCULADO).toLocaleString()}</td>
                  <td>${Number(d.TOTAL_ABONOS_CALCULADO).toLocaleString()}</td>
                  <td style={{ color: 'var(--accent-rose)', fontWeight: 700 }}>${Number(d.DIFERENCIA_DESCUADRE).toLocaleString()}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {/* Tabla de Violaciones SoD */}
      <h4 style={{ fontSize: '0.95rem', fontWeight: 700, color: 'var(--accent-rose)', marginBottom: '0.75rem', display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
        <ShieldAlert size={18} /> Violaciones de Segregación de Funciones (Maker == Checker)
      </h4>

      {report.alertas_sod.length === 0 ? (
        <div style={{ padding: '0.75rem', color: 'var(--accent-emerald)', display: 'flex', alignItems: 'center', gap: '0.5rem', fontSize: '0.85rem' }}>
          <CheckCircle size={16} /> Ningún usuario registró y aprobó el mismo asiento contable.
        </div>
      ) : (
        <div style={{ overflowX: 'auto' }}>
          <table className="medallion-table" style={{ width: '100%', fontSize: '0.82rem' }}>
            <thead>
              <tr>
                <th>FOLIO_ASIENTO</th>
                <th>REGISTRADOR (MAKER)</th>
                <th>APROBADOR (CHECKER)</th>
                <th>MONTO TOTAL</th>
                <th>RIESGO</th>
              </tr>
            </thead>
            <tbody>
              {report.alertas_sod.map((s, idx) => (
                <tr key={idx}>
                  <td style={{ fontWeight: 700 }}>{s.FOLIO_ASIENTO}</td>
                  <td style={{ color: 'var(--accent-rose)' }}>{s.USUARIO_REGISTRADOR}</td>
                  <td style={{ color: 'var(--accent-rose)' }}>{s.USUARIO_APROBADOR}</td>
                  <td>${Number(s.MONTO_TOTAL_ASIENTO).toLocaleString()}</td>
                  <td><span style={{ padding: '0.15rem 0.4rem', borderRadius: '4px', backgroundColor: 'rgba(239, 68, 68, 0.2)', color: 'var(--accent-rose)', fontWeight: 700 }}>{s.NIVEL_RIESGO}</span></td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
};
