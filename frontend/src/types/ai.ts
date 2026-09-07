export interface GrammarExplanation {
  concept: string
  explanation: string
  example_sentence: string
  example_translation: string
}

export interface VocabularyExplanation {
  term: string
  meaning: string
  explanation: string
  example_sentence: string
  example_translation: string
}

export interface MistakeExplanation {
  concept: string
  explanation: string
  tip: string
}
