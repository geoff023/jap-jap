import type { JlptLevel } from './profile'

export interface SpeakingPrompt {
  key: string
  level: JlptLevel
  target_text: string
  target_reading: string
  target_translation: string
}

export interface SubmitSpeakingAttemptResponse {
  transcript: string
  target_text: string
  correct: boolean
  similarity: number
  xp_earned: number
  total_xp: number
}

export interface SpeakingAttemptSummary {
  id: string
  prompt_key: string
  level: JlptLevel
  target_text: string
  transcript: string
  correct: boolean
  similarity: number
  xp_earned: number
  created_at: string
}
