import { safeFetch } from "../../shared/api/httpClient";
import type { Project, CreateProjectPayload, TransformationRules } from "../../shared/api/types";

const API_BASE = '/api';

export const projectApi = {
  async getProjects(): Promise<Project[]> {
    return safeFetch<Project[]>(`${API_BASE}/projects`);
  },

  async createProject(payload: CreateProjectPayload): Promise<Project> {
    return safeFetch<Project>(`${API_BASE}/projects`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });
  },

  async deleteProject(projectId: string): Promise<{ success: boolean }> {
    return safeFetch<{ success: boolean }>(`${API_BASE}/projects/${projectId}`, {
      method: 'DELETE',
    });
  },

  async getProjectRecipe(projectId: string): Promise<TransformationRules | null> {
    const res = await fetch(`${API_BASE}/projects/${projectId}/recipe`);
    if (res.status === 404) return null;
    if (!res.ok) {
      const body = await res.text().catch(() => 'Unknown error');
      throw new Error(`HTTP ${res.status}: ${body}`);
    }
    return res.json();
  },

  async saveProjectRecipe(projectId: string, rules: TransformationRules): Promise<any> {
    return safeFetch(`${API_BASE}/projects/${projectId}/recipe`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(rules),
    });
  },
};
