import { useQuery } from '@tanstack/react-query'
import { Link } from 'react-router-dom'
import { fetchProgress } from '../services/progressApi'
import { useAuthStore } from '../stores/authStore'
import { CATEGORY_LABELS } from '../types/progress'

function formatMastery(mastery: number | null, hasData: boolean): string {
  if (!hasData || mastery === null) return 'Not enough data yet.'
  return `${Math.round(mastery * 100)}%`
}

export default function ProgressPage() {
  const token = useAuthStore((state) => state.token)

  const progressQuery = useQuery({
    queryKey: ['progress'],
    queryFn: () => fetchProgress(token as string),
    enabled: Boolean(token),
  })

  const progress = progressQuery.data

  return (
    <main className="min-h-screen bg-gradient-to-b from-rose-50 via-white to-sky-50 px-6 py-12">
      <div className="mx-auto flex max-w-lg flex-col items-center gap-6">
        <div className="flex w-full items-center justify-between">
          <Link to="/dashboard" className="text-sm text-slate-500 hover:underline">
            ← Back to dashboard
          </Link>
          <div className="flex gap-4">
            <Link to="/mistakes" className="text-sm text-slate-500 hover:underline">
              Mistakes →
            </Link>
            <Link to="/activity-history" className="text-sm text-slate-500 hover:underline">
              History →
            </Link>
          </div>
        </div>

        <h1 className="text-2xl font-bold text-slate-800">Your progress</h1>

        {progressQuery.isLoading && <p className="text-sm text-slate-500">Loading…</p>}

        {progress && (
          <>
            <div className="w-full rounded-2xl border border-slate-200 bg-white p-6 text-center shadow-sm">
              <h2 className="text-sm font-semibold text-slate-700">Overall Japanese</h2>
              <p className="mt-1 text-3xl font-bold text-rose-600">
                {formatMastery(progress.overall.mastery, progress.overall.has_data)}
              </p>
            </div>

            <div className="w-full rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
              <h2 className="text-sm font-semibold text-slate-700">By skill</h2>
              <div className="mt-3 flex flex-col gap-3">
                {progress.skills.map((skill) => (
                  <div key={skill.category} className="flex items-center justify-between">
                    <span className="text-sm text-slate-600">
                      {CATEGORY_LABELS[skill.category] ?? skill.category}
                    </span>
                    <span
                      className={`text-sm font-medium ${
                        skill.has_data ? 'text-slate-800' : 'text-slate-400'
                      }`}
                    >
                      {formatMastery(skill.mastery, skill.has_data)}
                    </span>
                  </div>
                ))}
              </div>
            </div>

            <div className="w-full rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
              <h2 className="text-sm font-semibold text-slate-700">
                Estimated JLPT readiness
                {progress.estimated_jlpt_readiness.jlpt_target && (
                  <span className="ml-1 font-normal text-slate-400">
                    (goal: {progress.estimated_jlpt_readiness.jlpt_target})
                  </span>
                )}
              </h2>
              <p className="mt-1 text-2xl font-bold text-slate-800">
                {formatMastery(
                  progress.estimated_jlpt_readiness.score,
                  progress.estimated_jlpt_readiness.has_data,
                )}
              </p>
              <p className="mt-1 text-xs text-slate-400">
                An estimate based on your own practice so far — not an official JLPT prediction.
              </p>
            </div>
          </>
        )}
      </div>
    </main>
  )
}
