import { safeFetch } from './httpClient';

export interface SegmentDefinition {
  index: number;
  suggested_alias: string;
  sample_value?: string;
}

export interface AtomicitySuggestion {
  column_name: string;
  suggested_clean_header?: string;
  delimiter: string;
  confidence_score: number;
  detected_segments_count: number;
  suggested_segments: SegmentDefinition[];
  sample_raw_values: string[];
}

export interface ColumnSplitRule {
  column_name: string;
  enabled: boolean;
  delimiter: string;
  keep_original: boolean;
  segments: SegmentDefinition[];
}

export const atomicityApi = {
  async getSuggestions(projectId?: string): Promise<AtomicitySuggestion[]> {
    const query = projectId ? `?project_id=${projectId}` : '';
    return safeFetch<AtomicitySuggestion[]>(`/api/medallion/atomicity-suggestions${query}`);
  },
};
