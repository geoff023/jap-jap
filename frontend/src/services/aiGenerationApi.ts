import type { JlptLevel } from '../types/profile'
import type {
  ComprehensionAnswer,
  GeneratedQuestion,
  MiniStory,
  SubmitComprehensionResponse,
  SubmitGeneratedQuestionResponse,
} from '../types/aiGeneration'
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

export function generateVocabularyQuestion(
  token: string,
  level: JlptLevel,
): Promise<GeneratedQuestion> {
  return postJson('/api/ai/generate/vocabulary-question', token, { level })
}

export function generateGrammarQuestion(
  token: string,
  level: JlptLevel,
): Promise<GeneratedQuestion> {
  return postJson('/api/ai/generate/grammar-question', token, { level })
}

export function generateMiniStory(
  token: string,
  level: JlptLevel,
  topic?: string,
): Promise<MiniStory> {
  return postJson('/api/ai/generate/mini-story', token, { level, topic: topic || undefined })
}

export function submitComprehension(
  token: string,
  storyId: string,
  answers: ComprehensionAnswer[],
): Promise<SubmitComprehensionResponse> {
  return postJson(`/api/ai/mini-stories/${storyId}/comprehension/submit`, token, { answers })
}

export function submitGeneratedQuestion(
  token: string,
  questionId: string,
  selected: string,
): Promise<SubmitGeneratedQuestionResponse> {
  return postJson(`/api/ai/generated-questions/${questionId}/submit`, token, { selected })
}
