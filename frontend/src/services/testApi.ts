import type {
  AnswerSubmission,
  SubmitAttemptResponse,
  TestAttemptDetail,
  TestAttemptSummary,
  TestDetail,
  TestSummary,
} from '../types/test'
import { API_BASE_URL } from './api'
import { ApiError, parseErrorMessage } from './httpErrors'

function authHeaders(token: string): HeadersInit {
  return { Authorization: `Bearer ${token}`, 'Content-Type': 'application/json' }
}

async function getJson<T>(path: string, token: string): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${path}`, { headers: authHeaders(token) })
  if (!response.ok) {
    throw new ApiError(response.status, await parseErrorMessage(response))
  }
  return response.json()
}

export function fetchTests(token: string): Promise<TestSummary[]> {
  return getJson('/api/tests', token)
}

export function fetchTestDetail(token: string, testId: string): Promise<TestDetail> {
  return getJson(`/api/tests/${testId}`, token)
}

export async function submitTestAttempt(
  token: string,
  testId: string,
  answers: AnswerSubmission[],
): Promise<SubmitAttemptResponse> {
  const response = await fetch(`${API_BASE_URL}/api/tests/${testId}/attempts`, {
    method: 'POST',
    headers: authHeaders(token),
    body: JSON.stringify({ answers }),
  })
  if (!response.ok) {
    throw new ApiError(response.status, await parseErrorMessage(response))
  }
  return response.json()
}

export function fetchAttemptHistory(token: string): Promise<TestAttemptSummary[]> {
  return getJson('/api/tests/attempts', token)
}

export function fetchAttemptDetail(token: string, attemptId: string): Promise<TestAttemptDetail> {
  return getJson(`/api/tests/attempts/${attemptId}`, token)
}
