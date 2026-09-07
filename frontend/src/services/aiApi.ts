import type { GrammarExplanation, MistakeExplanation, VocabularyExplanation } from '../types/ai'
import { API_BASE_URL } from './api'
import { ApiError, parseErrorMessage } from './httpErrors'

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

export function explainGrammar(
  token: string,
  concept: string,
  context?: string,
): Promise<GrammarExplanation> {
  return postJson('/api/ai/explain/grammar', token, { concept, context })
}

export function explainVocabulary(
  token: string,
  term: string,
  context?: string,
): Promise<VocabularyExplanation> {
  return postJson('/api/ai/explain/vocabulary', token, { term, context })
}

export function explainMistake(
  token: string,
  category: string,
  concept: string,
  userAnswer: string,
  correctAnswer: string,
): Promise<MistakeExplanation> {
  return postJson('/api/ai/explain/mistake', token, {
    category,
    concept,
    user_answer: userAnswer,
    correct_answer: correctAnswer,
  })
}

export function aiUnavailableMessage(error: unknown): string | null {
  if (error instanceof ApiError && error.status === 503) {
    return 'The AI tutor is not available (no Gemini API key configured for this deployment).'
  }
  return null
}
