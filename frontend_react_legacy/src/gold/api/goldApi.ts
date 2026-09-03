import { safeFetch } from '../../shared/api/httpClient';
import type { GoldBalanceItem, TabularResult } from '../../shared/api/types';

const API_BASE = '/api/gold';

export const goldApi = {
  async getBalances(
    projectId?: string,
    search?: string,
    columnName?: string,
    filtersJson?: string
  ): Promise<GoldBalanceItem[]> {
    const params = new URLSearchParams();
    if (projectId) params.append('project_id', projectId);
    if (search && search.trim()) params.append('search', search.trim());
    if (columnName && columnName !== 'TODOS') params.append('column_name', columnName);
    if (filtersJson && filtersJson.trim()) params.append('filters_json', filtersJson);

    const queryString = params.toString() ? `?${params.toString()}` : '';
    const data = await safeFetch<TabularResult>(`${API_BASE}/balances${queryString}`);
    return data.rows as GoldBalanceItem[];
  },

  async getAccountBalances(
    projectId?: string,
    search?: string,
    columnName?: string,
    filtersJson?: string
  ): Promise<Record<string, any>[]> {
    const params = new URLSearchParams();
    if (projectId) params.append('project_id', projectId);
    if (search && search.trim()) params.append('search', search.trim());
    if (columnName && columnName !== 'TODOS') params.append('column_name', columnName);
    if (filtersJson && filtersJson.trim()) params.append('filters_json', filtersJson);

    const queryString = params.toString() ? `?${params.toString()}` : '';
    const data = await safeFetch<TabularResult>(`${API_BASE}/account-balances${queryString}`);
    return data.rows;
  },

  async getDistinctValues(table: 'ledger' | 'account', columnName: string, projectId?: string): Promise<{ value: string; count: number }[]> {
    const query = projectId ? `?project_id=${projectId}` : '';
    return safeFetch<{ value: string; count: number }[]>(
      `${API_BASE}/distinct-values/${table}/${columnName}${query}`
    );
  },
};
