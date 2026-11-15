/**
 * API client service for AgroSight Fair Space backend.
 * Provides resilient communication with the FastAPI backend endpoints.
 */

import type {
  AiHintResponse,
  BackendHealth,
  DistrictCropIndicator,
  StudyRegion,
} from '../types'

const API_BASE = (import.meta.env.VITE_API_URL as string | undefined)?.replace(/\/+$/, '') || '/api/v1'
const TIMEOUT_MS = 6000

async function request<T>(path: string, options: RequestInit = {}): Promise<T> {
  const url = path.startsWith('http') ? path : `${API_BASE}${path.startsWith('/') ? path : `/${path}`}`
  const controller = new AbortController()
  const timeoutId = setTimeout(() => controller.abort(), TIMEOUT_MS)

  try {
    const res = await fetch(url, {
      ...options,
      signal: controller.signal,
      headers: {
        'Content-Type': 'application/json',
        Accept: 'application/json',
        ...options.headers,
      },
    })

    if (!res.ok) {
      const errorBody = await res.json().catch(() => ({}))
      throw new Error(errorBody?.error?.message || `API error ${res.status}: ${res.statusText}`)
    }

    return (await res.json()) as T
  } finally {
    clearTimeout(timeoutId)
  }
}

export const api = {
  /**
   * Check backend health and database status.
   */
  async checkHealth(): Promise<BackendHealth> {
    const controller = new AbortController()
    const timeoutId = setTimeout(() => controller.abort(), TIMEOUT_MS)
    try {
      const response = await fetch(`${API_BASE}/health`, {
        headers: { Accept: 'application/json' },
        signal: controller.signal,
      })
      const data = (await response.json()) as BackendHealth
      return data.status ? data : { status: 'offline' }
    } catch {
      return { status: 'offline' }
    } finally {
      clearTimeout(timeoutId)
    }
  },

  /**
   * Fetch agricultural study regions (Gaza, Tete, Zambézia).
   */
  async getRegions(): Promise<StudyRegion[]> {
    const res = await request<{ items: StudyRegion[] }>('/regions?limit=100&offset=0')
    return res.items
  },

  /**
   * Get single region metadata.
   */
  async getRegion(regionId: string): Promise<StudyRegion | null> {
    try {
      return await request<StudyRegion>(`/regions/${regionId}`)
    } catch {
      return null
    }
  },

  /**
   * Get region boundary GeoJSON.
   */
  async getRegionMap(regionId: string): Promise<unknown | null> {
    try {
      return await request<unknown>(`/regions/${regionId}/map`)
    } catch {
      return null
    }
  },

  /**
   * Get agricultural crop statistics for a region.
   */
  async getRegionIndicators(regionId: string): Promise<DistrictCropIndicator[]> {
    const res = await request<{ items: DistrictCropIndicator[] }>(
      `/regions/${encodeURIComponent(regionId)}/indicators?limit=100&offset=0`,
    )
    return res.items
  },

  /**
   * Get content manifest for verified missions.
   */
  async getContentManifest(regionId?: string, language: 'pt' | 'en' = 'pt'): Promise<unknown[]> {
    try {
      const query = new URLSearchParams({ language })
      if (regionId) query.set('region_id', regionId)
      const res = await request<{ items: unknown[] }>(`/content/manifest?${query.toString()}`)
      return res.items || []
    } catch {
      return []
    }
  },

  /**
   * Request deterministic AI explanation/hint for farming challenge context.
   */
  async getAiHint(
    language: 'pt' | 'en' = 'pt',
  ): Promise<AiHintResponse> {
    return request<AiHintResponse>('/ai/hint', {
      method: 'POST',
      body: JSON.stringify({
        language,
        context: {
          category: 'simulation',
          source: 'AgroSpace local educational content',
          dataset_version: 'not-applicable',
          limitations: [
            'This is a local educational simulation, not a real satellite observation.',
          ],
        },
      }),
    })
  },

  /**
   * Fetch Earth Observation datasets catalogue.
   */
  async getEarthObservationDatasets(): Promise<unknown[]> {
    try {
      const res = await request<{ items: unknown[] }>('/earth-observation/datasets')
      return res.items || []
    } catch {
      return []
    }
  },
}
