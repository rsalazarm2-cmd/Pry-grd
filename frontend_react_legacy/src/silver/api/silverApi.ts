import { safeFetch } from '../../shared/api/httpClient';
import type { DatasetProfile, SilverResult, TabularResult, TransformationRules } from '../../shared/api/types';

const API_BASE = '/api/silver';

export const silverApi = {
  async profile(projectId?: string): Promise<DatasetProfile> {
    const query = projectId ? `?project_id=${projectId}` : '';
    return safeFetch<DatasetProfile>(`${API_BASE}/profile${query}`);
  },

  async transform(rules?: Partial<TransformationRules>, projectId?: string): Promise<SilverResult> {
    const query = projectId ? `?project_id=${projectId}` : '';
    return safeFetch<SilverResult>(`${API_BASE}/transform${query}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(rules || {}),
    });
  },

  async getRecords(
    projectId?: string,
    qualityStatus?: string,
    search?: string,
    columnName?: string,
    filtersJson?: string
  ): Promise<Record<string, any>[]> {
    const params = new URLSearchParams();
    if (projectId) params.append('project_id', projectId);
    if (qualityStatus && qualityStatus !== 'TODOS') params.append('quality_status', qualityStatus);
    if (search && search.trim()) params.append('search', search.trim());
    if (columnName && columnName !== 'TODOS') params.append('column_name', columnName);
    if (filtersJson && filtersJson.trim()) params.append('filters_json', filtersJson);

    const queryString = params.toString() ? `?${params.toString()}` : '';
    const data = await safeFetch<TabularResult>(`${API_BASE}/records${queryString}`);
    return data.rows;
  },

  async getAtomicitySuggestions(projectId?: string): Promise<any[]> {
    const query = projectId ? `?project_id=${projectId}` : '';
    return safeFetch<any[]>(`${API_BASE}/atomicity-suggestions${query}`);
  },

  async getDistinctValues(columnName: string, projectId?: string): Promise<{ value: string; count: number }[]> {
    const query = projectId ? `?project_id=${projectId}` : '';
    return safeFetch<{ value: string; count: number }[]>(
      `${API_BASE}/distinct-values/${columnName}${query}`
    );
  },
};
