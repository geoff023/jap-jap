import { useQuery, useQueryClient } from '@tanstack/react-query'
import { Navigate } from 'react-router-dom'
import { logout } from '../services/authApi'
import { ApiError } from '../services/httpErrors'
import { fetchProfile, updateProfile } from '../services/profileApi'
import { useAuthStore } from '../stores/authStore'
import { LEARNING_GOALS, PRACTICE_LEVELS } from '../types/profile'
import type { PracticeLevel } from '../types/profile'

export default function DashboardPage() {
  const user = useAuthStore((state) => state.user)
  const token = useAuthStore((state) => state.token)
  const clearAuth = useAuthStore((state) => state.clearAuth)
  const queryClient = useQueryClient()

  const profileQuery = useQuery({
    queryKey: ['profile'],
    queryFn: () => fetchProfile(token as string),
    enabled: Boolean(token),
    retry: false,
  })

  async function handleLogout() {
    if (token) {
      await logout(token)
    }
    // ProtectedRoute redirects to /login as soon as isAuthenticated flips to
    // false, so no explicit navigation is needed (and none should be added —
    // it would race the redirect).
    clearAuth()
  }

  async function handleLevelChange(level: PracticeLevel) {
    if (!token) return
    const updated = await updateProfile(token, { preferred_level: level })
    queryClient.setQueryData(['profile'], updated)
  }

  if (profileQuery.isError && profileQuery.error instanceof ApiError && profileQuery.error.status === 404) {
    return <Navigate to="/onboarding" replace />
  }

  const profile = profileQuery.data

  return (
    <main className="flex min-h-screen flex-col items-center gap-6 bg-gradient-to-b from-rose-50 via-white to-sky-50 px-6 py-16 text-center">
      <span className="text-5xl">🎌</span>
      <h1 className="text-2xl font-bold text-slate-800">Welcome, {user?.email}</h1>

      {profileQuery.isLoading && <p className="text-sm text-slate-500">Loading your profile…</p>}

      {profile && (
        <div className="w-full max-w-md rounded-2xl border border-slate-200 bg-white p-6 text-left shadow-sm">
          <h2 className="text-sm font-semibold text-slate-700">Practising</h2>
          <div className="mt-2 flex flex-wrap gap-2">
            {PRACTICE_LEVELS.map((level) => (
              <button
                key={level.value}
                type="button"
                onClick={() => handleLevelChange(level.value)}
                className={`rounded-lg border px-3 py-1.5 text-sm font-medium transition ${
                  profile.preferred_level === level.value
                    ? 'border-rose-400 bg-rose-50 text-rose-700'
                    : 'border-slate-200 text-slate-600 hover:bg-slate-50'
                }`}
              >
                {level.label}
              </button>
            ))}
          </div>
          <p className="mt-2 text-xs text-slate-400">
            Switch anytime — no lock, no penalty, no forced order.
          </p>

          <h2 className="mt-5 text-sm font-semibold text-slate-700">Estimated level</h2>
          <p className="mt-1 text-sm text-slate-500">
            {profile.estimated_level ?? 'Not enough data yet.'}
          </p>

          {profile.jlpt_target && (
            <>
              <h2 className="mt-5 text-sm font-semibold text-slate-700">JLPT goal</h2>
              <p className="mt-1 text-sm text-slate-500">{profile.jlpt_target}</p>
            </>
          )}

          <h2 className="mt-5 text-sm font-semibold text-slate-700">Why you're here</h2>
          <p className="mt-1 text-sm text-slate-500">
            {profile.goals
              .map((goal) => LEARNING_GOALS.find((g) => g.value === goal)?.label ?? goal)
              .join(', ')}
          </p>
        </div>
      )}

      <p className="max-w-md text-sm text-slate-500">
        This is your JapJap home base. Learning features arrive in later phases.
      </p>
      <button
        type="button"
        onClick={handleLogout}
        className="rounded-lg border border-slate-300 px-4 py-2 text-sm font-semibold text-slate-700 transition hover:bg-slate-50"
      >
        Log out
      </button>
    </main>
  )
}
