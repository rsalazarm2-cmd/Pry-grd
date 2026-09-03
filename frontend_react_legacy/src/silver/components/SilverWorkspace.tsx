import React from 'react';
import { Award, Play, Loader2, CheckCircle2 } from 'lucide-react';
import { SilverProfilingDiagnostic } from "./tables/SilverProfilingDiagnostic";
import { SilverTable } from "./tables/SilverTable";
import { AtomizeTool } from "../../transformations/components/AtomizeTool";
import { CombineColumnsTool } from "../../transformations/components/CombineColumnsTool";
import { CalculatedFieldsTool } from "../../transformations/components/CalculatedFieldsTool";
import { SilverDimensionsTool } from "../../transformations/components/SilverDimensionsTool";
import { SemanticMappingTool } from "../../transformations/components/SemanticMappingTool";
import { SilverLineageViewer } from './SilverLineageViewer';
import { useSilverWorkspaceController } from "../hooks/useSilverWorkspaceController";

export const SilverWorkspace: React.FC = () => {
  const ctrl = useSilverWorkspaceController();

  return (
    <div className="tab-pane" style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
      <SilverProfilingDiagnostic
        profile={ctrl.profile}
        onOpenValueTools={ctrl.toggleValueTools}
      />

      {ctrl.showConfig && (
        <div id="config-panel-silver" className="glass-card" style={{ padding: '0', overflow: 'hidden' }}>
          <div style={{ padding: '1.2rem 1.5rem', backgroundColor: 'var(--bg-modal-header)', borderBottom: '1px solid var(--border-glass)', display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '1rem' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
              <div style={{ padding: '0.5rem', borderRadius: '8px', backgroundColor: 'rgba(245, 158, 11, 0.15)', color: 'var(--accent-amber)', display: 'flex' }}>
                <Award size={20} />
              </div>
              <div>
                <h3 style={{ fontSize: '1.1rem', fontWeight: 700, margin: 0, color: 'var(--text-main)' }}>Configuración de Funcionalidades de Valor Agregado</h3>
                <p style={{ fontSize: '0.82rem', color: 'var(--text-muted)', margin: 0 }}>Aplica atomización, combinaciones y campos calculados a la Capa Plata.</p>
              </div>
            </div>
          </div>

          <div style={{ padding: '1.25rem 1.5rem', display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
            <AtomizeTool columns={ctrl.profile?.columns || []} splitRules={ctrl.state.splitRules} onUpdateRules={ctrl.state.setSplitRules} />
            <CombineColumnsTool columns={ctrl.profile?.columns || []} combineRules={ctrl.state.combineRules} onUpdateRules={ctrl.state.setCombineRules} />
            <CalculatedFieldsTool columns={ctrl.profile?.columns || []} calculatedFieldRules={ctrl.state.calculatedFieldRules} onUpdateRules={ctrl.state.setCalculatedFieldRules} />
            {ctrl.showDimensions && (
              <SilverDimensionsTool columns={ctrl.profile?.columns || []} silverRecords={ctrl.silverRecords} goldDimensions={ctrl.state.goldDimensions} onUpdateDimensions={ctrl.state.setGoldDimensions} onClose={() => ctrl.setShowDimensions(false)} />
            )}
            {ctrl.showSemanticMapping && (
              <SemanticMappingTool columns={ctrl.profile?.columns || []} onClose={() => ctrl.setShowSemanticMapping(false)} />
            )}
            <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '1rem', paddingTop: '1rem', borderTop: '1px solid var(--border-glass)' }}>
              <button onClick={() => ctrl.setShowSemanticMapping(true)} className="px-4 py-2 text-sm font-medium bg-indigo-500/10 text-indigo-400 hover:bg-indigo-500/20 border border-indigo-500/20 rounded-lg">Mapeo Semántico</button>
              <button onClick={() => ctrl.setShowDimensions(true)} className="px-4 py-2 text-sm font-medium bg-indigo-500/10 text-indigo-400 hover:bg-indigo-500/20 border border-indigo-500/20 rounded-lg">Dimensiones Plata</button>
              <button onClick={ctrl.handleProcessSilver} disabled={ctrl.isProcessing} style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', padding: '0.65rem 1.6rem', borderRadius: '8px', border: 'none', background: ctrl.isProcessing ? 'gray' : 'linear-gradient(135deg, var(--accent-orange), var(--accent-rose))', color: 'white', fontWeight: 700, fontSize: '0.88rem', cursor: ctrl.isProcessing ? 'not-allowed' : 'pointer' }}>
                {ctrl.isProcessing ? <><Loader2 size={18} className="spin" /> Procesando...</> : <><Play size={18} /> Aplicar Transformaciones y Guardar Datamart Plata</>}
              </button>
            </div>
          </div>
        </div>
      )}

      {ctrl.showLineage && <SilverLineageViewer projectId={ctrl.state.activeProject?.id} />}

      <SilverTable
        profile={ctrl.profile}
        silverRecords={ctrl.silverRecords}
        silverLoading={ctrl.silverLoading}
        silverFilterStatus={ctrl.state.silverFilterStatus}
        onStatusChange={ctrl.state.setSilverFilterStatus}
        silverSearch={ctrl.state.silverSearch}
        onSearchChange={ctrl.state.setSilverSearch}
        silverCol={ctrl.state.silverCol}
        onColChange={ctrl.state.setSilverCol}
        silverExcelFilters={ctrl.state.silverExcelFilters}
        onApplyExcelFilter={(c, v) => ctrl.state.handleApplyFilter('silver', c, v)}
        projectId={ctrl.state.activeProject?.id}
      />
    </div>
  );
};
