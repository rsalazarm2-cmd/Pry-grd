import React, { useState } from 'react';
import { Network, Search, X, Check, ArrowRight } from 'lucide-react';
import { useMedallionStore } from '../../shared/store/medallionStore';
import { useMedallionQueries } from '../../shared/hooks/useMedallionQueries';
import { projectApi } from '../../project/api/projectApi';

interface SemanticMappingToolProps {
  onClose: () => void;
}

const MAPPING_FIELDS = [
  { id: 'ledger_col', label: 'Libro Contable (Ledger)', description: 'Identifica el libro contable de la transacción' },
  { id: 'account_col', label: 'Cuenta Contable', description: 'El identificador principal de la cuenta' },
  { id: 'entered_dr_col', label: 'Débitos Ingresados', description: 'Monto de débitos en moneda de origen' },
  { id: 'entered_cr_col', label: 'Créditos Ingresados', description: 'Monto de créditos en moneda de origen' },
  { id: 'accounted_dr_col', label: 'Débitos Contabilizados', description: 'Monto de débitos en moneda funcional' },
  { id: 'accounted_cr_col', label: 'Créditos Contabilizados', description: 'Monto de créditos en moneda funcional' },
  { id: 'date_col', label: 'Fecha Efectiva', description: 'Fecha de la transacción contable' },
  { id: 'category_col', label: 'Categoría de Asiento', description: 'Categoría o tipo de comprobante' }
] as const;

export const SemanticMappingTool: React.FC<SemanticMappingToolProps> = ({ onClose }) => {
  const [searchTerm, setSearchTerm] = useState('');
  const [isSaving, setIsSaving] = useState(false);
  const activeProject = useMedallionStore((s) => s.activeProject);
  
  const semanticMapping = useMedallionStore((s) => s.semanticMapping);
  const updateSemanticMapping = useMedallionStore((s) => s.updateSemanticMapping);
  
  const storeState = useMedallionStore();

  const { useSilverData } = useMedallionQueries(activeProject?.id);
  const { data: silverData } = useSilverData();

  const availableColumns = silverData?.columns?.map(c => c.column_name) || [];

  const handleSave = async () => {
    if (!activeProject) return;
    setIsSaving(true);
    try {
      const payload = {
        split_rules: storeState.splitRules,
        combine_rules: storeState.combineRules,
        calculated_field_rules: storeState.calculatedFieldRules,
        gold_dimensions: storeState.goldDimensions,
        semantic_mapping: semanticMapping
      };
      await projectApi.saveProjectRecipe(activeProject.id, payload as any);
      onClose();
    } catch (err) {
      console.error("Error saving semantic mapping", err);
      alert("Error al guardar el mapeo semántico");
    } finally {
      setIsSaving(false);
    }
  };

  const filteredFields = MAPPING_FIELDS.filter(f => 
    f.label.toLowerCase().includes(searchTerm.toLowerCase()) || 
    f.description.toLowerCase().includes(searchTerm.toLowerCase())
  );

  return (
    <div className="fixed inset-0 z-50 bg-black/60 backdrop-blur-sm flex items-center justify-center p-4">
      <div className="bg-gray-900 border border-gray-800 w-full max-w-3xl rounded-xl shadow-2xl flex flex-col max-h-[90vh]">
        
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-gray-800">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-indigo-500/20 text-indigo-400 rounded-lg">
              <Network className="w-6 h-6" />
            </div>
            <div>
              <h2 className="text-xl font-bold text-white">Mapeo Semántico (Semantic Mapping)</h2>
              <p className="text-sm text-gray-400">
                Enseña al motor SQL cómo interpretar tus datos para los modelos de Inteligencia de Negocios.
              </p>
            </div>
          </div>
          <button onClick={onClose} className="p-2 text-gray-400 hover:text-white rounded-lg hover:bg-gray-800 transition-colors">
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Search */}
        <div className="p-4 border-b border-gray-800 bg-gray-900/50">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-500" />
            <input
              type="text"
              placeholder="Buscar un campo semántico (Ej. Cuenta Contable, Débitos)..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full bg-black/40 border border-gray-800 rounded-lg pl-10 pr-4 py-2.5 text-sm text-white placeholder-gray-500 focus:outline-none focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 transition-all"
            />
          </div>
        </div>

        {/* Content */}
        <div className="flex-1 overflow-y-auto p-6 space-y-4">
          {filteredFields.map(field => {
            const currentValue = semanticMapping[field.id as keyof typeof semanticMapping] || '';
            const isMapped = !!currentValue;

            return (
              <div key={field.id} className={`p-4 rounded-xl border transition-all ${isMapped ? 'bg-indigo-500/5 border-indigo-500/30' : 'bg-gray-800/30 border-gray-700/50 hover:border-gray-600'}`}>
                <div className="flex items-center justify-between gap-4">
                  <div className="flex-1">
                    <div className="flex items-center gap-2 mb-1">
                      <h3 className={`font-medium ${isMapped ? 'text-indigo-400' : 'text-gray-200'}`}>{field.label}</h3>
                      {isMapped && <Check className="w-4 h-4 text-indigo-400" />}
                    </div>
                    <p className="text-sm text-gray-500">{field.description}</p>
                  </div>
                  
                  <div className="flex items-center gap-3">
                    <ArrowRight className="w-4 h-4 text-gray-600" />
                    <select
                      value={currentValue}
                      onChange={(e) => updateSemanticMapping(field.id as keyof typeof semanticMapping, e.target.value || undefined)}
                      className={`bg-gray-950 border ${isMapped ? 'border-indigo-500/50 text-white' : 'border-gray-700 text-gray-400'} rounded-lg px-4 py-2 text-sm focus:outline-none focus:border-indigo-500 min-w-[200px] max-w-[250px] truncate`}
                    >
                      <option value="">-- No mapeado --</option>
                      {availableColumns.map(col => (
                        <option key={col} value={col}>{col}</option>
                      ))}
                    </select>
                  </div>
                </div>
              </div>
            );
          })}
        </div>

        {/* Footer */}
        <div className="p-6 border-t border-gray-800 bg-gray-900/50 flex justify-end gap-3">
          <button
            onClick={onClose}
            className="px-4 py-2 text-sm font-medium text-gray-300 hover:text-white bg-transparent hover:bg-gray-800 rounded-lg transition-colors"
          >
            Cancelar
          </button>
          <button
            onClick={handleSave}
            disabled={isSaving}
            className="flex items-center gap-2 px-6 py-2 text-sm font-medium text-white bg-indigo-600 hover:bg-indigo-500 disabled:opacity-50 disabled:cursor-not-allowed rounded-lg shadow-lg shadow-indigo-500/20 transition-all"
          >
            {isSaving ? 'Guardando...' : 'Guardar Mapeo'}
            {!isSaving && <Check className="w-4 h-4" />}
          </button>
        </div>
      </div>
    </div>
  );
};
