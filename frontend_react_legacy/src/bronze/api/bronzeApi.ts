import { safeFetch } from '../../shared/api/httpClient';
import type { BronzeResult, ColumnProfile, DatasetProfile, TabularResult } from '../../shared/api/types';

const API_BASE = '/api/bronze';

export const bronzeApi = {
  async profile(projectId?: string): Promise<DatasetProfile> {
    const query = projectId ? `?project_id=${projectId}` : '';
    return safeFetch<DatasetProfile>(`${API_BASE}/profile${query}`);
  },

  async getRecords(
    projectId?: string,
    limit: number = 50,
    search?: string,
    columnName?: string,
    filtersJson?: string
  ): Promise<Record<string, any>[]> {
    const params = new URLSearchParams();
    if (projectId) params.append('project_id', projectId);
    params.append('limit', limit.toString());
    if (search && search.trim()) params.append('search', search.trim());
    if (columnName && columnName !== 'TODOS') params.append('column_name', columnName);
    if (filtersJson && filtersJson.trim()) params.append('filters_json', filtersJson);

    const queryString = params.toString() ? `?${params.toString()}` : '';
    const data = await safeFetch<TabularResult>(`${API_BASE}/records${queryString}`);
    return data.rows;
  },

  async getColumnDetail(columnName: string, projectId?: string): Promise<ColumnProfile> {
    const query = projectId ? `?project_id=${projectId}` : '';
    return safeFetch<ColumnProfile>(`${API_BASE}/column-detail/${columnName}${query}`);
  },

  async getDistinctValues(columnName: string, projectId?: string): Promise<{ value: string; count: number }[]> {
    const query = projectId ? `?project_id=${projectId}` : '';
    return safeFetch<{ value: string; count: number }[]>(
      `${API_BASE}/distinct-values/${columnName}${query}`
    );
  },

  async ingest(projectId?: string): Promise<BronzeResult> {
    const query = projectId ? `?project_id=${projectId}` : '';
    return safeFetch<BronzeResult>(`${API_BASE}/ingest${query}`, { method: 'POST' });
  },

  async uploadCSV(file: File, projectId?: string): Promise<BronzeResult> {
    const formData = new FormData();
    formData.append('file', file);
    const query = projectId ? `?project_id=${projectId}` : '';

    return safeFetch<BronzeResult>(`${API_BASE}/upload-ingest${query}`, {
      method: 'POST',
      body: formData,
    });
  },
};
