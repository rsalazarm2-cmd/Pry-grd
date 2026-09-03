import type { StateCreator } from 'zustand';

export interface FilterState {
  // Bronze Filters
  bronzeSearch: string;
  setBronzeSearch: (val: string) => void;
  bronzeCol: string;
  setBronzeCol: (val: string) => void;
  bronzeLimit: number;
  setBronzeLimit: (val: number) => void;
  bronzeExcelFilters: Record<string, string[]>;

  // Silver Filters
  silverSearch: string;
  setSilverSearch: (val: string) => void;
  silverCol: string;
  setSilverCol: (val: string) => void;
  silverFilterStatus: string;
  setSilverFilterStatus: (val: string) => void;
  silverExcelFilters: Record<string, string[]>;

  // Gold Ledger Filters
  goldSearch: string;
  setGoldSearch: (val: string) => void;
  goldCol: string;
  setGoldCol: (val: string) => void;
  goldLedgerExcelFilters: Record<string, string[]>;

  // Gold Account Filters
  goldAccountSearch: string;
  setGoldAccountSearch: (val: string) => void;
  goldAccountCol: string;
  setGoldAccountCol: (val: string) => void;
  goldAccountExcelFilters: Record<string, string[]>;

  // Common Filter Handler
  handleApplyFilter: (
    layer: 'bronze' | 'silver' | 'goldLedger' | 'goldAccount',
    colName: string,
    selectedVals: string[] | undefined
  ) => void;
}

export const createFilterSlice: StateCreator<FilterState, [], [], FilterState> = (set) => ({
  bronzeSearch: '',
  setBronzeSearch: (val) => set({ bronzeSearch: val }),
  bronzeCol: 'TODOS',
  setBronzeCol: (val) => set({ bronzeCol: val }),
  bronzeLimit: 50,
  setBronzeLimit: (val) => set({ bronzeLimit: val }),
  bronzeExcelFilters: {},

  silverSearch: '',
  setSilverSearch: (val) => set({ silverSearch: val }),
  silverCol: 'TODOS',
  setSilverCol: (val) => set({ silverCol: val }),
  silverFilterStatus: 'TODOS',
  setSilverFilterStatus: (val) => set({ silverFilterStatus: val }),
  silverExcelFilters: {},

  goldSearch: '',
  setGoldSearch: (val) => set({ goldSearch: val }),
  goldCol: 'TODOS',
  setGoldCol: (val) => set({ goldCol: val }),
  goldLedgerExcelFilters: {},

  goldAccountSearch: '',
  setGoldAccountSearch: (val) => set({ goldAccountSearch: val }),
  goldAccountCol: 'TODOS',
  setGoldAccountCol: (val) => set({ goldAccountCol: val }),
  goldAccountExcelFilters: {},

  handleApplyFilter: (layer, colName, selectedVals) => set((state) => {
    const layerKey = `${layer}ExcelFilters` as keyof Pick<
      FilterState,
      'bronzeExcelFilters' | 'silverExcelFilters' | 'goldLedgerExcelFilters' | 'goldAccountExcelFilters'
    >;
    const currentFilters = { ...(state[layerKey] as Record<string, string[]>) };

    if (selectedVals && selectedVals.length > 0) {
      currentFilters[colName] = selectedVals;
    } else {
      delete currentFilters[colName];
    }
    return { [layerKey]: currentFilters } as any;
  }),
});
