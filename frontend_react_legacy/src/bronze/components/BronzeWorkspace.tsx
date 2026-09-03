import React from 'react';
import { Sliders, Play, Loader2, Search, AlertTriangle } from 'lucide-react';
import { BronzeProfilingDiagnostic } from "./tables/BronzeProfilingDiagnostic";
import { BronzeTable } from "./tables/BronzeTable";
import { GlobalCleaningSwitches } from "../../cleaning/components/GlobalCleaningSwitches";
import { ConfirmOverwriteDialog } from "../../shared/components/common/ConfirmOverwriteDialog";
import { ColumnCleaningRow } from "../../cleaning/components/ColumnCleaningRow";
import { useBronzeWorkspaceController } from '../hooks/useBronzeWorkspaceController';

export const BronzeWorkspace: React.FC = () => {
  const {
    searchTerm,
    setSearchTerm,
    showConfig,
    setShowConfig,
    showConfirmProcess,
    setShowConfirmProcess,
    isSuggestingMapping,
    columns,
    filteredColumns,
    duplicateNamesList,
    allTranslateSelected,
    handleToggleSelectAllTranslate,
    state,
    profile,
    bronzeRecords,
    bronzeLoading,
    uploadMutation,
    transformMutation,
    clearDataMutation,
    handleSuggestMapping,
    handleSuggestedCleaning,
    handleProcessSilver,
    handleResetProject,
  } = useBronzeWorkspaceController();

  return (
    <div className="tab-pane" style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
      <BronzeProfilingDiagnostic
        profile={profile}
        onOpenCleaningModal={() => {
          setShowConfig(true);
          handleSuggestedCleaning();
          setTimeout(() => {
            document.getElementById('config-panel-bronze')?.scrollIntoView({ behavior: 'smooth' });
          }, 100);
        }}
      />

      {showConfig && (
        <div id="config-panel-bronze" className="glass-card" style={{ padding: '0', overflow: 'hidden' }}>
          <div style={{ padding: '1.2rem 1.5rem', backgroundColor: 'var(--bg-modal-header)', borderBottom: '1px solid var(--border-glass)', display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '1rem' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
              <div style={{ padding: '0.5rem', borderRadius: '8px', backgroundColor: 'rgba(79, 70, 229, 0.15)', color: 'var(--accent-indigo)', display: 'flex' }}><Sliders size={20} /></div>
              <div>
                <h3 style={{ fontSize: '1.1rem', fontWeight: 700, margin: 0, color: 'var(--text-main)' }}>Configuración de Transformación: Capa Bronce ➔ Capa Plata</h3>
                <p style={{ fontSize: '0.82rem', color: 'var(--text-muted)', margin: 0 }}>Aplica Tipado, Saneamiento de Texto, y Genera silver.parquet</p>
              </div>
            </div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', flexWrap: 'wrap' }}>
              {isSuggestingMapping && (
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem', padding: '0.55rem 1.1rem', borderRadius: '8px', backgroundColor: 'rgba(139, 92, 246, 0.15)', border: '1px solid rgba(139, 92, 246, 0.4)', color: 'var(--accent-purple)', fontWeight: 700, fontSize: '0.83rem' }}>
                  <Loader2 size={16} className="spin" /> Analizando (IA)...
                </div>
              )}
              <div style={{ display: 'inline-flex', alignItems: 'center', gap: '0.4rem' }}>
                <select id="nlp-lang-select" defaultValue="es" disabled={isSuggestingMapping} style={{ padding: '0.52rem 0.6rem', borderRadius: '8px', backgroundColor: 'rgba(139, 92, 246, 0.15)', border: '1px solid rgba(139, 92, 246, 0.4)', color: 'var(--accent-purple)', fontWeight: 700, fontSize: '0.82rem', cursor: 'pointer' }}>
                  <option value="es">🇪🇸 Traducir a Español</option>
                  <option value="en">🇺🇸 Traducir a Inglés</option>
                </select>
                <button
                  onClick={() => {
                    const sel = (document.getElementById('nlp-lang-select') as HTMLSelectElement)?.value || 'es';
                    const colsToTranslate = columns.filter((c) => state.columnRules[c.column_name]?.should_translate !== false).map((c) => c.column_name);
                    handleSuggestMapping(sel, colsToTranslate);
                  }}
                  disabled={isSuggestingMapping}
                  style={{ display: 'flex', alignItems: 'center', gap: '0.4rem', padding: '0.55rem 1.1rem', borderRadius: '8px', backgroundColor: 'rgba(139, 92, 246, 0.15)', border: '1px solid rgba(139, 92, 246, 0.4)', color: 'var(--accent-purple)', fontWeight: 700, fontSize: '0.83rem', cursor: isSuggestingMapping ? 'not-allowed' : 'pointer' }}
                >
                  {isSuggestingMapping ? <><Loader2 size={16} className="spin" /> Traduciendo con IA...</> : <>🤖 Auto-Alias IA</>}
                </button>
              </div>
              <button onClick={handleSuggestedCleaning} style={{ display: 'flex', alignItems: 'center', gap: '0.4rem', padding: '0.55rem 1.1rem', borderRadius: '8px', backgroundColor: 'rgba(16, 185, 129, 0.15)', border: '1px solid rgba(16, 185, 129, 0.4)', color: 'var(--accent-emerald)', fontWeight: 700, fontSize: '0.83rem', cursor: 'pointer' }}>🧹 Limpieza Sugerida</button>
              <button onClick={() => setShowConfirmProcess(true)} disabled={transformMutation.isPending} style={{ display: 'flex', alignItems: 'center', gap: '0.4rem', padding: '0.6rem 1.5rem', borderRadius: '8px', border: 'none', background: transformMutation.isPending ? 'gray' : 'linear-gradient(135deg, var(--accent-indigo), var(--accent-purple))', color: 'white', fontWeight: 700, fontSize: '0.88rem', cursor: transformMutation.isPending ? 'not-allowed' : 'pointer' }}>
                {transformMutation.isPending ? <><Loader2 size={18} className="spin" /> Procesando Bronce ➔ Plata...</> : <><Play size={18} /> 🚀 Procesar Bronce ➔ Generar Capa Plata</>}
              </button>
            </div>
          </div>
          <div style={{ padding: '1.25rem 1.5rem', display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
            {state.transformError && (
              <div style={{ padding: '0.85rem 1.25rem', borderRadius: '10px', backgroundColor: 'rgba(244, 63, 94, 0.15)', border: '1px solid var(--accent-rose)', color: 'var(--accent-rose)', fontSize: '0.88rem', fontWeight: 600, display: 'flex', alignItems: 'center', gap: '0.6rem' }}><AlertTriangle size={20} /><span>{state.transformError}</span></div>
            )}
            <GlobalCleaningSwitches
              globalTrimSpaces={state.globalTrimSpaces} onToggleTrim={state.setGlobalTrimSpaces}
              globalCleanSpecialChars={state.globalCleanSpecialChars} onToggleSpecialChars={state.setGlobalCleanSpecialChars}
              globalCleanAccentsAndN={state.globalCleanAccentsAndN} onToggleAccentsAndN={state.setGlobalCleanAccentsAndN}
              globalCleanColons={state.globalCleanColons} onToggleColons={state.setGlobalCleanColons}
              globalCleanDots={state.globalCleanDots} onToggleDots={state.setGlobalCleanDots}
              globalCleanCommas={state.globalCleanCommas} onToggleCommas={state.setGlobalCleanCommas}
            />
            <div style={{ position: 'relative' }}>
              <Search size={16} style={{ position: 'absolute', left: '12px', top: '50%', transform: 'translateY(-50%)', color: 'var(--text-muted)' }} />
              <input type="text" placeholder="Filtrar columnas..." value={searchTerm} onChange={(e) => setSearchTerm(e.target.value)} style={{ width: '100%', padding: '0.5rem 1rem 0.5rem 2.4rem', borderRadius: '8px', backgroundColor: 'var(--bg-input)', border: '1px solid var(--border-glass)', color: 'var(--text-main)', fontSize: '0.85rem' }} />
            </div>
            <div style={{ overflowX: 'auto', border: '1px solid var(--border-glass)', borderRadius: '12px', maxHeight: '560px', boxShadow: 'var(--card-shadow)', background: 'var(--bg-card)' }}>
              <table className="data-table" style={{ width: '100%', borderCollapse: 'separate', borderSpacing: 0 }}>
                <thead style={{ position: 'sticky', top: 0, zIndex: 10, backgroundColor: 'var(--table-header-bg)', backdropFilter: 'blur(10px)' }}>
                  <tr style={{ borderBottom: '2px solid var(--border-glass)' }}>
                    <th style={{ width: '50px', textAlign: 'center', padding: '0.85rem 0.5rem', color: 'var(--text-muted)', fontSize: '0.75rem', fontWeight: 800 }}>INCLUIR</th>
                    <th style={{ minWidth: '200px', padding: '0.85rem 0.85rem', color: 'var(--text-muted)', fontSize: '0.75rem', fontWeight: 800 }}>COLUMNA ORIGINAL</th>
                    <th style={{ minWidth: '270px', padding: '0.85rem 0.85rem', color: 'var(--text-muted)', fontSize: '0.75rem', fontWeight: 800 }}>
                      <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
                        <input type="checkbox" checked={allTranslateSelected} onChange={(e) => handleToggleSelectAllTranslate(e.target.checked)} title="Seleccionar / Deseleccionar todas las columnas para traducción IA" style={{ accentColor: 'var(--accent-purple)', transform: 'scale(1.1)', cursor: 'pointer' }} />
                        <span>ALIAS PLATA</span>
                      </div>
                    </th>
                    <th style={{ minWidth: '180px', padding: '0.85rem 0.85rem', color: 'var(--text-muted)', fontSize: '0.75rem', fontWeight: 800 }}>TIPO DATO PLATA</th>
                    <th style={{ width: '80px', textAlign: 'center', padding: '0.85rem 0.5rem', color: 'var(--text-muted)', fontSize: '0.75rem', fontWeight: 800 }}>ENUM</th>
                    <th style={{ minWidth: '240px', padding: '0.85rem 0.85rem', color: 'var(--text-muted)', fontSize: '0.75rem', fontWeight: 800 }}>TRATAMIENTO DE NULOS</th>
                    <th style={{ width: '70px', textAlign: 'center', padding: '0.85rem 0.5rem', color: 'var(--text-muted)', fontSize: '0.75rem', fontWeight: 800 }}>. (Puntos)</th>
                    <th style={{ width: '70px', textAlign: 'center', padding: '0.85rem 0.5rem', color: 'var(--text-muted)', fontSize: '0.75rem', fontWeight: 800 }}>, (Comas)</th>
                  </tr>
                </thead>
                <tbody>
                  {filteredColumns.map((col) => {
                    const rule = state.columnRules[col.column_name] || {};
                    const rawAlias = rule.new_column_name ? rule.new_column_name.trim() : col.column_name;
                    const isDuplicateAlias = (rule.include_in_silver !== false) && (duplicateNamesList.includes(rawAlias.toUpperCase()));
                    return (
                      <ColumnCleaningRow
                        key={col.column_name}
                        col={col}
                        rule={rule}
                        duplicateNamesList={duplicateNamesList}
                        onUpdateRule={state.updateColumnRule}
                        onHoverType={() => {}}
                      />
                    );
                  })}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      )}

      {showConfirmProcess && (
        <ConfirmOverwriteDialog
          isOpen={showConfirmProcess}
          onClose={() => setShowConfirmProcess(false)}
          onConfirm={handleProcessSilver}
          isProcessing={transformMutation.isPending}
          duplicateNamesList={duplicateNamesList}
        />
      )}

      <BronzeTable
        profile={profile}
        showConfig={showConfig}
        onToggleConfig={() => setShowConfig(!showConfig)}
        bronzeRecords={bronzeRecords}
        bronzeLoading={bronzeLoading}
        bronzeSearch={state.bronzeSearchTerm}
        onSearchChange={state.setBronzeSearchTerm}
        bronzeCol={state.bronzeCol}
        onColChange={state.setBronzeCol}
        bronzeExcelFilters={state.bronzeExcelFilters}
        onApplyExcelFilter={(c, v) => state.handleApplyFilter('bronze', c, v)}
        bronzeLimit={state.bronzeLimit}
        onLimitChange={state.setBronzeLimit}
        onFileUpload={(e) => e.target.files?.[0] && uploadMutation.mutate(e.target.files[0])}
        isUploading={uploadMutation.isPending}
        onResetProject={handleResetProject}
        isDeleting={clearDataMutation.isPending}
      />
    </div>
  );
};
