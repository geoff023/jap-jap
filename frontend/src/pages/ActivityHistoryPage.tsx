import { useQuery } from '@tanstack/react-query'
import { Link } from 'react-router-dom'
import { fetchActivityHistory } from '../services/activityApi'
import { fetchAttemptHistory } from '../services/testApi'
import { useAuthStore } from '../stores/authStore'

const ACTIVITY_TITLE: Record<string, string> = {
  multiple_choice: 'Multiple choice quiz',
  sentence_completion: 'Sentence completion quiz',
  flashcards: 'Flashcards',
}

interface TimelineItem {
  key: string
  title: string
  subtitle: string
  xpEarned: number
  date: string
  link?: string
}

export default function ActivityHistoryPage() {
  const token = useAuthStore((state) => state.token)

  const activitiesQuery = useQuery({
    queryKey: ['activity-history'],
    queryFn: () => fetchActivityHistory(token as string),
    enabled: Boolean(token),
  })
  const attemptsQuery = useQuery({
    queryKey: ['test-attempts'],
    queryFn: () => fetchAttemptHistory(token as string),
    enabled: Boolean(token),
  })

  const isLoading = activitiesQuery.isLoading || attemptsQuery.isLoading

  const items: TimelineItem[] = [
    ...(activitiesQuery.data ?? []).map((activity, index) => ({
      key: `activity-${index}-${activity.created_at}`,
      title: ACTIVITY_TITLE[activity.activity_type] ?? activity.activity_type,
      subtitle: `${activity.correct_count ?? activity.known_count ?? 0}/${activity.total} · ${activity.level}`,
      xpEarned: activity.xp_earned,
      date: activity.created_at,
    })),
    ...(attemptsQuery.data ?? []).map((attempt) => ({
      key: `attempt-${attempt.id}`,
      title: attempt.test_title,
      subtitle: `${attempt.score}/${attempt.total} · ${attempt.level}`,
      xpEarned: attempt.xp_earned,
      date: attempt.completed_at,
      link: `/tests/results/${attempt.id}`,
    })),
  ].sort((a, b) => new Date(b.date).getTime() - new Date(a.date).getTime())

  return (
    <main className="min-h-screen bg-gradient-to-b from-rose-50 via-white to-sky-50 px-6 py-12">
      <div className="mx-auto flex max-w-lg flex-col items-center gap-6">
        <Link to="/progress" className="self-start text-sm text-slate-500 hover:underline">
          ← Back to progress
        </Link>
        <h1 className="text-2xl font-bold text-slate-800">Activity history</h1>

        {isLoading && <p className="text-sm text-slate-500">Loading…</p>}

        {!isLoading && items.length === 0 && (
          <p className="text-sm text-slate-500">
            No activity yet. Not enough data yet.
          </p>
        )}

        <div className="flex w-full flex-col gap-3">
          {items.map((item) => {
            const card = (
              <div className="flex items-center justify-between rounded-2xl border border-slate-200 bg-white px-5 py-4 shadow-sm transition hover:shadow-md">
                <div>
                  <p className="font-semibold text-slate-800">{item.title}</p>
                  <p className="text-sm text-slate-500">{item.subtitle}</p>
                  <p className="text-xs text-slate-400">{new Date(item.date).toLocaleString()}</p>
                </div>
                <span className="text-sm font-medium text-amber-700">+{item.xpEarned} XP</span>
              </div>
            )
            return item.link ? (
              <Link key={item.key} to={item.link}>
                {card}
              </Link>
            ) : (
              <div key={item.key}>{card}</div>
            )
          })}
        </div>
      </div>
    </main>
  )
}
