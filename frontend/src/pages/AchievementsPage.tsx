import { useQuery } from '@tanstack/react-query'
import { Link } from 'react-router-dom'
import { fetchAchievements } from '../services/achievementsApi'
import { useAuthStore } from '../stores/authStore'

export default function AchievementsPage() {
  const token = useAuthStore((state) => state.token)

  const achievementsQuery = useQuery({
    queryKey: ['achievements'],
    queryFn: () => fetchAchievements(token as string),
    enabled: Boolean(token),
  })

  const achievements = achievementsQuery.data ?? []
  const earnedCount = achievements.filter((a) => a.earned).length

  return (
    <main className="min-h-screen bg-gradient-to-b from-rose-50 via-white to-sky-50 px-6 py-12">
      <div className="mx-auto flex max-w-lg flex-col items-center gap-6">
        <Link to="/dashboard" className="self-start text-sm text-slate-500 hover:underline">
          ← Back to dashboard
        </Link>
        <h1 className="text-2xl font-bold text-slate-800">🏅 Achievements</h1>

        {achievementsQuery.isLoading && <p className="text-sm text-slate-500">Loading…</p>}

        {achievements.length > 0 && (
          <p className="text-sm text-slate-500">
            {earnedCount} / {achievements.length} unlocked
          </p>
        )}

        <div className="grid w-full grid-cols-2 gap-3 sm:grid-cols-3">
          {achievements.map((achievement) => (
            <div
              key={achievement.key}
              className={`flex flex-col items-center gap-1 rounded-2xl border px-4 py-5 text-center shadow-sm transition ${
                achievement.earned
                  ? 'border-amber-300 bg-amber-50'
                  : 'border-slate-200 bg-white opacity-60'
              }`}
            >
              <div className={`text-3xl ${achievement.earned ? '' : 'grayscale'}`}>
                {achievement.emoji}
              </div>
              <p className="text-sm font-semibold text-slate-800">{achievement.name}</p>
              <p className="text-xs text-slate-500">{achievement.description}</p>
              {achievement.earned && achievement.unlocked_at && (
                <p className="mt-1 text-xs text-amber-700">
                  Unlocked {new Date(achievement.unlocked_at).toLocaleDateString()}
                </p>
              )}
            </div>
          ))}
        </div>
      </div>
    </main>
  )
}
