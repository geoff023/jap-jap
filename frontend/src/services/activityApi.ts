import type { JlptLevel } from '../types/profile'
import type {
  ActivityCategory,
  ActivityHistoryEntry,
  FlashcardCompletePayload,
  FlashcardCompleteResponse,
  GrammarConcept,
  KanjiItem,
  QuizResponse,
  QuizSubmitPayload,
  QuizSubmitResponse,
  VocabularyItem,
} from '../types/activity'
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

async function postJson<T>(path: string, token: string, payload: unknown): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    method: 'POST',
    headers: authHeaders(token),
    body: JSON.stringify(payload),
  })
  if (!response.ok) {
    throw new ApiError(response.status, await parseErrorMessage(response))
  }
  return response.json()
}

export function fetchVocabulary(token: string, level: JlptLevel): Promise<VocabularyItem[]> {
  return getJson(`/api/vocabulary?level=${level}`, token)
}

export function fetchGrammar(token: string, level: JlptLevel): Promise<GrammarConcept[]> {
  return getJson(`/api/grammar?level=${level}`, token)
}

export function fetchKanji(token: string, level: JlptLevel): Promise<KanjiItem[]> {
  return getJson(`/api/kanji?level=${level}`, token)
}

export function fetchFlashcardDeck(
  token: string,
  category: ActivityCategory,
  level: JlptLevel,
): Promise<(VocabularyItem | GrammarConcept | KanjiItem)[]> {
  return getJson(`/api/activities/flashcards?category=${category}&level=${level}`, token)
}

export function fetchQuiz(
  token: string,
  category: ActivityCategory,
  level: JlptLevel,
  size = 5,
): Promise<QuizResponse> {
  return getJson(`/api/activities/quiz?category=${category}&level=${level}&size=${size}`, token)
}

export function submitQuiz(
  token: string,
  payload: QuizSubmitPayload,
): Promise<QuizSubmitResponse> {
  return postJson('/api/activities/quiz/submit', token, payload)
}

export function completeFlashcards(
  token: string,
  payload: FlashcardCompletePayload,
): Promise<FlashcardCompleteResponse> {
  return postJson('/api/activities/flashcards/complete', token, payload)
}

export function fetchActivityHistory(token: string): Promise<ActivityHistoryEntry[]> {
  return getJson('/api/activities/history', token)
}
