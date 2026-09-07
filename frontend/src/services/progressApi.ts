import type { MistakeEntry, ProgressResponse } from '../types/progress'
import { API_BASE_URL } from './api'
import { ApiError, parseErrorMessage } from './httpErrors'

async function getJson<T>(path: string, token: string): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    headers: { Authorization: `Bearer ${token}` },
  })
  if (!response.ok) {
    throw new ApiError(response.status, await parseErrorMessage(response))
  }
  return response.json()
}

export function fetchProgress(token: string): Promise<ProgressResponse> {
  return getJson('/api/progress', token)
}

export function fetchMistakes(token: string): Promise<MistakeEntry[]> {
  return getJson('/api/mistakes', token)
}
