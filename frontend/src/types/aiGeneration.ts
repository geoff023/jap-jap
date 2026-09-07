import type { JlptLevel } from './profile'

export interface GeneratedQuestion {
  id: string
  category: 'vocabulary' | 'grammar'
  level: JlptLevel
  concept: string
  prompt: string
  options: string[]
}

export interface ComprehensionQuestionPublic {
  index: number
  prompt: string
  options: string[]
}

export interface MiniStory {
  id: string
  title: string
  level: JlptLevel
  story: string
  translation: string
  vocab_highlights: string[]
  comprehension_questions: ComprehensionQuestionPublic[]
}

export interface ComprehensionAnswer {
  index: number
  selected: string
}

export interface ComprehensionAnswerResult {
  index: number
  selected: string
  correct: boolean
  correct_answer: string
  explanation: string
}

export interface SubmitComprehensionResponse {
  score: number
  total: number
  xp_earned: number
  total_xp: number
  results: ComprehensionAnswerResult[]
}

export interface SubmitGeneratedQuestionResponse {
  correct: boolean
  correct_answer: string
  explanation: string
  xp_earned: number
  total_xp: number
}
