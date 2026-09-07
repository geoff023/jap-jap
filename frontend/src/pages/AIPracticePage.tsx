import { useState } from 'react'
import { Link } from 'react-router-dom'
import {
  generateGrammarQuestion,
  generateVocabularyQuestion,
  submitGeneratedQuestion,
} from '../services/aiGenerationApi'
import { aiUnavailableMessage } from '../services/aiApi'
import { useAuthStore } from '../stores/authStore'
import { JLPT_LEVELS } from '../types/profile'
import type { JlptLevel } from '../types/profile'
import type { GeneratedQuestion, SubmitGeneratedQuestionResponse } from '../types/aiGeneration'

type Category = 'vocabulary' | 'grammar'

export default function AIPracticePage() {
  const token = useAuthStore((state) => state.token)
  const [level, setLevel] = useState<JlptLevel>('N5')
  const [category, setCategory] = useState<Category>('vocabulary')
  const [question, setQuestion] = useState<GeneratedQuestion | null>(null)
  const [selected, setSelected] = useState<string | null>(null)
  const [result, setResult] = useState<SubmitGeneratedQuestionResponse | null>(null)
  const [isGenerating, setIsGenerating] = useState(false)
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [error, setError] = useState<string | null>(null)

  async function generate() {
    if (!token) return
    setIsGenerating(true)
    setError(null)
    setQuestion(null)
    setSelected(null)
    setResult(null)
    try {
      const generated =
        category === 'vocabulary'
          ? await generateVocabularyQuestion(token, level)
          : await generateGrammarQuestion(token, level)
      setQuestion(generated)
    } catch (err) {
      setError(aiUnavailableMessage(err) ?? 'Could not generate a question. Please try again.')
    } finally {
      setIsGenerating(false)
    }
  }

  async function submit() {
    if (!token || !question || selected === null) return
    setIsSubmitting(true)
    setError(null)
    try {
      const response = await submitGeneratedQuestion(token, question.id, selected)
      setResult(response)
    } catch (err) {
      setError(aiUnavailableMessage(err) ?? 'Could not submit your answer. Please try again.')
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
        <h1 className="text-2xl font-bold text-slate-800">🤖 AI Practice</h1>
        <p className="text-center text-sm text-slate-500">
          Fresh, AI-generated questions — supplementary practice beyond the core lessons.
        </p>

        <div className="flex flex-wrap items-center justify-center gap-2">
          {(['vocabulary', 'grammar'] as Category[]).map((c) => (
            <button
              key={c}
              type="button"
              onClick={() => setCategory(c)}
              className={`rounded-lg border px-4 py-1.5 text-sm font-medium capitalize transition ${
                category === c
                  ? 'border-rose-400 bg-rose-50 text-rose-700'
                  : 'border-slate-200 text-slate-600 hover:bg-slate-50'
              }`}
            >
              {c}
            </button>
          ))}
          <select
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

        {!question && (
          <button
            type="button"
            onClick={generate}
            disabled={isGenerating}
            className="rounded-lg bg-rose-500 px-4 py-2 text-sm font-semibold text-white transition hover:bg-rose-600 disabled:opacity-60"
          >
            {isGenerating ? 'Generating…' : 'Generate a question'}
          </button>
        )}

        {error && <p className="text-sm text-rose-600">{error}</p>}

        {question && (
          <div className="w-full rounded-2xl border border-slate-200 bg-white p-8 shadow-sm">
            <p className="text-xs uppercase tracking-wide text-slate-400">
              {category} · {level}
            </p>
            <p className="mt-3 text-xl font-semibold text-slate-800">{question.prompt}</p>

            <div className="mt-6 flex flex-col gap-2">
              {question.options.map((option) => (
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
                    disabled={Boolean(result)}
                    onChange={() => setSelected(option)}
                  />
                  {option}
                </label>
              ))}
            </div>

            {!result && (
              <button
                type="button"
                disabled={selected === null || isSubmitting}
                onClick={submit}
                className="mt-6 w-full rounded-lg bg-rose-500 px-4 py-2 text-sm font-semibold text-white transition hover:bg-rose-600 disabled:opacity-60"
              >
                {isSubmitting ? 'Checking…' : 'Submit answer'}
              </button>
            )}

            {result && (
              <div
                className={`mt-6 rounded-lg p-3 text-sm ${
                  result.correct ? 'bg-emerald-50 text-emerald-700' : 'bg-rose-50 text-rose-700'
                }`}
              >
                <p className="font-semibold">
                  {result.correct ? 'Correct!' : `Incorrect — answer: ${result.correct_answer}`}
                </p>
                <p className="mt-1">{result.explanation}</p>
                <p className="mt-2 text-xs">
                  +{result.xp_earned} XP earned · {result.total_xp} XP total
                </p>
              </div>
            )}

            {result && (
              <button
                type="button"
                onClick={generate}
                className="mt-4 w-full rounded-lg border border-slate-300 px-4 py-2 text-sm font-semibold text-slate-700 transition hover:bg-slate-50"
              >
                Generate another
              </button>
            )}
          </div>
        )}
      </div>
    </main>
  )
}
