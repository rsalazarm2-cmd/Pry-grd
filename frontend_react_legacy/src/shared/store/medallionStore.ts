import { create } from 'zustand';
import { createUISlice } from './uiSlice';
import type { MedallionUIState } from './uiSlice';
import { createFilterSlice } from './filterSlice';
import type { FilterState } from './filterSlice';
import { createRecipeSlice } from './recipeSlice';
import type { CleaningRulesState } from './recipeSlice';

export type MedallionStore = MedallionUIState & FilterState & CleaningRulesState;

export const useMedallionStore = create<MedallionStore>()((...a) => ({
  ...createUISlice(...a),
  ...createFilterSlice(...a),
  ...createRecipeSlice(...a),
}));

export type { MedallionUIState } from './uiSlice';
export type { FilterState } from './filterSlice';
export type { CleaningRulesState } from './recipeSlice';
