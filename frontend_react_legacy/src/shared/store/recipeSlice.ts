import type { StateCreator } from 'zustand';
import type { ColumnSplitRule } from '../api/atomicityApi';
import type { ColumnCombineRule, CalculatedFieldRule, ColumnCleaningRule, SemanticMapping } from '../api/types';
import { projectApi } from '../../project/api/projectApi';

export interface CleaningRulesState {
  globalTrimSpaces: boolean;
  setGlobalTrimSpaces: (val: boolean) => void;
  globalCleanSpecialChars: boolean;
  setGlobalCleanSpecialChars: (val: boolean) => void;
  globalCleanAccentsAndN: boolean;
  setGlobalCleanAccentsAndN: (val: boolean) => void;
  globalCleanColons: boolean;
  setGlobalCleanColons: (val: boolean) => void;
  globalCleanDots: boolean;
  setGlobalCleanDots: (val: boolean) => void;
  globalCleanCommas: boolean;
  setGlobalCleanCommas: (val: boolean) => void;

  columnRules: Record<string, ColumnCleaningRule>;
  setColumnRules: (rules: Record<string, ColumnCleaningRule>) => void;
  updateColumnRule: (colName: string, field: string, value: any) => void;

  splitRules: ColumnSplitRule[];
  setSplitRules: (rules: ColumnSplitRule[]) => void;
  combineRules: ColumnCombineRule[];
  setCombineRules: (rules: ColumnCombineRule[]) => void;
  calculatedFieldRules: CalculatedFieldRule[];
  setCalculatedFieldRules: (rules: CalculatedFieldRule[]) => void;
  goldDimensions: string[];
  setGoldDimensions: (dims: string[]) => void;

  semanticMapping: SemanticMapping;
  setSemanticMapping: (mapping: SemanticMapping) => void;
  updateSemanticMapping: (field: keyof SemanticMapping, value: string | undefined) => void;

  loadRecipe: (projectId: string) => Promise<void>;
}

export const createRecipeSlice: StateCreator<CleaningRulesState, [], [], CleaningRulesState> = (set) => ({
  globalTrimSpaces: true,
  setGlobalTrimSpaces: (val) => set({ globalTrimSpaces: val }),
  globalCleanSpecialChars: false,
  setGlobalCleanSpecialChars: (val) => set({ globalCleanSpecialChars: val }),
  globalCleanAccentsAndN: false,
  setGlobalCleanAccentsAndN: (val) => set({ globalCleanAccentsAndN: val }),
  globalCleanColons: false,
  setGlobalCleanColons: (val) => set({ globalCleanColons: val }),
  globalCleanDots: false,
  setGlobalCleanDots: (val) => set({ globalCleanDots: val }),
  globalCleanCommas: false,
  setGlobalCleanCommas: (val) => set({ globalCleanCommas: val }),

  columnRules: {},
  setColumnRules: (rules) => set({ columnRules: rules }),
  updateColumnRule: (colName, field, value) => set((state) => ({
    columnRules: {
      ...state.columnRules,
      [colName]: {
        include_in_silver: true,
        new_column_name: '',
        null_imputation: 'DEFAULT',
        convert_to_category: false,
        user_overrode_type: field === 'target_data_type' ? true : ((state.columnRules[colName] as any)?.user_overrode_type || false),
        ...(state.columnRules[colName] || {}),
        [field]: value,
      } as ColumnCleaningRule,
    },
  })),

  splitRules: [],
  setSplitRules: (rules) => set({ splitRules: rules }),
  combineRules: [],
  setCombineRules: (rules) => set({ combineRules: rules }),
  calculatedFieldRules: [],
  setCalculatedFieldRules: (rules) => set({ calculatedFieldRules: rules }),
  goldDimensions: [],
  setGoldDimensions: (dims) => set({ goldDimensions: dims }),

  semanticMapping: {},
  setSemanticMapping: (mapping) => set({ semanticMapping: mapping }),
  updateSemanticMapping: (field, value) => set((state) => ({
    semanticMapping: { ...state.semanticMapping, [field]: value },
  })),

  loadRecipe: async (projectId: string) => {
    try {
      const recipe = await projectApi.getProjectRecipe(projectId);
      if (!recipe) return;

      set({
        globalTrimSpaces: recipe.global_trim_spaces ?? true,
        globalCleanSpecialChars: recipe.global_clean_special_chars ?? false,
        globalCleanAccentsAndN: recipe.global_clean_accents_and_n ?? false,
        globalCleanColons: recipe.global_clean_colons ?? false,
        globalCleanDots: recipe.global_clean_dots ?? false,
        globalCleanCommas: recipe.global_clean_commas ?? false,
      });

      if (recipe.column_rules) set({ columnRules: recipe.column_rules as Record<string, ColumnCleaningRule> });
      if (recipe.split_rules) set({ splitRules: recipe.split_rules });
      if (recipe.combine_rules) set({ combineRules: recipe.combine_rules });
      if (recipe.calculated_field_rules) set({ calculatedFieldRules: recipe.calculated_field_rules });
      if (recipe.gold_dimensions) set({ goldDimensions: recipe.gold_dimensions });
      if (recipe.semantic_mapping) set({ semanticMapping: recipe.semantic_mapping });
    } catch (err) {
      console.warn('Could not load recipe for project', projectId, err);
    }
  },
});
