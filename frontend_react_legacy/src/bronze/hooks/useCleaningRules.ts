import { useState, useEffect } from 'react';
import type { ColumnSplitRule } from '../api/atomicityApi';
import type { ColumnCombineRule, CalculatedFieldRule } from '../api/types';
import { projectApi } from '../api/projectApi';

export function useCleaningRules(projectId?: string) {
  const [globalTrimSpaces, setGlobalTrimSpaces] = useState<boolean>(true);
  const [globalUppercase, setGlobalUppercase] = useState<boolean>(true);
  const [globalCleanSpecialChars, setGlobalCleanSpecialChars] = useState<boolean>(false);
  const [globalCleanAccentsAndN, setGlobalCleanAccentsAndN] = useState<boolean>(false);
  const [globalCleanColons, setGlobalCleanColons] = useState<boolean>(false);
  const [globalCleanDots, setGlobalCleanDots] = useState<boolean>(false);
  const [globalCleanCommas, setGlobalCleanCommas] = useState<boolean>(false);
  const [columnRules, setColumnRules] = useState<Record<string, any>>({});
  const [splitRules, setSplitRules] = useState<ColumnSplitRule[]>([]);
  
  const [combineRules, setCombineRules] = useState<ColumnCombineRule[]>([]);
  const [calculatedFieldRules, setCalculatedFieldRules] = useState<CalculatedFieldRule[]>([]);
  const [goldDimensions, setGoldDimensions] = useState<string[]>([]);

  // Hydrate state from recipe.json if it exists
  useEffect(() => {
    if (!projectId) return;
    
    projectApi.getProjectRecipe(projectId).then(recipe => {
      if (!recipe) return;
      
      setGlobalTrimSpaces(recipe.global_trim_spaces ?? true);
      setGlobalUppercase(recipe.global_uppercase ?? true);
      setGlobalCleanSpecialChars(recipe.global_clean_special_chars ?? false);
      setGlobalCleanAccentsAndN(recipe.global_clean_accents_and_n ?? false);
      setGlobalCleanColons(recipe.global_clean_colons ?? false);
      setGlobalCleanDots(recipe.global_clean_dots ?? false);
      setGlobalCleanCommas(recipe.global_clean_commas ?? false);
      
      if (recipe.column_rules) {
        setColumnRules(recipe.column_rules);
      }
      if (recipe.split_rules) {
        setSplitRules(recipe.split_rules);
      }
      if (recipe.combine_rules) {
        setCombineRules(recipe.combine_rules);
      }
      if (recipe.calculated_field_rules) {
        setCalculatedFieldRules(recipe.calculated_field_rules);
      }
      if (recipe.gold_dimensions) {
        setGoldDimensions(recipe.gold_dimensions);
      }
    }).catch(err => {
      console.warn("Could not load recipe for project", projectId, err);
    });
  }, [projectId]);

  const updateColumnRule = (colName: string, field: string, value: any) => {
    setColumnRules((prev) => ({
      ...prev,
      [colName]: {
        include_in_silver: true,
        new_column_name: '',
        null_imputation: 'DEFAULT',
        convert_to_category: false,
        user_overrode_type: field === 'target_data_type' ? true : (prev[colName]?.user_overrode_type || false),
        ...(prev[colName] || {}),
        [field]: value,
      },
    }));
  };

  return {
    globalTrimSpaces,
    setGlobalTrimSpaces,
    globalUppercase,
    setGlobalUppercase,
    globalCleanSpecialChars,
    setGlobalCleanSpecialChars,
    globalCleanAccentsAndN,
    setGlobalCleanAccentsAndN,
    globalCleanColons,
    setGlobalCleanColons,
    globalCleanDots,
    setGlobalCleanDots,
    globalCleanCommas,
    setGlobalCleanCommas,
    columnRules,
    setColumnRules,
    updateColumnRule,
    splitRules,
    setSplitRules,
    combineRules,
    setCombineRules,
    calculatedFieldRules,
    setCalculatedFieldRules,
    goldDimensions,
    setGoldDimensions
  };
}
