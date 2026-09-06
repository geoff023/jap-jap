import { useQuery } from '@tanstack/react-query'
import { Link } from 'react-router-dom'
import { fetchHealth } from '../services/api'
import { useAuthStore } from '../stores/authStore'

const MODES = [
  {
    emoji: '🎮',
    name: 'Explore',
    description: 'Vocabulary, mini stories, culture, and everyday Japanese.',
  },
  {
    emoji: '🗣️',
    name: 'Speak',
    description: 'AI conversation, roleplay, and speaking practice.',
  },
  {
    emoji: '📚',
    name: 'JLPT',
    description: 'Structured N5–N1 prep: vocabulary, kanji, grammar, and more.',
  },
]

function HealthBadge() {
  const { data, isLoading, isError } = useQuery({
    queryKey: ['health'],
    queryFn: fetchHealth,
    retry: false,
  })

  let label = 'Checking backend…'
  let color = 'bg-amber-100 text-amber-800'

  if (!isLoading) {
    if (isError) {
      label = 'Backend unavailable'
      color = 'bg-rose-100 text-rose-800'
    } else if (data) {
      label = `Backend online (db: ${data.database})`
      color = 'bg-emerald-100 text-emerald-800'
    }
  }

  return (
    <span className={`rounded-full px-3 py-1 text-sm font-medium ${color}`}>
      {label}
    </span>
  )
}

export default function LandingPage() {
  const isAuthenticated = useAuthStore((state) => state.isAuthenticated)

  return (
    <main className="min-h-screen bg-gradient-to-b from-rose-50 via-white to-sky-50 text-slate-800">
      <div className="mx-auto flex max-w-3xl flex-col items-center px-6 py-20 text-center">
        <span className="text-6xl">🎌</span>
        <h1 className="mt-4 text-4xl font-bold tracking-tight sm:text-5xl">
          Jap<span className="text-rose-500">Jap</span>
        </h1>
        <p className="mt-4 max-w-xl text-lg text-slate-600">
          A playful, AI-assisted way to learn Japanese — from your first
          hiragana to N1, and everyday conversation along the way.
        </p>

        <div className="mt-6 flex gap-3">
          {isAuthenticated ? (
            <Link
              to="/dashboard"
              className="rounded-lg bg-rose-500 px-5 py-2 text-sm font-semibold text-white transition hover:bg-rose-600"
            >
              Go to dashboard
            </Link>
          ) : (
            <>
              <Link
                to="/register"
                className="rounded-lg bg-rose-500 px-5 py-2 text-sm font-semibold text-white transition hover:bg-rose-600"
              >
                Sign up
              </Link>
              <Link
                to="/login"
                className="rounded-lg border border-slate-300 px-5 py-2 text-sm font-semibold text-slate-700 transition hover:bg-white"
              >
                Log in
              </Link>
            </>
          )}
        </div>

        <div className="mt-8">
          <HealthBadge />
        </div>

        <div className="mt-12 grid w-full gap-4 sm:grid-cols-3">
          {MODES.map((mode) => (
            <div
              key={mode.name}
              className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm transition hover:shadow-md"
            >
              <div className="text-3xl">{mode.emoji}</div>
              <h2 className="mt-2 text-lg font-semibold">{mode.name}</h2>
              <p className="mt-1 text-sm text-slate-500">{mode.description}</p>
            </div>
          ))}
        </div>

        <p className="mt-16 text-xs text-slate-400">
          Under active development — see the project README for progress.
        </p>
      </div>
    </main>
  )
}
