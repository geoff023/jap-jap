import { logout } from '../services/authApi'
import { useAuthStore } from '../stores/authStore'

export default function DashboardPage() {
  const user = useAuthStore((state) => state.user)
  const token = useAuthStore((state) => state.token)
  const clearAuth = useAuthStore((state) => state.clearAuth)

  async function handleLogout() {
    if (token) {
      await logout(token)
    }
    // ProtectedRoute redirects to /login as soon as isAuthenticated flips to
    // false, so no explicit navigation is needed (and none should be added —
    // it would race the redirect).
    clearAuth()
  }

  return (
    <main className="flex min-h-screen flex-col items-center justify-center gap-6 bg-gradient-to-b from-rose-50 via-white to-sky-50 px-6 text-center">
      <span className="text-5xl">🎌</span>
      <h1 className="text-2xl font-bold text-slate-800">Welcome, {user?.email}</h1>
      <p className="max-w-md text-sm text-slate-500">
        This is your JapJap home base. Learning features arrive in later phases — for now, this
        page just proves you're logged in.
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
