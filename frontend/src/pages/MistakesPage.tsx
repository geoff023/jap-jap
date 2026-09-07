import { useQuery } from '@tanstack/react-query'
import { Link } from 'react-router-dom'
import { fetchMistakes } from '../services/progressApi'
import { useAuthStore } from '../stores/authStore'
import { CATEGORY_LABELS } from '../types/progress'

export default function MistakesPage() {
  const token = useAuthStore((state) => state.token)

  const mistakesQuery = useQuery({
    queryKey: ['mistakes'],
    queryFn: () => fetchMistakes(token as string),
    enabled: Boolean(token),
  })

  const mistakes = mistakesQuery.data ?? []

  return (
    <main className="min-h-screen bg-gradient-to-b from-rose-50 via-white to-sky-50 px-6 py-12">
      <div className="mx-auto flex max-w-lg flex-col items-center gap-6">
        <Link to="/progress" className="self-start text-sm text-slate-500 hover:underline">
          ← Back to progress
        </Link>
        <h1 className="text-2xl font-bold text-slate-800">Recurring mistakes</h1>
        <p className="text-center text-sm text-slate-500">
          Concepts you've gotten wrong at least once, most frequent first.
        </p>

        {mistakesQuery.isLoading && <p className="text-sm text-slate-500">Loading…</p>}

        {!mistakesQuery.isLoading && mistakes.length === 0 && (
          <p className="text-sm text-slate-500">
            No recurring mistakes yet. Not enough data yet.
          </p>
        )}

        <div className="flex w-full flex-col gap-3">
          {mistakes.map((mistake) => (
            <div
              key={`${mistake.category}-${mistake.concept}`}
              className="rounded-2xl border border-slate-200 bg-white px-5 py-4 shadow-sm"
            >
              <div className="flex items-center justify-between">
                <p className="font-semibold text-slate-800">{mistake.concept}</p>
                <span className="rounded-full bg-rose-50 px-2 py-0.5 text-xs font-medium text-rose-600">
                  {mistake.occurrences}× missed
                </span>
              </div>
              <p className="mt-1 text-sm text-slate-500">
                {CATEGORY_LABELS[mistake.category] ?? mistake.category} · Mastery{' '}
                {Math.round(mistake.mastery * 100)}%
              </p>
              <p className="text-xs text-slate-400">
                Last seen {new Date(mistake.last_seen).toLocaleString()}
              </p>
            </div>
          ))}
        </div>
      </div>
    </main>
  )
}
