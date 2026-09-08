import type { Achievement } from '../types/achievements'
import { API_BASE_URL } from './api'
import { ApiError, parseErrorMessage } from './httpErrors'

export async function fetchAchievements(token: string): Promise<Achievement[]> {
  const response = await fetch(`${API_BASE_URL}/api/achievements`, {
    headers: { Authorization: `Bearer ${token}` },
  })
  if (!response.ok) {
    throw new ApiError(response.status, await parseErrorMessage(response))
  }
  return response.json()
}
