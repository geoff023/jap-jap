import { useQuery } from '@tanstack/react-query'
import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { fetchScenarios, startConversation } from '../services/conversationApi'
import { useAuthStore } from '../stores/authStore'
import { JLPT_LEVELS } from '../types/profile'
import type { JlptLevel } from '../types/profile'
import type { ScenarioKey } from '../types/conversation'

export default function ConversationScenariosPage() {
  const token = useAuthStore((state) => state.token)
  const navigate = useNavigate()
  const [level, setLevel] = useState<JlptLevel>('N5')
  const [startingKey, setStartingKey] = useState<ScenarioKey | null>(null)
  const [error, setError] = useState<string | null>(null)

  const scenariosQuery = useQuery({
    queryKey: ['conversation-scenarios'],
    queryFn: () => fetchScenarios(token as string),
    enabled: Boolean(token),
  })

  async function handleStart(scenario: ScenarioKey) {
    if (!token) return
    setStartingKey(scenario)
    setError(null)
    try {
      const session = await startConversation(token, scenario, level)
      navigate(`/conversation/${session.id}`)
    } catch {
      setError('Could not start the conversation. Please try again.')
      setStartingKey(null)
    }
  }

  return (
    <main className="min-h-screen bg-gradient-to-b from-rose-50 via-white to-sky-50 px-6 py-12">
      <div className="mx-auto flex max-w-lg flex-col items-center gap-6">
        <Link to="/dashboard" className="self-start text-sm text-slate-500 hover:underline">
          ← Back to dashboard
        </Link>
        <h1 className="text-2xl font-bold text-slate-800">💬 Conversation Practice</h1>
        <p className="text-center text-sm text-slate-500">
          Pick a scenario and chat in Japanese with an AI character.
        </p>

        <Link to="/conversation/history" className="text-sm text-sky-600 hover:underline">
          View past conversations
        </Link>

        <div className="flex items-center gap-2 text-sm text-slate-600">
          <label htmlFor="level-select">Your level:</label>
          <select
            id="level-select"
            value={level}
            onChange={(e) => setLevel(e.target.value as JlptLevel)}
            className="rounded-lg border border-slate-200 px-3 py-1.5 text-sm text-slate-600"
          >
            {JLPT_LEVELS.map((l) => (
              <option key={l.value} value={l.value}>
                {l.label}
              </option>
            ))}
          </select>
        </div>

        {error && <p className="text-sm text-rose-600">{error}</p>}

        {scenariosQuery.isLoading && <p className="text-sm text-slate-500">Loading scenarios…</p>}

        <div className="flex w-full flex-col gap-3">
          {scenariosQuery.data?.map((scenario) => (
            <button
              key={scenario.key}
              type="button"
              onClick={() => handleStart(scenario.key)}
              disabled={startingKey !== null}
              className="flex items-center gap-4 rounded-2xl border border-slate-200 bg-white px-5 py-4 text-left shadow-sm transition hover:shadow-md disabled:opacity-60"
            >
              <span className="text-3xl">{scenario.emoji}</span>
              <span className="flex-1">
                <span className="block font-semibold text-slate-800">{scenario.title}</span>
                <span className="block text-sm text-slate-500">{scenario.description}</span>
                <span className="mt-1 block text-xs text-slate-400">
                  {scenario.character.emoji} {scenario.character.name} ·{' '}
                  {scenario.character.specialty}
                </span>
              </span>
              {startingKey === scenario.key && (
                <span className="text-xs text-slate-400">Starting…</span>
              )}
            </button>
          ))}
        </div>
      </div>
    </main>
  )
}
