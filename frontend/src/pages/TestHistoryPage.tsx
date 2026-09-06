import { useQuery } from '@tanstack/react-query'
import { Link } from 'react-router-dom'
import { fetchAttemptHistory } from '../services/testApi'
import { useAuthStore } from '../stores/authStore'

export default function TestHistoryPage() {
  const token = useAuthStore((state) => state.token)

  const historyQuery = useQuery({
    queryKey: ['test-attempts'],
    queryFn: () => fetchAttemptHistory(token as string),
    enabled: Boolean(token),
  })

  const attempts = historyQuery.data ?? []

  return (
    <main className="min-h-screen bg-gradient-to-b from-rose-50 via-white to-sky-50 px-6 py-12">
      <div className="mx-auto flex max-w-lg flex-col items-center gap-6">
        <Link to="/tests" className="self-start text-sm text-slate-500 hover:underline">
          ← Back to tests
        </Link>
        <h1 className="text-2xl font-bold text-slate-800">Test history</h1>

        {historyQuery.isLoading && <p className="text-sm text-slate-500">Loading…</p>}

        {!historyQuery.isLoading && attempts.length === 0 && (
          <p className="text-sm text-slate-500">
            You haven't taken any tests yet. Not enough data yet.
          </p>
        )}

        <div className="flex w-full flex-col gap-3">
          {attempts.map((attempt) => (
            <Link
              key={attempt.id}
              to={`/tests/results/${attempt.id}`}
              className="flex items-center justify-between rounded-2xl border border-slate-200 bg-white px-5 py-4 shadow-sm transition hover:shadow-md"
            >
              <div>
                <p className="font-semibold text-slate-800">{attempt.test_title}</p>
                <p className="text-sm text-slate-500">
                  {attempt.score} / {attempt.total} correct · +{attempt.xp_earned} XP
                </p>
                <p className="text-xs text-slate-400">
                  {new Date(attempt.completed_at).toLocaleString()}
                </p>
              </div>
              <span className="text-rose-500">→</span>
            </Link>
          ))}
        </div>
      </div>
    </main>
  )
}
