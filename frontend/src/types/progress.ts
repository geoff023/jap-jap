import type { JlptLevel } from './profile'

export interface CategoryProgress {
  category: string
  mastery: number | null
  concepts_tracked: number
  has_data: boolean
}

export interface OverallProgress {
  mastery: number | null
  has_data: boolean
}

export interface JlptReadiness {
  jlpt_target: JlptLevel | null
  score: number | null
  has_data: boolean
}

export interface ProgressResponse {
  overall: OverallProgress
  skills: CategoryProgress[]
  estimated_jlpt_readiness: JlptReadiness
}

export interface MistakeEntry {
  category: string
  concept: string
  occurrences: number
  mastery: number
  last_seen: string
}

export const CATEGORY_LABELS: Record<string, string> = {
  vocabulary: 'Vocabulary',
  grammar: 'Grammar',
  kanji: 'Kanji',
  reading: 'Reading',
  listening: 'Listening',
  speaking: 'Speaking',
  conversation: 'Conversation',
}
