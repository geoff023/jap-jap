import { useQuery } from '@tanstack/react-query'
import { useState } from 'react'
import { Link } from 'react-router-dom'
import { completeFlashcards, fetchGrammar, fetchVocabulary } from '../services/activityApi'
import { useAuthStore } from '../stores/authStore'
import type { ActivityCategory, FlashcardReview, GrammarConcept, VocabularyItem } from '../types/activity'

const LEVEL = 'N5'

type DeckItem = VocabularyItem | GrammarConcept

function isVocabItem(item: DeckItem): item is VocabularyItem {
  return 'term' in item
}

export default function FlashcardsPage() {
  const token = useAuthStore((state) => state.token)
  const [category, setCategory] = useState<ActivityCategory>('vocabulary')
  const [index, setIndex] = useState(0)
  const [revealed, setRevealed] = useState(false)
  const [reviewed, setReviewed] = useState<FlashcardReview[]>([])
  const [result, setResult] = useState<{ xpEarned: number; totalXp: number } | null>(null)
  const [isSubmitting, setIsSubmitting] = useState(false)

  const deckQuery = useQuery<DeckItem[]>({
    queryKey: ['flashcards', category],
    queryFn: () =>
      category === 'vocabulary'
        ? fetchVocabulary(token as string, LEVEL)
        : fetchGrammar(token as string, LEVEL),
    enabled: Boolean(token),
  })

  function switchCategory(next: ActivityCategory) {
    setCategory(next)
    setIndex(0)
    setRevealed(false)
    setReviewed([])
    setResult(null)
  }

  async function review(known: boolean) {
    const deck = deckQuery.data ?? []
    const current = deck[index]
    const next = [...reviewed, { item_id: current.id, known }]
    setReviewed(next)
    setRevealed(false)

    if (index + 1 < deck.length) {
      setIndex(index + 1)
      return
    }

    if (!token) return
    setIsSubmitting(true)
    try {
      const response = await completeFlashcards(token, {
        category,
        level: LEVEL,
        reviewed: next,
      })
      setResult({ xpEarned: response.xp_earned, totalXp: response.total_xp })
    } finally {
      setIsSubmitting(false)
    }
  }

  const deck = deckQuery.data ?? []
  const current = deck[index]

  return (
    <main className="min-h-screen bg-gradient-to-b from-rose-50 via-white to-sky-50 px-6 py-12">
      <div className="mx-auto flex max-w-lg flex-col items-center gap-6">
        <Link to="/dashboard" className="self-start text-sm text-slate-500 hover:underline">
          ← Back to dashboard
        </Link>
        <h1 className="text-2xl font-bold text-slate-800">Flashcards</h1>

        <div className="flex gap-2">
          {(['vocabulary', 'grammar'] as ActivityCategory[]).map((c) => (
            <button
              key={c}
              type="button"
              onClick={() => switchCategory(c)}
              className={`rounded-lg border px-4 py-1.5 text-sm font-medium capitalize transition ${
                category === c
                  ? 'border-rose-400 bg-rose-50 text-rose-700'
                  : 'border-slate-200 text-slate-600 hover:bg-slate-50'
              }`}
            >
              {c}
            </button>
          ))}
        </div>

        {deckQuery.isLoading && <p className="text-sm text-slate-500">Loading…</p>}

        {result && (
          <div className="w-full rounded-2xl border border-slate-200 bg-white p-6 text-center shadow-sm">
            <p className="text-lg font-semibold text-slate-800">Deck complete!</p>
            <p className="mt-2 text-sm text-slate-500">
              +{result.xpEarned} XP earned · {result.totalXp} XP total
            </p>
            <button
              type="button"
              onClick={() => switchCategory(category)}
              className="mt-4 rounded-lg bg-rose-500 px-4 py-2 text-sm font-semibold text-white transition hover:bg-rose-600"
            >
              Review again
            </button>
          </div>
        )}

        {!result && current && (
          <div className="w-full rounded-2xl border border-slate-200 bg-white p-8 text-center shadow-sm">
            <p className="text-xs uppercase tracking-wide text-slate-400">
              Card {index + 1} of {deck.length}
            </p>

            {isVocabItem(current) ? (
              <>
                <p className="mt-4 text-3xl font-bold text-slate-800">{current.term}</p>
                <p className="mt-1 text-sm text-slate-500">{current.reading}</p>
                {revealed && (
                  <div className="mt-4 border-t border-slate-100 pt-4">
                    <p className="text-lg text-rose-600">{current.meaning}</p>
                    {current.example_sentence && (
                      <p className="mt-2 text-sm text-slate-500">
                        {current.example_sentence}
                        <br />
                        {current.example_translation}
                      </p>
                    )}
                  </div>
                )}
              </>
            ) : (
              <>
                <p className="mt-4 text-lg font-semibold text-slate-800">
                  {current.example_sentence}
                </p>
                <p className="mt-1 text-sm text-slate-500">{current.example_translation}</p>
                {revealed && (
                  <div className="mt-4 border-t border-slate-100 pt-4">
                    <p className="text-lg text-rose-600">Answer: {current.answer}</p>
                    <p className="mt-2 text-sm text-slate-500">{current.explanation}</p>
                  </div>
                )}
              </>
            )}

            <div className="mt-6 flex justify-center gap-3">
              {!revealed ? (
                <button
                  type="button"
                  onClick={() => setRevealed(true)}
                  className="rounded-lg bg-rose-500 px-4 py-2 text-sm font-semibold text-white transition hover:bg-rose-600"
                >
                  Show answer
                </button>
              ) : (
                <>
                  <button
                    type="button"
                    disabled={isSubmitting}
                    onClick={() => review(false)}
                    className="rounded-lg border border-slate-300 px-4 py-2 text-sm font-semibold text-slate-700 transition hover:bg-slate-50 disabled:opacity-60"
                  >
                    Still learning
                  </button>
                  <button
                    type="button"
                    disabled={isSubmitting}
                    onClick={() => review(true)}
                    className="rounded-lg bg-emerald-500 px-4 py-2 text-sm font-semibold text-white transition hover:bg-emerald-600 disabled:opacity-60"
                  >
                    Know it
                  </button>
                </>
              )}
            </div>
          </div>
        )}
      </div>
    </main>
  )
}
