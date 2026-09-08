import type { JlptLevel } from './profile'

export type ScenarioKey = 'ramen_shop' | 'convenience_store' | 'train_station'

export interface CharacterPublic {
  key: string
  name: string
  emoji: string
  specialty: string
}

export interface ScenarioPublic {
  key: ScenarioKey
  title: string
  emoji: string
  description: string
  character: CharacterPublic
}

export interface MessagePublic {
  role: 'user' | 'character'
  content: string
  translation: string | null
  created_at: string
}

export interface ConversationSessionSummary {
  id: string
  scenario: ScenarioKey
  character_name: string
  character_emoji: string
  level: JlptLevel
  started_at: string
  last_message_at: string
  message_count: number
}

export interface ConversationSessionDetail {
  id: string
  scenario: ScenarioKey
  character: CharacterPublic
  level: JlptLevel
  started_at: string
  messages: MessagePublic[]
}

export interface SendMessageResponse {
  user_message: MessagePublic
  character_message: MessagePublic
  xp_earned: number
  total_xp: number
}
