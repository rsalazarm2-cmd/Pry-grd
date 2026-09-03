/**
 * Cliente HTTP base para la API REST del backend.
 * Wrapper sobre fetch con tipado estricto, inyección de project_id y manejo de errores.
 */

const BASE_URL = '/api'

export class ApiError extends Error {
  constructor(
    public readonly status: number,
    message: string,
  ) {
    super(message)
    this.name = 'ApiError'
  }
}

function appendProjectId(path: string): string {
  const activeProjectId = localStorage.getItem('active_project_id')
  if (!activeProjectId) return path

  try {
    const url = new URL(path, 'http://localhost')
    if (!url.searchParams.has('project_id')) {
      url.searchParams.set('project_id', activeProjectId)
    }
    return url.pathname + url.search
  } catch {
    return path
  }
}

/** Ejecuta un GET tipado contra la API REST. */
export async function apiGet<T>(path: string): Promise<T> {
  const target = `${BASE_URL}${appendProjectId(path)}`
  const res = await fetch(target)
  if (!res.ok) {
    const text = await res.text().catch(() => 'Error desconocido')
    throw new ApiError(res.status, text)
  }
  return res.json() as Promise<T>
}

/** Ejecuta un POST tipado contra la API REST. */
export async function apiPost<T, B = unknown>(path: string, body: B): Promise<T> {
  const target = `${BASE_URL}${appendProjectId(path)}`
  const res = await fetch(target, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  })
  if (!res.ok) {
    const text = await res.text().catch(() => 'Error desconocido')
    throw new ApiError(res.status, text)
  }
  return res.json() as Promise<T>
}

/** Ejecuta un DELETE tipado contra la API REST. */
export async function apiDelete<T>(path: string): Promise<T> {
  const target = `${BASE_URL}${appendProjectId(path)}`
  const res = await fetch(target, { method: 'DELETE' })
  if (!res.ok) {
    const text = await res.text().catch(() => 'Error desconocido')
    throw new ApiError(res.status, text)
  }
  return res.json() as Promise<T>
}
