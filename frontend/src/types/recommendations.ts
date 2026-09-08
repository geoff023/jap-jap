export type RecommendationReason = 'weak_mastery' | 'try_something_new' | 'challenge'

export interface RecommendationEntry {
  category: string | null
  reason: RecommendationReason
  message: string
  mastery: number | null
  action_label: string
  action_path: string
}

export interface RecommendationsResponse {
  recommendations: RecommendationEntry[]
}
