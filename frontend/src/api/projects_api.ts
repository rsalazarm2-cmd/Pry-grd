/**
 * API Client para la gestión de proyectos reales en backend.
 * Endpoints: GET /api/projects, DELETE /api/projects/{project_id}
 */
import { apiGet, apiDelete } from './http_client'

export interface ProjectDTO {
  id: string
  name: string
  description?: string
  domain?: string
  created_at?: string
  storage_path?: string
  has_recipe?: boolean
}

export async function fetchProjectsList(): Promise<ProjectDTO[]> {
  return apiGet<ProjectDTO[]>('/projects')
}

export async function deleteProjectApi(projectId: string): Promise<{ success: boolean }> {
  return apiDelete<{ success: boolean }>(`/projects/${projectId}`)
}
