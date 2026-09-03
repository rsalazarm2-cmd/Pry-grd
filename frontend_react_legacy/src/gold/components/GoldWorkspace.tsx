import React from 'react';
import { GoldLedgerTable } from "./tables/GoldLedgerTable";
import { GoldAccountTable } from "./tables/GoldAccountTable";
import { useMedallionStore } from "../../shared/store/medallionStore";
import { useMedallionQueries } from "../../shared/hooks/useMedallionQueries";

export const GoldWorkspace: React.FC = () => {
  const state = useMedallionStore();
  const { 
    goldBalances, goldLoading, 
    goldAccountBalances, goldAccountLoading 
  } = useMedallionQueries();

  return (
    <div className="tab-pane">
      <GoldLedgerTable
        goldBalances={goldBalances}
        goldLoading={goldLoading}
        goldSearch={state.goldSearch}
        onSearchChange={state.setGoldSearch}
        goldCol={state.goldCol}
        onColChange={state.setGoldCol}
        goldLedgerExcelFilters={state.goldLedgerExcelFilters}
        onApplyExcelFilter={(c, v) => state.handleApplyFilter('goldLedger', c, v)}
      />

      <GoldAccountTable
        goldAccountBalances={goldAccountBalances}
        goldAccountLoading={goldAccountLoading}
        goldAccountSearch={state.goldAccountSearch}
        onSearchChange={state.setGoldAccountSearch}
        goldAccountCol={state.goldAccountCol}
        onColChange={state.setGoldAccountCol}
        goldAccountExcelFilters={state.goldAccountExcelFilters}
        onApplyExcelFilter={(c, v) => state.handleApplyFilter('goldAccount', c, v)}
      />
    </div>
  );
};
