/**
 * Cliente HTTP seguro con validación de respuestas.
 *
 * Resuelve SEC-10: Todas las llamadas fetch validan res.ok antes de parsear JSON.
 * Un único punto de mantenimiento para headers, error handling y futuros interceptores.
 */

export class HttpError extends Error {
  status: number;
  body: string;

  constructor(status: number, body: string) {
    let cleanMessage = body;
    try {
      const parsed = JSON.parse(body);
      if (parsed && typeof parsed.detail === 'string') {
        cleanMessage = parsed.detail;
      } else if (parsed && typeof parsed.message === 'string') {
        cleanMessage = parsed.message;
      }
    } catch (_) {}

    super(cleanMessage);
    this.name = 'HttpError';
    this.status = status;
    this.body = body;
  }
}

export async function safeFetch<T>(url: string, init?: RequestInit): Promise<T> {
  const res = await fetch(url, init);

  if (!res.ok) {
    const body = await res.text().catch(() => 'Unknown error');
    throw new HttpError(res.status, body);
  }

  return res.json();
}

export async function safeFetchOptional<T>(url: string, init?: RequestInit): Promise<T | null> {
  const res = await fetch(url, init);

  if (res.status === 404) {
    return null;
  }

  if (!res.ok) {
    const body = await res.text().catch(() => 'Unknown error');
    throw new HttpError(res.status, body);
  }

  return res.json();
}
