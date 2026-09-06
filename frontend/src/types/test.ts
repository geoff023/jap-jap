import type { JlptLevel } from './profile'

export type TestCategory = 'vocabulary' | 'grammar' | 'mixed'

export interface TestSummary {
  id: string
  title: string
  category: TestCategory
  level: JlptLevel
  question_count: number
}

export interface QuestionPublic {
  id: string
  prompt: string
  options: string[]
}

export interface TestDetail {
  id: string
  title: string
  category: TestCategory
  level: JlptLevel
  questions: QuestionPublic[]
}

export interface AnswerSubmission {
  question_id: string
  selected: string
}

export interface AnswerResult {
  question_id: string
  concept: string
  selected: string
  correct: boolean
  correct_answer: string
  explanation: string
}

export interface TestAttemptSummary {
  id: string
  test_id: string
  test_title: string
  category: TestCategory
  level: JlptLevel
  score: number
  total: number
  xp_earned: number
  completed_at: string
}

export interface TestAttemptDetail extends TestAttemptSummary {
  answers: AnswerResult[]
}

export interface SubmitAttemptResponse extends TestAttemptDetail {
  total_xp: number
}
