import { useQuery } from '@tanstack/react-query'
import { useState } from 'react'
import { Link, useParams } from 'react-router-dom'
import { aiUnavailableMessage, explainMistake } from '../services/aiApi'
import { fetchAttemptDetail } from '../services/testApi'
import { useAuthStore } from '../stores/authStore'
import type { MistakeExplanation } from '../types/ai'

export default function TestResultPage() {
  const { attemptId } = useParams<{ attemptId: string }>()
  const token = useAuthStore((state) => state.token)
  const [explanations, setExplanations] = useState<Record<string, MistakeExplanation>>({})
  const [explaining, setExplaining] = useState<Record<string, boolean>>({})
  const [explainErrors, setExplainErrors] = useState<Record<string, string>>({})

  const attemptQuery = useQuery({
    queryKey: ['test-attempt', attemptId],
    queryFn: () => fetchAttemptDetail(token as string, attemptId as string),
    enabled: Boolean(token && attemptId),
  })

  const attempt = attemptQuery.data

  async function askAiTutor(
    questionId: string,
    concept: string,
    selected: string,
    correctAnswer: string,
  ) {
    if (!token || !attempt) return
    setExplaining((prev) => ({ ...prev, [questionId]: true }))
    setExplainErrors((prev) => {
      const next = { ...prev }
      delete next[questionId]
      return next
    })
    try {
      const explanation = await explainMistake(
        token,
        attempt.category,
        concept,
        selected,
        correctAnswer,
      )
      setExplanations((prev) => ({ ...prev, [questionId]: explanation }))
    } catch (err) {
      setExplainErrors((prev) => ({
        ...prev,
        [questionId]:
          aiUnavailableMessage(err) ?? 'Could not reach the AI tutor. Please try again.',
      }))
    } finally {
      setExplaining((prev) => ({ ...prev, [questionId]: false }))
    }
  }

  return (
    <main className="min-h-screen bg-gradient-to-b from-rose-50 via-white to-sky-50 px-6 py-12">
      <div className="mx-auto flex max-w-lg flex-col items-center gap-6">
        <div className="flex w-full items-center justify-between">
          <Link to="/tests" className="text-sm text-slate-500 hover:underline">
            ← Back to tests
          </Link>
          <Link to="/tests/history" className="text-sm text-slate-500 hover:underline">
            History →
          </Link>
        </div>

        {attemptQuery.isLoading && <p className="text-sm text-slate-500">Loading…</p>}
        {attemptQuery.isError && (
          <p className="text-sm text-rose-600">Could not load this result.</p>
        )}

        {attempt && (
          <div className="w-full rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
            <h1 className="text-xl font-bold text-slate-800">{attempt.test_title}</h1>
            <p className="mt-1 text-lg font-semibold text-slate-700">
              {attempt.score} / {attempt.total} correct
            </p>
            <p className="text-sm text-slate-500">+{attempt.xp_earned} XP earned</p>

            <ul className="mt-4 flex flex-col gap-2">
              {attempt.answers.map((answer) => (
                <li
                  key={answer.question_id}
                  className={`rounded-lg px-3 py-2 text-sm ${
                    answer.correct
                      ? 'bg-emerald-50 text-emerald-700'
                      : 'bg-rose-50 text-rose-700'
                  }`}
                >
                  <p className="font-medium">
                    {answer.correct ? 'Correct' : `Incorrect — you chose "${answer.selected}"`}
                  </p>
                  <p className="mt-1 text-slate-600">{answer.explanation}</p>

                  {!answer.correct && !explanations[answer.question_id] && (
                    <button
                      type="button"
                      onClick={() =>
                        askAiTutor(
                          answer.question_id,
                          answer.concept,
                          answer.selected,
                          answer.correct_answer,
                        )
                      }
                      disabled={explaining[answer.question_id]}
                      className="mt-2 rounded-lg border border-sky-300 bg-white px-3 py-1 text-xs font-semibold text-sky-700 transition hover:bg-sky-50 disabled:opacity-60"
                    >
                      {explaining[answer.question_id]
                        ? 'Asking AI Tutor…'
                        : '🤖 Ask AI Tutor for more'}
                    </button>
                  )}
                  {explainErrors[answer.question_id] && (
                    <p className="mt-1 text-xs text-rose-500">
                      {explainErrors[answer.question_id]}
                    </p>
                  )}
                  {explanations[answer.question_id] && (
                    <div className="mt-2 rounded-lg bg-sky-50 p-2 text-xs text-sky-900">
                      <p className="font-semibold">🤖 AI Tutor</p>
                      <p className="mt-1">{explanations[answer.question_id].explanation}</p>
                      <p className="mt-1 italic">{explanations[answer.question_id].tip}</p>
                    </div>
                  )}
                </li>
              ))}
            </ul>

            <Link
              to="/tests"
              className="mt-4 block w-full rounded-lg bg-rose-500 px-4 py-2 text-center text-sm font-semibold text-white transition hover:bg-rose-600"
            >
              Take another test
            </Link>
          </div>
        )}
      </div>
    </main>
  )
}
