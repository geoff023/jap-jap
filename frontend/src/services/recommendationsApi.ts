import type { RecommendationsResponse } from '../types/recommendations'
import { API_BASE_URL } from './api'
import { ApiError, parseErrorMessage } from './httpErrors'

export async function fetchRecommendations(token: string): Promise<RecommendationsResponse> {
  const response = await fetch(`${API_BASE_URL}/api/recommendations`, {
    headers: { Authorization: `Bearer ${token}` },
  })
  if (!response.ok) {
    throw new ApiError(response.status, await parseErrorMessage(response))
  }
  return response.json()
}
