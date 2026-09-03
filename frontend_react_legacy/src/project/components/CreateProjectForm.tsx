import React from 'react';

interface CreateProjectFormProps {
  newName: string;
  setNewName: (val: string) => void;
  newDesc: string;
  setNewDesc: (val: string) => void;
  newDomain: string;
  setNewDomain: (val: string) => void;
  onSubmit: (e: React.FormEvent) => void;
  onCancel: () => void;
  canCancel: boolean;
}

export const CreateProjectForm: React.FC<CreateProjectFormProps> = ({
  newName,
  setNewName,
  newDesc,
  setNewDesc,
  newDomain,
  setNewDomain,
  onSubmit,
  onCancel,
  canCancel,
}) => {
  return (
    <form onSubmit={onSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
      <h3 style={{ fontSize: '1rem', fontWeight: 600, color: 'var(--accent-indigo)', margin: 0 }}>
        Crear Nuevo Proyecto Aislado
      </h3>

      <div>
        <label style={{ display: 'block', fontSize: '0.85rem', marginBottom: '0.4rem', color: 'var(--text-muted)' }}>
          Nombre del Proyecto *
        </label>
        <input
          type="text"
          required
          placeholder="Ej: Contabilidad Colombia 2025"
          value={newName}
          onChange={(e) => setNewName(e.target.value)}
          style={{ width: '100%', padding: '0.75rem 1rem', borderRadius: '8px', backgroundColor: 'var(--bg-input)', border: '1px solid var(--border-glass)', color: 'var(--text-main)' }}
        />
      </div>

      <div>
        <label style={{ display: 'block', fontSize: '0.85rem', marginBottom: '0.4rem', color: 'var(--text-muted)' }}>
          Descripción u Objetivo del Negocio
        </label>
        <textarea
          rows={2}
          placeholder="Ej: Ingesta mensual de asientos Oracle EBS para consolidación PyG"
          value={newDesc}
          onChange={(e) => setNewDesc(e.target.value)}
          style={{ width: '100%', padding: '0.75rem 1rem', borderRadius: '8px', backgroundColor: 'var(--bg-input)', border: '1px solid var(--border-glass)', color: 'var(--text-main)' }}
        />
      </div>

      <div>
        <label style={{ display: 'block', fontSize: '0.85rem', marginBottom: '0.4rem', color: 'var(--text-muted)' }}>
          Dominio ERP
        </label>
        <select
          value={newDomain}
          onChange={(e) => setNewDomain(e.target.value)}
          style={{ width: '100%', padding: '0.75rem 1rem', borderRadius: '8px', backgroundColor: 'var(--bg-input-select)', border: '1px solid var(--border-glass)', color: 'var(--text-main)' }}
        >
          <option value="GENERAL_LEDGER">General Ledger (Libro Mayor)</option>
          <option value="PAYROLL">Nómina y Talento</option>
          <option value="SALES_RMS">Ventas y Facturación (RMS)</option>
          <option value="ACCOUNTS_PAYABLE">Cuentas por Pagar (AP)</option>
        </select>
      </div>

      <div style={{ display: 'flex', gap: '0.75rem', justifyContent: 'flex-end', marginTop: '1rem' }}>
        {canCancel && (
          <button
            type="button"
            onClick={onCancel}
            style={{ padding: '0.6rem 1.25rem', borderRadius: '8px', border: '1px solid var(--border-glass)', background: 'transparent', color: 'var(--text-muted)', cursor: 'pointer' }}
          >
            Cancelar
          </button>
        )}
        <button
          type="submit"
          style={{ padding: '0.6rem 1.25rem', borderRadius: '8px', border: 'none', background: 'linear-gradient(135deg, var(--accent-indigo), var(--accent-purple))', color: 'white', fontWeight: 600, cursor: 'pointer' }}
        >
          Guardar y Crear Proyecto
        </button>
      </div>
    </form>
  );
};
