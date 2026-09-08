import { useQuery } from '@tanstack/react-query'
import { Link } from 'react-router-dom'
import { fetchConversationSessions } from '../services/conversationApi'
import { useAuthStore } from '../stores/authStore'

const SCENARIO_TITLE: Record<string, string> = {
  ramen_shop: 'Ramen Shop',
  convenience_store: 'Convenience Store',
  train_station: 'Train Station',
}

export default function ConversationHistoryPage() {
  const token = useAuthStore((state) => state.token)

  const sessionsQuery = useQuery({
    queryKey: ['conversation-sessions'],
    queryFn: () => fetchConversationSessions(token as string),
    enabled: Boolean(token),
  })

  const sessions = sessionsQuery.data ?? []

  return (
    <main className="min-h-screen bg-gradient-to-b from-rose-50 via-white to-sky-50 px-6 py-12">
      <div className="mx-auto flex max-w-lg flex-col items-center gap-6">
        <Link to="/conversation" className="self-start text-sm text-slate-500 hover:underline">
          ← Back to scenarios
        </Link>
        <h1 className="text-2xl font-bold text-slate-800">Past conversations</h1>

        {sessionsQuery.isLoading && <p className="text-sm text-slate-500">Loading…</p>}

        {!sessionsQuery.isLoading && sessions.length === 0 && (
          <p className="text-sm text-slate-500">No conversations yet. Not enough data yet.</p>
        )}

        <div className="flex w-full flex-col gap-3">
          {sessions.map((session) => (
            <Link
              key={session.id}
              to={`/conversation/${session.id}`}
              className="flex items-center gap-4 rounded-2xl border border-slate-200 bg-white px-5 py-4 shadow-sm transition hover:shadow-md"
            >
              <span className="text-2xl">{session.character_emoji}</span>
              <span className="flex-1">
                <span className="block font-semibold text-slate-800">
                  {SCENARIO_TITLE[session.scenario] ?? session.scenario}
                </span>
                <span className="block text-sm text-slate-500">
                  with {session.character_name} · {session.level}
                </span>
                <span className="block text-xs text-slate-400">
                  {new Date(session.last_message_at).toLocaleString()} ·{' '}
                  {session.message_count} messages
                </span>
              </span>
            </Link>
          ))}
        </div>
      </div>
    </main>
  )
}
