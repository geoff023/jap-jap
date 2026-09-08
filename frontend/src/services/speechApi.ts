import type {
  SpeakingAttemptSummary,
  SpeakingPrompt,
  SubmitSpeakingAttemptResponse,
} from '../types/speech'
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

export function fetchSpeakingPrompts(token: string, level?: string): Promise<SpeakingPrompt[]> {
  const query = level ? `?level=${encodeURIComponent(level)}` : ''
  return getJson(`/api/speech/prompts${query}`, token)
}

export function fetchSpeakingAttempts(token: string): Promise<SpeakingAttemptSummary[]> {
  return getJson('/api/speech/attempts', token)
}

export async function submitSpeakingAttempt(
  token: string,
  promptKey: string,
  audio: Blob,
): Promise<SubmitSpeakingAttemptResponse> {
  const formData = new FormData()
  formData.append('prompt_key', promptKey)
  formData.append('audio', audio, 'recording.webm')

  const response = await fetch(`${API_BASE_URL}/api/speech/attempts`, {
    method: 'POST',
    headers: { Authorization: `Bearer ${token}` },
    body: formData,
  })
  if (!response.ok) {
    throw new ApiError(response.status, await parseErrorMessage(response))
  }
  return response.json()
}

export function speechUnavailableMessage(error: unknown): string | null {
  if (error instanceof ApiError && error.status === 503) {
    return 'Speech practice is not available (no speech provider configured for this deployment).'
  }
  return null
}
