import { useQuery } from '@tanstack/react-query'
import { Link } from 'react-router-dom'
import { fetchSpeakingAttempts } from '../services/speechApi'
import { useAuthStore } from '../stores/authStore'

export default function SpeakingHistoryPage() {
  const token = useAuthStore((state) => state.token)

  const attemptsQuery = useQuery({
    queryKey: ['speaking-attempts'],
    queryFn: () => fetchSpeakingAttempts(token as string),
    enabled: Boolean(token),
  })

  const attempts = attemptsQuery.data ?? []

  return (
    <main className="min-h-screen bg-gradient-to-b from-rose-50 via-white to-sky-50 px-6 py-12">
      <div className="mx-auto flex max-w-lg flex-col items-center gap-6">
        <Link to="/speaking" className="self-start text-sm text-slate-500 hover:underline">
          ← Back to speaking practice
        </Link>
        <h1 className="text-2xl font-bold text-slate-800">Past attempts</h1>

        {attemptsQuery.isLoading && <p className="text-sm text-slate-500">Loading…</p>}

        {!attemptsQuery.isLoading && attempts.length === 0 && (
          <p className="text-sm text-slate-500">No attempts yet. Not enough data yet.</p>
        )}

        <div className="flex w-full flex-col gap-3">
          {attempts.map((attempt) => (
            <div
              key={attempt.id}
              className="flex items-center justify-between rounded-2xl border border-slate-200 bg-white px-5 py-4 shadow-sm"
            >
              <div>
                <p className="font-semibold text-slate-800">{attempt.target_text}</p>
                <p className="text-sm text-slate-500">Heard: {attempt.transcript}</p>
                <p className="text-xs text-slate-400">
                  {new Date(attempt.created_at).toLocaleString()} ·{' '}
                  {Math.round(attempt.similarity * 100)}% match
                </p>
              </div>
              <span
                className={`text-sm font-medium ${
                  attempt.correct ? 'text-emerald-600' : 'text-rose-600'
                }`}
              >
                {attempt.correct ? `+${attempt.xp_earned} XP` : 'Try again'}
              </span>
            </div>
          ))}
        </div>
      </div>
    </main>
  )
}
