import { useQuery, useQueryClient } from '@tanstack/react-query'
import { useState } from 'react'
import { Link, Navigate, useParams } from 'react-router-dom'
import { aiUnavailableMessage } from '../services/aiApi'
import { fetchConversationSession, sendConversationMessage } from '../services/conversationApi'
import { ApiError } from '../services/httpErrors'
import { useAuthStore } from '../stores/authStore'
import type { ConversationSessionDetail } from '../types/conversation'

export default function ConversationChatPage() {
  const { sessionId } = useParams<{ sessionId: string }>()
  const token = useAuthStore((state) => state.token)
  const queryClient = useQueryClient()
  const [draft, setDraft] = useState('')
  const [isSending, setIsSending] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [lastXpEarned, setLastXpEarned] = useState<number | null>(null)

  const sessionQuery = useQuery({
    queryKey: ['conversation-session', sessionId],
    queryFn: () => fetchConversationSession(token as string, sessionId as string),
    enabled: Boolean(token && sessionId),
    retry: false,
  })

  if (
    sessionQuery.isError &&
    sessionQuery.error instanceof ApiError &&
    sessionQuery.error.status === 404
  ) {
    return <Navigate to="/conversation" replace />
  }

  const session = sessionQuery.data

  async function handleSend() {
    if (!token || !sessionId || !draft.trim() || !session) return
    const content = draft.trim()
    setIsSending(true)
    setError(null)
    try {
      const response = await sendConversationMessage(token, sessionId, content)
      setLastXpEarned(response.xp_earned)
      const updated: ConversationSessionDetail = {
        ...session,
        messages: [...session.messages, response.user_message, response.character_message],
      }
      queryClient.setQueryData(['conversation-session', sessionId], updated)
      setDraft('')
    } catch (err) {
      setError(aiUnavailableMessage(err) ?? 'The character could not respond. Please try again.')
    } finally {
      setIsSending(false)
    }
  }

  return (
    <main className="flex min-h-screen flex-col bg-gradient-to-b from-rose-50 via-white to-sky-50 px-6 py-12">
      <div className="mx-auto flex w-full max-w-lg flex-1 flex-col gap-4">
        <Link to="/conversation" className="self-start text-sm text-slate-500 hover:underline">
          ← Back to scenarios
        </Link>

        {sessionQuery.isLoading && <p className="text-sm text-slate-500">Loading conversation…</p>}

        {session && (
          <>
            <h1 className="text-xl font-bold text-slate-800">
              {session.character.emoji} {session.character.name}
            </h1>

            <div className="flex flex-1 flex-col gap-3 overflow-y-auto rounded-2xl border border-slate-200 bg-white p-4 shadow-sm">
              {session.messages.map((message, index) => (
                <div
                  key={index}
                  className={`max-w-[80%] rounded-2xl px-4 py-2 text-sm ${
                    message.role === 'character'
                      ? 'self-start bg-slate-100 text-slate-800'
                      : 'self-end bg-rose-500 text-white'
                  }`}
                >
                  <p>{message.content}</p>
                  {message.translation && (
                    <p
                      className={`mt-1 text-xs ${
                        message.role === 'character' ? 'text-slate-500' : 'text-rose-100'
                      }`}
                    >
                      {message.translation}
                    </p>
                  )}
                </div>
              ))}
            </div>

            {error && <p className="text-sm text-rose-600">{error}</p>}
            {lastXpEarned !== null && !error && (
              <p className="text-xs text-amber-700">+{lastXpEarned} XP earned</p>
            )}

            <div className="flex gap-2">
              <input
                type="text"
                value={draft}
                onChange={(e) => setDraft(e.target.value)}
                onKeyDown={(e) => {
                  if (e.key === 'Enter') handleSend()
                }}
                placeholder="Type in Japanese…"
                disabled={isSending}
                className="flex-1 rounded-lg border border-slate-200 px-3 py-2 text-sm text-slate-700"
              />
              <button
                type="button"
                onClick={handleSend}
                disabled={isSending || !draft.trim()}
                className="rounded-lg bg-rose-500 px-4 py-2 text-sm font-semibold text-white transition hover:bg-rose-600 disabled:opacity-60"
              >
                {isSending ? 'Sending…' : 'Send'}
              </button>
            </div>
          </>
        )}
      </div>
    </main>
  )
}
