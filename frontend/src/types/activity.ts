import type { JlptLevel } from './profile'

export type ActivityCategory = 'vocabulary' | 'grammar' | 'kanji'

export interface VocabularyItem {
  id: string
  term: string
  reading: string
  meaning: string
  level: JlptLevel
  example_sentence: string | null
  example_translation: string | null
}

export interface GrammarConcept {
  id: string
  key: string
  title: string
  level: JlptLevel
  explanation: string
  example_sentence: string
  example_translation: string
  answer: string
}

export interface KanjiItem {
  id: string
  character: string
  onyomi: string
  kunyomi: string
  meaning: string
  level: JlptLevel
  example_word: string | null
  example_reading: string | null
  example_meaning: string | null
}

export interface QuizQuestion {
  item_id: string
  prompt: string
  options: string[]
}

export interface QuizResponse {
  category: ActivityCategory
  level: JlptLevel
  questions: QuizQuestion[]
}

export interface QuizAnswer {
  item_id: string
  selected: string
}

export interface QuizSubmitPayload {
  category: ActivityCategory
  level: JlptLevel
  answers: QuizAnswer[]
}

export interface QuizResultItem {
  item_id: string
  correct: boolean
  correct_answer: string
}

export interface QuizSubmitResponse {
  correct_count: number
  total: number
  xp_earned: number
  total_xp: number
  results: QuizResultItem[]
}

export interface FlashcardReview {
  item_id: string
  known: boolean
}

export interface FlashcardCompletePayload {
  category: ActivityCategory
  level: JlptLevel
  reviewed: FlashcardReview[]
}

export interface FlashcardCompleteResponse {
  known_count: number
  total: number
  xp_earned: number
  total_xp: number
}

export interface ActivityHistoryEntry {
  category: ActivityCategory
  activity_type: string
  level: JlptLevel
  correct_count: number | null
  known_count: number | null
  total: number
  xp_earned: number
  created_at: string
}
