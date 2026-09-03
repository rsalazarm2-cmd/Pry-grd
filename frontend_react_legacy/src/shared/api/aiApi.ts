import { safeFetch } from './httpClient';

const API_BASE = '/api/ai';

export const aiApi = {
  async suggestMapping(sourceColumns: string[], targetLang: string = 'es'): Promise<Record<string, string>> {
    const params = new URLSearchParams();
    params.append('source_columns', sourceColumns.join(','));
    params.append('target_lang', targetLang);
    const queryString = params.toString();
    const data = await safeFetch<any>(`${API_BASE}/suggest-mapping?${queryString}`);
    return data?.suggested_mapping || data || {};
  },
};
