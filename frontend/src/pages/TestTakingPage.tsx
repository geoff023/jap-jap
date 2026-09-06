import { useQuery } from '@tanstack/react-query'
import { useState } from 'react'
import { Link, useNavigate, useParams } from 'react-router-dom'
import { fetchTestDetail, submitTestAttempt } from '../services/testApi'
import { useAuthStore } from '../stores/authStore'
import type { AnswerSubmission } from '../types/test'

export default function TestTakingPage() {
  const { testId } = useParams<{ testId: string }>()
  const navigate = useNavigate()
  const token = useAuthStore((state) => state.token)

  const [index, setIndex] = useState(0)
  const [selected, setSelected] = useState<string | null>(null)
  const [answers, setAnswers] = useState<AnswerSubmission[]>([])
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const testQuery = useQuery({
    queryKey: ['test', testId],
    queryFn: () => fetchTestDetail(token as string, testId as string),
    enabled: Boolean(token && testId),
  })

  async function next() {
    const questions = testQuery.data?.questions ?? []
    const current = questions[index]
    if (!current || selected === null) return

    const nextAnswers = [...answers, { question_id: current.id, selected }]
    setAnswers(nextAnswers)
    setSelected(null)

    if (index + 1 < questions.length) {
      setIndex(index + 1)
      return
    }

    if (!token || !testId) return
    setIsSubmitting(true)
    setError(null)
    try {
      const result = await submitTestAttempt(token, testId, nextAnswers)
      navigate(`/tests/results/${result.id}`)
    } catch {
      setError('Could not submit your answers. Please try again.')
    } finally {
      setIsSubmitting(false)
    }
  }

  const questions = testQuery.data?.questions ?? []
  const current = questions[index]

  return (
    <main className="min-h-screen bg-gradient-to-b from-rose-50 via-white to-sky-50 px-6 py-12">
      <div className="mx-auto flex max-w-lg flex-col items-center gap-6">
        <Link to="/tests" className="self-start text-sm text-slate-500 hover:underline">
          ← Back to tests
        </Link>
        <h1 className="text-2xl font-bold text-slate-800">{testQuery.data?.title}</h1>

        {testQuery.isLoading && <p className="text-sm text-slate-500">Loading…</p>}
        {testQuery.isError && (
          <p className="text-sm text-rose-600">Could not load this test. Please go back.</p>
        )}

        {current && (
          <div className="w-full rounded-2xl border border-slate-200 bg-white p-8 shadow-sm">
            <p className="text-xs uppercase tracking-wide text-slate-400">
              Question {index + 1} of {questions.length}
            </p>
            <p className="mt-3 text-xl font-semibold text-slate-800">{current.prompt}</p>

            <div className="mt-6 flex flex-col gap-2">
              {current.options.map((option) => (
                <label
                  key={option}
                  className={`cursor-pointer rounded-lg border px-3 py-2 text-sm transition ${
                    selected === option
                      ? 'border-rose-400 bg-rose-50 text-rose-700'
                      : 'border-slate-200 text-slate-600 hover:bg-slate-50'
                  }`}
                >
                  <input
                    type="radio"
                    name="option"
                    className="sr-only"
                    checked={selected === option}
                    onChange={() => setSelected(option)}
                  />
                  {option}
                </label>
              ))}
            </div>

            {error && <p className="mt-4 text-sm text-rose-600">{error}</p>}

            <button
              type="button"
              disabled={selected === null || isSubmitting}
              onClick={next}
              className="mt-6 w-full rounded-lg bg-rose-500 px-4 py-2 text-sm font-semibold text-white transition hover:bg-rose-600 disabled:opacity-60"
            >
              {isSubmitting
                ? 'Submitting…'
                : index + 1 < questions.length
                  ? 'Next'
                  : 'Finish test'}
            </button>
          </div>
        )}
      </div>
    </main>
  )
}
