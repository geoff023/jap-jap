import { useQuery } from '@tanstack/react-query'
import { Link } from 'react-router-dom'
import { fetchTests } from '../services/testApi'
import { useAuthStore } from '../stores/authStore'

const CATEGORY_LABEL: Record<string, string> = {
  vocabulary: '📚 Vocabulary',
  grammar: '✏️ Grammar',
  mixed: '🎲 Mixed',
}

export default function TestsPage() {
  const token = useAuthStore((state) => state.token)

  const testsQuery = useQuery({
    queryKey: ['tests'],
    queryFn: () => fetchTests(token as string),
    enabled: Boolean(token),
  })

  return (
    <main className="min-h-screen bg-gradient-to-b from-rose-50 via-white to-sky-50 px-6 py-12">
      <div className="mx-auto flex max-w-lg flex-col items-center gap-6">
        <div className="flex w-full items-center justify-between">
          <Link to="/dashboard" className="text-sm text-slate-500 hover:underline">
            ← Back to dashboard
          </Link>
          <Link to="/tests/history" className="text-sm text-slate-500 hover:underline">
            History →
          </Link>
        </div>
        <h1 className="text-2xl font-bold text-slate-800">Tests</h1>

        {testsQuery.isLoading && <p className="text-sm text-slate-500">Loading…</p>}

        <div className="flex w-full flex-col gap-3">
          {testsQuery.data?.map((test) => (
            <Link
              key={test.id}
              to={`/tests/${test.id}`}
              className="flex items-center justify-between rounded-2xl border border-slate-200 bg-white px-5 py-4 shadow-sm transition hover:shadow-md"
            >
              <div>
                <p className="font-semibold text-slate-800">{test.title}</p>
                <p className="text-sm text-slate-500">
                  {CATEGORY_LABEL[test.category] ?? test.category} · {test.level} ·{' '}
                  {test.question_count} questions
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
