import React, { useEffect, useState } from 'react';
import { History, FileJson, ArrowRight, Check, X, ShieldCheck } from 'lucide-react';
import { projectApi } from "../../project/api/projectApi";

interface SilverLineageViewerProps {
  projectId?: string;
}

export const SilverLineageViewer: React.FC<SilverLineageViewerProps> = ({ projectId }) => {
  const [recipe, setRecipe] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!projectId) {
      setLoading(false);
      return;
    }
    
    setLoading(true);
    projectApi.getProjectRecipe(projectId)
      .then(res => {
        setRecipe(res);
      })
      .catch(err => {
        console.error("No se pudo cargar el linaje", err);
      })
      .finally(() => {
        setLoading(false);
      });
  }, [projectId]);

  if (loading) {
    return <div style={{ color: 'var(--text-muted)' }}>Cargando metadatos del archivo...</div>;
  }

  if (!recipe) {
    return null; // Si no hay receta, no se muestra nada
  }

  return (
    <div className="glass-card" style={{ marginBottom: '1.5rem', border: '1px solid var(--accent-emerald)' }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: '0.85rem', marginBottom: '1.25rem' }}>
        <div style={{ padding: '0.65rem', borderRadius: '10px', backgroundColor: 'rgba(16, 185, 129, 0.15)', color: 'var(--accent-emerald)', display: 'flex' }}>
          <ShieldCheck size={24} />
        </div>
        <div>
          <h3 style={{ fontSize: '1.1rem', fontWeight: 700, margin: '0 0 0.25rem 0', color: 'var(--text-main)' }}>
            Auditoría y Linaje de Datos
          </h3>
          <p style={{ fontSize: '0.84rem', color: 'var(--text-muted)', margin: 0 }}>
            Este panel muestra cómo se construyó el archivo actual <code style={{ color: 'var(--accent-emerald)' }}>silver.parquet</code> a partir de la Capa Bronce.
          </p>
        </div>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '1.5rem' }}>
        
        {/* Reglas Globales Aplicadas */}
        <div style={{ backgroundColor: 'rgba(255,255,255,0.02)', padding: '1rem', borderRadius: '8px', border: '1px solid var(--border-glass)' }}>
          <h4 style={{ fontSize: '0.9rem', color: 'var(--accent-cyan)', marginBottom: '1rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <FileJson size={16} /> Limpieza Global Aplicada
          </h4>
          <ul style={{ listStyle: 'none', padding: 0, margin: 0, display: 'flex', flexDirection: 'column', gap: '0.5rem', fontSize: '0.85rem', color: 'var(--text-main)' }}>
            <li style={{ display: 'flex', justifyContent: 'space-between' }}>
              <span>Recortar Espacios (Trim)</span>
              {recipe.global_trim_spaces ? <Check size={16} color="var(--accent-emerald)" /> : <X size={16} color="var(--accent-rose)" />}
            </li>
            <li style={{ display: 'flex', justifyContent: 'space-between' }}>
              <span>Forzar Mayúsculas</span>
              {recipe.global_uppercase ? <Check size={16} color="var(--accent-emerald)" /> : <X size={16} color="var(--accent-rose)" />}
            </li>
            <li style={{ display: 'flex', justifyContent: 'space-between' }}>
              <span>Limpiar Caracteres Especiales</span>
              {recipe.global_clean_special_chars ? <Check size={16} color="var(--accent-emerald)" /> : <X size={16} color="var(--accent-rose)" />}
            </li>
          </ul>
        </div>

        {/* Linaje de Columnas */}
        <div style={{ backgroundColor: 'rgba(255,255,255,0.02)', padding: '1rem', borderRadius: '8px', border: '1px solid var(--border-glass)' }}>
          <h4 style={{ fontSize: '0.9rem', color: 'var(--accent-cyan)', marginBottom: '1rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <History size={16} /> Mapeo de Columnas (Bronce ➔ Plata)
          </h4>
          
          <div style={{ maxHeight: '200px', overflowY: 'auto', paddingRight: '0.5rem' }}>
            {Object.keys(recipe.column_rules || {}).length === 0 ? (
              <p style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>No se registraron cambios específicos de alias o tipos.</p>
            ) : (
              <ul style={{ listStyle: 'none', padding: 0, margin: 0, display: 'flex', flexDirection: 'column', gap: '0.8rem', fontSize: '0.8rem' }}>
                {Object.entries(recipe.column_rules).map(([origCol, rules]: [string, any]) => (
                  <li key={origCol} style={{ display: 'flex', flexDirection: 'column', gap: '0.3rem', borderBottom: '1px dashed var(--border-glass)', paddingBottom: '0.5rem' }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                      <span style={{ color: 'var(--text-muted)' }}>{origCol}</span>
                      <ArrowRight size={14} style={{ color: 'var(--accent-emerald)' }} />
                      <span style={{ fontWeight: 600, color: 'white' }}>{rules.new_column_name || origCol}</span>
                    </div>
                    <div style={{ display: 'flex', gap: '1rem', color: 'var(--text-muted)', fontSize: '0.75rem' }}>
                      <span>Tipo: <strong style={{ color: 'var(--accent-cyan)' }}>{rules.target_data_type || 'INFERIDO'}</strong></span>
                      <span>Nulos: <strong>{rules.null_imputation}</strong></span>
                    </div>
                  </li>
                ))}
              </ul>
            )}
          </div>
        </div>

      </div>
    </div>
  );
};
