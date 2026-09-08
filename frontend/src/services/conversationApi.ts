import type { JlptLevel } from '../types/profile'
import type {
  ConversationSessionDetail,
  ConversationSessionSummary,
  ScenarioKey,
  ScenarioPublic,
  SendMessageResponse,
} from '../types/conversation'
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

async function postJson<T>(path: string, token: string, payload: unknown): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    method: 'POST',
    headers: { Authorization: `Bearer ${token}`, 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  })
  if (!response.ok) {
    throw new ApiError(response.status, await parseErrorMessage(response))
  }
  return response.json()
}

export function fetchScenarios(token: string): Promise<ScenarioPublic[]> {
  return getJson('/api/conversation/scenarios', token)
}

export function startConversation(
  token: string,
  scenario: ScenarioKey,
  level: JlptLevel,
): Promise<ConversationSessionDetail> {
  return postJson('/api/conversation/sessions', token, { scenario, level })
}

export function fetchConversationSessions(token: string): Promise<ConversationSessionSummary[]> {
  return getJson('/api/conversation/sessions', token)
}

export function fetchConversationSession(
  token: string,
  sessionId: string,
): Promise<ConversationSessionDetail> {
  return getJson(`/api/conversation/sessions/${sessionId}`, token)
}

export function sendConversationMessage(
  token: string,
  sessionId: string,
  content: string,
): Promise<SendMessageResponse> {
  return postJson(`/api/conversation/sessions/${sessionId}/messages`, token, { content })
}
