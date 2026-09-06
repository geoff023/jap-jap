export type LearningGoal =
  | 'anime_manga'
  | 'travel'
  | 'conversation'
  | 'jlpt'
  | 'university'
  | 'work'
  | 'culture'
  | 'fun'

export type ExperienceLevel =
  | 'complete_beginner'
  | 'knows_some_words'
  | 'knows_hiragana'
  | 'knows_hiragana_katakana'
  | 'basic_grammar'
  | 'previously_studied'

export type PracticeLevel = 'N5' | 'N4' | 'N3' | 'N2' | 'N1' | 'conversation'

export type JlptLevel = 'N5' | 'N4' | 'N3' | 'N2' | 'N1'

export interface LearnerProfile {
  user_id: string
  goals: LearningGoal[]
  experience: ExperienceLevel
  preferred_level: PracticeLevel
  estimated_level: PracticeLevel | null
  jlpt_target: JlptLevel | null
  onboarding_completed: boolean
  created_at: string
  updated_at: string
}

export interface OnboardingPayload {
  goals: LearningGoal[]
  experience: ExperienceLevel
  preferred_level: PracticeLevel
  jlpt_target: JlptLevel | null
}

export type ProfileUpdatePayload = Partial<OnboardingPayload>

export const LEARNING_GOALS: { value: LearningGoal; label: string }[] = [
  { value: 'anime_manga', label: 'Anime / manga' },
  { value: 'travel', label: 'Travel' },
  { value: 'conversation', label: 'Conversation' },
  { value: 'jlpt', label: 'JLPT' },
  { value: 'university', label: 'University' },
  { value: 'work', label: 'Work' },
  { value: 'culture', label: 'Culture' },
  { value: 'fun', label: 'Just for fun' },
]

export const EXPERIENCE_LEVELS: { value: ExperienceLevel; label: string }[] = [
  { value: 'complete_beginner', label: 'Complete beginner' },
  { value: 'knows_some_words', label: 'Know some words' },
  { value: 'knows_hiragana', label: 'Know hiragana' },
  { value: 'knows_hiragana_katakana', label: 'Know hiragana + katakana' },
  { value: 'basic_grammar', label: 'Basic grammar' },
  { value: 'previously_studied', label: 'Previously studied Japanese' },
]

export const PRACTICE_LEVELS: { value: PracticeLevel; label: string }[] = [
  { value: 'N5', label: 'N5' },
  { value: 'N4', label: 'N4' },
  { value: 'N3', label: 'N3' },
  { value: 'N2', label: 'N2' },
  { value: 'N1', label: 'N1' },
  { value: 'conversation', label: 'Conversation' },
]

export const JLPT_LEVELS: { value: JlptLevel; label: string }[] = [
  { value: 'N5', label: 'N5' },
  { value: 'N4', label: 'N4' },
  { value: 'N3', label: 'N3' },
  { value: 'N2', label: 'N2' },
  { value: 'N1', label: 'N1' },
]
