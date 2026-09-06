import type { LearnerProfile, OnboardingPayload, ProfileUpdatePayload } from '../types/profile'
import { API_BASE_URL } from './api'
import { ApiError, parseErrorMessage } from './httpErrors'

function authHeaders(token: string): HeadersInit {
  return { Authorization: `Bearer ${token}`, 'Content-Type': 'application/json' }
}

export async function fetchProfile(token: string): Promise<LearnerProfile> {
  const response = await fetch(`${API_BASE_URL}/api/profile`, {
    headers: authHeaders(token),
  })
  if (!response.ok) {
    throw new ApiError(response.status, await parseErrorMessage(response))
  }
  return response.json()
}

export async function submitOnboarding(
  token: string,
  payload: OnboardingPayload,
): Promise<LearnerProfile> {
  const response = await fetch(`${API_BASE_URL}/api/onboarding`, {
    method: 'POST',
    headers: authHeaders(token),
    body: JSON.stringify(payload),
  })
  if (!response.ok) {
    throw new ApiError(response.status, await parseErrorMessage(response))
  }
  return response.json()
}

export async function updateProfile(
  token: string,
  payload: ProfileUpdatePayload,
): Promise<LearnerProfile> {
  const response = await fetch(`${API_BASE_URL}/api/profile`, {
    method: 'PATCH',
    headers: authHeaders(token),
    body: JSON.stringify(payload),
  })
  if (!response.ok) {
    throw new ApiError(response.status, await parseErrorMessage(response))
  }
  return response.json()
}
