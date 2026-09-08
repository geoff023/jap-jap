import { useQuery } from '@tanstack/react-query'
import { useState } from 'react'
import { Link } from 'react-router-dom'
import { useAudioRecorder } from '../hooks/useAudioRecorder'
import { fetchSpeakingPrompts, speechUnavailableMessage, submitSpeakingAttempt } from '../services/speechApi'
import { useAuthStore } from '../stores/authStore'
import { JLPT_LEVELS } from '../types/profile'
import type { JlptLevel } from '../types/profile'
import type { SpeakingPrompt, SubmitSpeakingAttemptResponse } from '../types/speech'

export default function SpeakingPracticePage() {
  const token = useAuthStore((state) => state.token)
  const [level, setLevel] = useState<JlptLevel>('N5')
  const [selectedPrompt, setSelectedPrompt] = useState<SpeakingPrompt | null>(null)
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [result, setResult] = useState<SubmitSpeakingAttemptResponse | null>(null)
  const [error, setError] = useState<string | null>(null)
  const recorder = useAudioRecorder()

  const promptsQuery = useQuery({
    queryKey: ['speaking-prompts', level],
    queryFn: () => fetchSpeakingPrompts(token as string, level),
    enabled: Boolean(token),
  })

  function selectPrompt(prompt: SpeakingPrompt) {
    setSelectedPrompt(prompt)
    setResult(null)
    setError(null)
    recorder.reset()
  }

  function backToPrompts() {
    setSelectedPrompt(null)
    setResult(null)
    setError(null)
    recorder.reset()
  }

  async function submit() {
    if (!token || !selectedPrompt || !recorder.audioBlob) return
    setIsSubmitting(true)
    setError(null)
    try {
      const response = await submitSpeakingAttempt(token, selectedPrompt.key, recorder.audioBlob)
      setResult(response)
    } catch (err) {
      setError(speechUnavailableMessage(err) ?? 'Could not check your pronunciation. Please try again.')
    } finally {
      setIsSubmitting(false)
    }
  }

  return (
    <main className="min-h-screen bg-gradient-to-b from-rose-50 via-white to-sky-50 px-6 py-12">
      <div className="mx-auto flex max-w-lg flex-col items-center gap-6">
        <Link to="/dashboard" className="self-start text-sm text-slate-500 hover:underline">
          ← Back to dashboard
        </Link>
        <h1 className="text-2xl font-bold text-slate-800">🎤 Speaking Practice</h1>
        <p className="text-center text-sm text-slate-500">
          Read the phrase aloud, record yourself, and get instant feedback.
        </p>

        <Link to="/speaking/history" className="text-sm text-sky-600 hover:underline">
          View past attempts
        </Link>

        {!selectedPrompt && (
          <>
            <div className="flex items-center gap-2 text-sm text-slate-600">
              <label htmlFor="level-select">Level:</label>
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

            {promptsQuery.isLoading && <p className="text-sm text-slate-500">Loading phrases…</p>}

            <div className="flex w-full flex-col gap-3">
              {promptsQuery.data?.map((prompt) => (
                <button
                  key={prompt.key}
                  type="button"
                  onClick={() => selectPrompt(prompt)}
                  className="rounded-2xl border border-slate-200 bg-white px-5 py-4 text-left shadow-sm transition hover:shadow-md"
                >
                  <p className="font-semibold text-slate-800">{prompt.target_text}</p>
                  <p className="text-sm text-slate-500">{prompt.target_translation}</p>
                </button>
              ))}
            </div>
          </>
        )}

        {selectedPrompt && (
          <div className="w-full rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
            <button
              type="button"
              onClick={backToPrompts}
              className="text-sm text-slate-500 hover:underline"
            >
              ← Choose a different phrase
            </button>

            <p className="mt-4 text-center text-2xl font-bold text-slate-800">
              {selectedPrompt.target_text}
            </p>
            <p className="mt-1 text-center text-sm text-slate-500">
              {selectedPrompt.target_reading}
            </p>
            <p className="mt-1 text-center text-sm text-slate-400">
              {selectedPrompt.target_translation}
            </p>

            {recorder.status === 'unsupported' && (
              <p className="mt-6 text-center text-sm text-rose-600">
                Your browser doesn't support audio recording.
              </p>
            )}
            {recorder.status === 'denied' && (
              <p className="mt-6 text-center text-sm text-rose-600">
                Microphone access was denied. Please allow microphone access and try again.
              </p>
            )}

            {!result && recorder.status !== 'unsupported' && (
              <div className="mt-6 flex flex-col items-center gap-3">
                {recorder.status !== 'recording' && (
                  <button
                    type="button"
                    onClick={() => recorder.start()}
                    className="rounded-lg bg-rose-500 px-4 py-2 text-sm font-semibold text-white transition hover:bg-rose-600"
                  >
                    {recorder.audioBlob ? 'Record again' : '🎙️ Start recording'}
                  </button>
                )}
                {recorder.status === 'recording' && (
                  <button
                    type="button"
                    onClick={() => recorder.stop()}
                    className="rounded-lg bg-slate-800 px-4 py-2 text-sm font-semibold text-white transition hover:bg-slate-900"
                  >
                    ⏹ Stop recording
                  </button>
                )}
                {recorder.audioBlob && recorder.status !== 'recording' && (
                  <button
                    type="button"
                    onClick={submit}
                    disabled={isSubmitting}
                    className="rounded-lg border border-rose-400 px-4 py-2 text-sm font-semibold text-rose-600 transition hover:bg-rose-50 disabled:opacity-60"
                  >
                    {isSubmitting ? 'Checking…' : 'Submit recording'}
                  </button>
                )}
              </div>
            )}

            {error && <p className="mt-4 text-center text-sm text-rose-600">{error}</p>}

            {result && (
              <div className="mt-6 flex flex-col items-center gap-2">
                <p
                  className={`text-lg font-semibold ${
                    result.correct ? 'text-emerald-600' : 'text-rose-600'
                  }`}
                >
                  {result.correct ? 'Nice pronunciation!' : 'Not quite — try again.'}
                </p>
                <p className="text-sm text-slate-500">
                  We heard: <span className="font-medium text-slate-700">{result.transcript}</span>
                </p>
                <p className="text-xs text-slate-400">
                  {Math.round(result.similarity * 100)}% match · +{result.xp_earned} XP
                </p>
                <button
                  type="button"
                  onClick={() => {
                    setResult(null)
                    recorder.reset()
                  }}
                  className="mt-2 rounded-lg border border-slate-300 px-4 py-2 text-sm font-semibold text-slate-700 transition hover:bg-slate-50"
                >
                  Try again
                </button>
              </div>
            )}
          </div>
        )}
      </div>
    </main>
  )
}
