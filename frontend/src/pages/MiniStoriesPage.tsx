import { useState } from 'react'
import { Link } from 'react-router-dom'
import { aiUnavailableMessage } from '../services/aiApi'
import { generateMiniStory, submitComprehension } from '../services/aiGenerationApi'
import { useAuthStore } from '../stores/authStore'
import { JLPT_LEVELS } from '../types/profile'
import type { JlptLevel } from '../types/profile'
import type {
  ComprehensionAnswer,
  MiniStory,
  SubmitComprehensionResponse,
} from '../types/aiGeneration'

export default function MiniStoriesPage() {
  const token = useAuthStore((state) => state.token)
  const [level, setLevel] = useState<JlptLevel>('N5')
  const [topic, setTopic] = useState('')
  const [story, setStory] = useState<MiniStory | null>(null)
  const [answers, setAnswers] = useState<Record<number, string>>({})
  const [result, setResult] = useState<SubmitComprehensionResponse | null>(null)
  const [isGenerating, setIsGenerating] = useState(false)
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [error, setError] = useState<string | null>(null)

  async function generate() {
    if (!token) return
    setIsGenerating(true)
    setError(null)
    setStory(null)
    setAnswers({})
    setResult(null)
    try {
      const generated = await generateMiniStory(token, level, topic)
      setStory(generated)
    } catch (err) {
      setError(aiUnavailableMessage(err) ?? 'Could not generate a story. Please try again.')
    } finally {
      setIsGenerating(false)
    }
  }

  async function submit() {
    if (!token || !story) return
    const submittedAnswers: ComprehensionAnswer[] = Object.entries(answers).map(
      ([index, selected]) => ({ index: Number(index), selected }),
    )
    if (submittedAnswers.length === 0) return

    setIsSubmitting(true)
    setError(null)
    try {
      const response = await submitComprehension(token, story.id, submittedAnswers)
      setResult(response)
    } catch (err) {
      setError(aiUnavailableMessage(err) ?? 'Could not submit your answers. Please try again.')
    } finally {
      setIsSubmitting(false)
    }
  }

  const allAnswered = story ? story.comprehension_questions.every((q) => answers[q.index]) : false

  return (
    <main className="min-h-screen bg-gradient-to-b from-rose-50 via-white to-sky-50 px-6 py-12">
      <div className="mx-auto flex max-w-lg flex-col items-center gap-6">
        <Link to="/dashboard" className="self-start text-sm text-slate-500 hover:underline">
          ← Back to dashboard
        </Link>
        <h1 className="text-2xl font-bold text-slate-800">🤖 Mini Stories</h1>
        <p className="text-center text-sm text-slate-500">
          An AI-generated short story with reading comprehension questions.
        </p>

        {!story && (
          <div className="flex w-full flex-col gap-3">
            <div className="flex gap-2">
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
              <input
                type="text"
                value={topic}
                onChange={(e) => setTopic(e.target.value)}
                placeholder="Topic (optional), e.g. ramen shop"
                className="flex-1 rounded-lg border border-slate-200 px-3 py-1.5 text-sm text-slate-600"
              />
            </div>
            <button
              type="button"
              onClick={generate}
              disabled={isGenerating}
              className="rounded-lg bg-rose-500 px-4 py-2 text-sm font-semibold text-white transition hover:bg-rose-600 disabled:opacity-60"
            >
              {isGenerating ? 'Generating…' : 'Generate a story'}
            </button>
          </div>
        )}

        {error && <p className="text-sm text-rose-600">{error}</p>}

        {story && (
          <div className="w-full rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
            <h2 className="text-lg font-bold text-slate-800">{story.title}</h2>
            <p className="mt-2 whitespace-pre-line text-slate-700">{story.story}</p>
            <p className="mt-2 whitespace-pre-line text-sm text-slate-500">{story.translation}</p>

            <div className="mt-4 flex flex-wrap gap-1.5">
              {story.vocab_highlights.map((word) => (
                <span
                  key={word}
                  className="rounded-full bg-sky-50 px-2 py-0.5 text-xs font-medium text-sky-700"
                >
                  {word}
                </span>
              ))}
            </div>

            <h3 className="mt-6 text-sm font-semibold text-slate-700">Comprehension</h3>
            <div className="mt-3 flex flex-col gap-4">
              {story.comprehension_questions.map((question) => {
                const answerResult = result?.results.find((r) => r.index === question.index)
                return (
                  <div key={question.index}>
                    <p className="text-sm font-medium text-slate-800">{question.prompt}</p>
                    <div className="mt-2 flex flex-col gap-1.5">
                      {question.options.map((option) => (
                        <label
                          key={option}
                          className={`cursor-pointer rounded-lg border px-3 py-1.5 text-sm transition ${
                            answers[question.index] === option
                              ? 'border-rose-400 bg-rose-50 text-rose-700'
                              : 'border-slate-200 text-slate-600 hover:bg-slate-50'
                          }`}
                        >
                          <input
                            type="radio"
                            name={`question-${question.index}`}
                            className="sr-only"
                            disabled={Boolean(result)}
                            checked={answers[question.index] === option}
                            onChange={() =>
                              setAnswers((prev) => ({ ...prev, [question.index]: option }))
                            }
                          />
                          {option}
                        </label>
                      ))}
                    </div>
                    {answerResult && (
                      <p
                        className={`mt-1 text-xs ${
                          answerResult.correct ? 'text-emerald-600' : 'text-rose-600'
                        }`}
                      >
                        {answerResult.correct ? 'Correct — ' : 'Incorrect — '}
                        {answerResult.explanation}
                      </p>
                    )}
                  </div>
                )
              })}
            </div>

            {!result && (
              <button
                type="button"
                onClick={submit}
                disabled={!allAnswered || isSubmitting}
                className="mt-6 w-full rounded-lg bg-rose-500 px-4 py-2 text-sm font-semibold text-white transition hover:bg-rose-600 disabled:opacity-60"
              >
                {isSubmitting ? 'Checking…' : 'Submit answers'}
              </button>
            )}

            {result && (
              <>
                <p className="mt-4 text-center text-sm font-semibold text-slate-700">
                  {result.score} / {result.total} correct · +{result.xp_earned} XP earned
                </p>
                <button
                  type="button"
                  onClick={generate}
                  className="mt-4 w-full rounded-lg border border-slate-300 px-4 py-2 text-sm font-semibold text-slate-700 transition hover:bg-slate-50"
                >
                  Generate another story
                </button>
              </>
            )}
          </div>
        )}
      </div>
    </main>
  )
}
