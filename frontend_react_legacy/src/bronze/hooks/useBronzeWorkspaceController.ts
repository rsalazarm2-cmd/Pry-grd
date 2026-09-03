import { useState, useEffect, useRef } from 'react';
import { useMedallionStore } from '../../shared/store/medallionStore';
import { useMedallionQueries } from '../../shared/hooks/useMedallionQueries';
import { NlpNamingService } from '../../ai/services/nlpNamingService';
import { inferSilverTypeFromColumn } from '../../shared/utils/dataTypeMapper';

export const useBronzeWorkspaceController = () => {
  const [searchTerm, setSearchTerm] = useState('');
  const [showConfig, setShowConfig] = useState(false);
  const [showConfirmProcess, setShowConfirmProcess] = useState(false);
  const [isSuggestingMapping, setIsSuggestingMapping] = useState(false);

  const state = useMedallionStore();
  const {
    profile,
    bronzeRecords,
    bronzeLoading,
    uploadMutation,
    transformMutation,
    clearDataMutation,
  } = useMedallionQueries();

  const columns = profile?.columns || [];
  const hasTriggeredMappingRef = useRef(false);

  useEffect(() => {
    if (columns.length > 0 && !hasTriggeredMappingRef.current) {
      const hasMappings = columns.some((col) => {
        const rule = state.columnRules[col.column_name];
        return rule && rule.new_column_name && rule.new_column_name !== col.column_name;
      });

      if (!hasMappings) {
        hasTriggeredMappingRef.current = true;
        handleSuggestMapping();
      }
    }
  }, [columns.length]);

  const activeNamesCount: Record<string, number> = {};
  columns.forEach((col) => {
    const rule = state.columnRules[col.column_name];
    if (!rule || rule.include_in_silver !== false) {
      const rawAlias = rule?.new_column_name ? rule.new_column_name.trim() : col.column_name;
      activeNamesCount[rawAlias.toUpperCase()] = (activeNamesCount[rawAlias.toUpperCase()] || 0) + 1;
    }
  });

  const duplicateNamesList = Object.keys(activeNamesCount).filter((name) => activeNamesCount[name] > 1);

  const filteredColumns = columns.filter((col) => {
    const alias = state.columnRules[col.column_name]?.new_column_name || '';
    return (
      col.column_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      alias.toLowerCase().includes(searchTerm.toLowerCase())
    );
  });

  const handleSuggestMapping = async (targetLang: string = 'es', specificCols?: string[]) => {
    if (!columns.length) return;
    setIsSuggestingMapping(true);
    try {
      const sourceCols = specificCols && specificCols.length > 0 ? specificCols : columns.map((c) => c.column_name);
      await NlpNamingService.applyNlpNamingSuggestions(sourceCols, state.updateColumnRule, targetLang);
    } catch (err) {
      console.error('Error obteniendo sugerencias de nombres NLP:', err);
    } finally {
      setIsSuggestingMapping(false);
    }
  };

  const handleSuggestedCleaning = async () => {
    if (!columns.length) return;

    columns.forEach((col) => {
      const isConstant = col.unique_count <= 1;
      const isAllNullOrZero = col.null_percentage >= 100.0;
      const shouldInclude = !(isConstant || isAllNullOrZero);

      state.updateColumnRule(col.column_name, 'include_in_silver', shouldInclude);

      if (shouldInclude) {
        const inferredType = inferSilverTypeFromColumn(col);

        if (inferredType === 'VARCHAR' || inferredType === 'TEXT') {
          state.updateColumnRule(col.column_name, 'clean_dots', true);
          state.updateColumnRule(col.column_name, 'clean_commas', true);
        }

        if (col.null_count > 0 && inferredType !== 'VARCHAR' && inferredType !== 'TEXT') {
          state.updateColumnRule(col.column_name, 'null_imputation', 'DEFAULT');
        }

        if (inferredType !== 'VARCHAR') {
          state.updateColumnRule(col.column_name, 'target_data_type', inferredType);
        }

        if (inferredType === 'VARCHAR' || inferredType === 'TEXT') {
          const isCategory = col.unique_count > 1 && (col.unique_count <= 50 || col.uniqueness_ratio < 0.05);
          state.updateColumnRule(col.column_name, 'convert_to_category', isCategory);
        }
      }
    });

    await handleSuggestMapping();
  };

  const handleProcessSilver = async () => {
    state.setTransformError(null);
    try {
      await transformMutation.mutateAsync({
        global_trim_spaces: state.globalTrimSpaces,
        global_clean_special_chars: state.globalCleanSpecialChars,
        global_clean_accents_and_n: state.globalCleanAccentsAndN,
        global_clean_colons: state.globalCleanColons,
        global_clean_dots: state.globalCleanDots,
        global_clean_commas: state.globalCleanCommas,
        column_rules: state.columnRules,
      });
      setShowConfirmProcess(false);
    } catch (err: any) {
      state.setTransformError(err?.message || 'Error al procesar la Capa Plata. Revisa la configuración.');
      setShowConfirmProcess(false);
    }
  };

  const handleResetProject = () => {
    if (
      confirm(
        '¿Estás seguro de limpiar todos los datos? Esta acción eliminará los archivos Parquet e ingestados, pero mantendrá las reglas de limpieza (receta) configuradas.'
      )
    ) {
      clearDataMutation.mutate(undefined, {
        onSuccess: () => {},
      });
    }
  };

  const allTranslateSelected = columns.length > 0 && columns.every((col) => state.columnRules[col.column_name]?.should_translate !== false);

  const handleToggleSelectAllTranslate = (checked: boolean) => {
    columns.forEach((col) => {
      state.updateColumnRule(col.column_name, 'should_translate', checked);
    });
  };

  return {
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
  };
};
