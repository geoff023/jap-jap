import { useQuery } from '@tanstack/react-query'
import { useState } from 'react'
import { Link } from 'react-router-dom'
import { fetchQuiz, submitQuiz } from '../services/activityApi'
import { aiUnavailableMessage, explainMistake } from '../services/aiApi'
import { useAuthStore } from '../stores/authStore'
import type { ActivityCategory, QuizAnswer, QuizSubmitResponse } from '../types/activity'
import type { MistakeExplanation } from '../types/ai'

const LEVEL = 'N5'

export default function QuizPage() {
  const token = useAuthStore((state) => state.token)
  const [category, setCategory] = useState<ActivityCategory>('vocabulary')
  const [index, setIndex] = useState(0)
  const [selected, setSelected] = useState<string | null>(null)
  const [answers, setAnswers] = useState<QuizAnswer[]>([])
  const [result, setResult] = useState<QuizSubmitResponse | null>(null)
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [explanations, setExplanations] = useState<Record<string, MistakeExplanation>>({})
  const [explaining, setExplaining] = useState<Record<string, boolean>>({})
  const [explainErrors, setExplainErrors] = useState<Record<string, string>>({})

  const quizQuery = useQuery({
    queryKey: ['quiz', category],
    queryFn: () => fetchQuiz(token as string, category, LEVEL, 5),
    enabled: Boolean(token),
  })

  function switchCategory(next: ActivityCategory) {
    setCategory(next)
    setIndex(0)
    setSelected(null)
    setAnswers([])
    setResult(null)
    setExplanations({})
    setExplaining({})
    setExplainErrors({})
  }

  async function askAiTutor(itemId: string, correctAnswer: string) {
    if (!token) return
    const answer = answers.find((a) => a.item_id === itemId)
    const question = questions.find((q) => q.item_id === itemId)
    if (!answer || !question) return

    setExplaining((prev) => ({ ...prev, [itemId]: true }))
    setExplainErrors((prev) => {
      const next = { ...prev }
      delete next[itemId]
      return next
    })
    try {
      const explanation = await explainMistake(
        token,
        category,
        question.prompt,
        answer.selected,
        correctAnswer,
      )
      setExplanations((prev) => ({ ...prev, [itemId]: explanation }))
    } catch (err) {
      setExplainErrors((prev) => ({
        ...prev,
        [itemId]: aiUnavailableMessage(err) ?? 'Could not reach the AI tutor. Please try again.',
      }))
    } finally {
      setExplaining((prev) => ({ ...prev, [itemId]: false }))
    }
  }

  async function next() {
    const questions = quizQuery.data?.questions ?? []
    const current = questions[index]
    if (!current || selected === null) return

    const nextAnswers = [...answers, { item_id: current.item_id, selected }]
    setAnswers(nextAnswers)
    setSelected(null)

    if (index + 1 < questions.length) {
      setIndex(index + 1)
      return
    }

    if (!token) return
    setIsSubmitting(true)
    try {
      const response = await submitQuiz(token, { category, level: LEVEL, answers: nextAnswers })
      setResult(response)
    } finally {
      setIsSubmitting(false)
    }
  }

  const questions = quizQuery.data?.questions ?? []
  const current = questions[index]

  return (
    <main className="min-h-screen bg-gradient-to-b from-rose-50 via-white to-sky-50 px-6 py-12">
      <div className="mx-auto flex max-w-lg flex-col items-center gap-6">
        <Link to="/dashboard" className="self-start text-sm text-slate-500 hover:underline">
          ← Back to dashboard
        </Link>
        <h1 className="text-2xl font-bold text-slate-800">
          {category === 'vocabulary' ? 'Multiple choice' : 'Sentence completion'}
        </h1>

        <div className="flex gap-2">
          {(['vocabulary', 'grammar'] as ActivityCategory[]).map((c) => (
            <button
              key={c}
              type="button"
              onClick={() => switchCategory(c)}
              className={`rounded-lg border px-4 py-1.5 text-sm font-medium capitalize transition ${
                category === c
                  ? 'border-rose-400 bg-rose-50 text-rose-700'
                  : 'border-slate-200 text-slate-600 hover:bg-slate-50'
              }`}
            >
              {c}
            </button>
          ))}
        </div>

        {quizQuery.isLoading && <p className="text-sm text-slate-500">Loading…</p>}

        {result && (
          <div className="w-full rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
            <p className="text-center text-lg font-semibold text-slate-800">
              {result.correct_count} / {result.total} correct
            </p>
            <p className="mt-1 text-center text-sm text-slate-500">
              +{result.xp_earned} XP earned · {result.total_xp} XP total
            </p>
            <ul className="mt-4 flex flex-col gap-2">
              {result.results.map((r) => (
                <li
                  key={r.item_id}
                  className={`rounded-lg px-3 py-2 text-sm ${
                    r.correct ? 'bg-emerald-50 text-emerald-700' : 'bg-rose-50 text-rose-700'
                  }`}
                >
                  {r.correct ? 'Correct' : `Incorrect — answer: ${r.correct_answer}`}

                  {!r.correct && !explanations[r.item_id] && (
                    <button
                      type="button"
                      onClick={() => askAiTutor(r.item_id, r.correct_answer)}
                      disabled={explaining[r.item_id]}
                      className="mt-2 block rounded-lg border border-sky-300 bg-white px-3 py-1 text-xs font-semibold text-sky-700 transition hover:bg-sky-50 disabled:opacity-60"
                    >
                      {explaining[r.item_id] ? 'Asking AI Tutor…' : '🤖 Ask AI Tutor'}
                    </button>
                  )}
                  {explainErrors[r.item_id] && (
                    <p className="mt-1 text-xs text-rose-500">{explainErrors[r.item_id]}</p>
                  )}
                  {explanations[r.item_id] && (
                    <div className="mt-2 rounded-lg bg-sky-50 p-2 text-xs text-sky-900">
                      <p className="font-semibold">🤖 AI Tutor</p>
                      <p className="mt-1">{explanations[r.item_id].explanation}</p>
                      <p className="mt-1 italic">{explanations[r.item_id].tip}</p>
                    </div>
                  )}
                </li>
              ))}
            </ul>
            <button
              type="button"
              onClick={() => switchCategory(category)}
              className="mt-4 w-full rounded-lg bg-rose-500 px-4 py-2 text-sm font-semibold text-white transition hover:bg-rose-600"
            >
              New quiz
            </button>
          </div>
        )}

        {!result && current && (
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

            <button
              type="button"
              disabled={selected === null || isSubmitting}
              onClick={next}
              className="mt-6 w-full rounded-lg bg-rose-500 px-4 py-2 text-sm font-semibold text-white transition hover:bg-rose-600 disabled:opacity-60"
            >
              {index + 1 < questions.length ? 'Next' : 'Finish'}
            </button>
          </div>
        )}
      </div>
    </main>
  )
}
