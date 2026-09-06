import { useState } from 'react'
import type { FormEvent } from 'react'
import { useNavigate } from 'react-router-dom'
import { ApiError } from '../services/httpErrors'
import { submitOnboarding } from '../services/profileApi'
import { useAuthStore } from '../stores/authStore'
import type { ExperienceLevel, JlptLevel, LearningGoal, PracticeLevel } from '../types/profile'
import { EXPERIENCE_LEVELS, JLPT_LEVELS, LEARNING_GOALS, PRACTICE_LEVELS } from '../types/profile'

export default function OnboardingPage() {
  const navigate = useNavigate()
  const token = useAuthStore((state) => state.token)

  const [goals, setGoals] = useState<LearningGoal[]>([])
  const [experience, setExperience] = useState<ExperienceLevel | ''>('')
  const [preferredLevel, setPreferredLevel] = useState<PracticeLevel | ''>('')
  const [jlptTarget, setJlptTarget] = useState<JlptLevel | ''>('')
  const [error, setError] = useState<string | null>(null)
  const [isSubmitting, setIsSubmitting] = useState(false)

  function toggleGoal(goal: LearningGoal) {
    setGoals((current) =>
      current.includes(goal) ? current.filter((g) => g !== goal) : [...current, goal],
    )
  }

  async function handleSubmit(event: FormEvent) {
    event.preventDefault()
    setError(null)

    if (goals.length === 0) {
      setError('Pick at least one reason you are learning Japanese.')
      return
    }
    if (!experience || !preferredLevel || !token) {
      setError('Please answer every question.')
      return
    }

    setIsSubmitting(true)
    try {
      await submitOnboarding(token, {
        goals,
        experience,
        preferred_level: preferredLevel,
        jlpt_target: jlptTarget || null,
      })
      navigate('/dashboard')
    } catch (err) {
      setError(err instanceof ApiError ? err.message : 'Something went wrong. Please try again.')
    } finally {
      setIsSubmitting(false)
    }
  }

  return (
    <main className="min-h-screen bg-gradient-to-b from-rose-50 via-white to-sky-50 px-6 py-12">
      <form
        onSubmit={handleSubmit}
        className="mx-auto flex max-w-xl flex-col gap-8 rounded-2xl border border-slate-200 bg-white p-8 shadow-sm"
      >
        <div className="text-center">
          <span className="text-4xl">🎌</span>
          <h1 className="mt-2 text-2xl font-bold text-slate-800">Let's set up your JapJap</h1>
          <p className="mt-1 text-sm text-slate-500">A few quick questions to get started.</p>
        </div>

        <fieldset>
          <legend className="text-sm font-semibold text-slate-700">
            Why are you learning Japanese?
          </legend>
          <div className="mt-3 grid grid-cols-2 gap-2 sm:grid-cols-3">
            {LEARNING_GOALS.map((goal) => (
              <label
                key={goal.value}
                className={`cursor-pointer rounded-lg border px-3 py-2 text-center text-sm transition ${
                  goals.includes(goal.value)
                    ? 'border-rose-400 bg-rose-50 text-rose-700'
                    : 'border-slate-200 text-slate-600 hover:bg-slate-50'
                }`}
              >
                <input
                  type="checkbox"
                  className="sr-only"
                  checked={goals.includes(goal.value)}
                  onChange={() => toggleGoal(goal.value)}
                />
                {goal.label}
              </label>
            ))}
          </div>
        </fieldset>

        <fieldset>
          <legend className="text-sm font-semibold text-slate-700">
            What's your experience with Japanese?
          </legend>
          <div className="mt-3 flex flex-col gap-2">
            {EXPERIENCE_LEVELS.map((level) => (
              <label
                key={level.value}
                className={`cursor-pointer rounded-lg border px-3 py-2 text-sm transition ${
                  experience === level.value
                    ? 'border-rose-400 bg-rose-50 text-rose-700'
                    : 'border-slate-200 text-slate-600 hover:bg-slate-50'
                }`}
              >
                <input
                  type="radio"
                  name="experience"
                  className="sr-only"
                  checked={experience === level.value}
                  onChange={() => setExperience(level.value)}
                />
                {level.label}
              </label>
            ))}
          </div>
        </fieldset>

        <fieldset>
          <legend className="text-sm font-semibold text-slate-700">Starting level</legend>
          <p className="mt-1 text-xs text-slate-400">You can change your difficulty anytime.</p>
          <div className="mt-3 grid grid-cols-3 gap-2">
            {PRACTICE_LEVELS.map((level) => (
              <label
                key={level.value}
                className={`cursor-pointer rounded-lg border px-3 py-2 text-center text-sm transition ${
                  preferredLevel === level.value
                    ? 'border-rose-400 bg-rose-50 text-rose-700'
                    : 'border-slate-200 text-slate-600 hover:bg-slate-50'
                }`}
              >
                <input
                  type="radio"
                  name="preferredLevel"
                  className="sr-only"
                  checked={preferredLevel === level.value}
                  onChange={() => setPreferredLevel(level.value)}
                />
                {level.label}
              </label>
            ))}
          </div>
        </fieldset>

        <fieldset>
          <legend className="text-sm font-semibold text-slate-700">
            JLPT goal <span className="font-normal text-slate-400">(optional)</span>
          </legend>
          <div className="mt-3 grid grid-cols-3 gap-2">
            <label
              className={`cursor-pointer rounded-lg border px-3 py-2 text-center text-sm transition ${
                jlptTarget === ''
                  ? 'border-rose-400 bg-rose-50 text-rose-700'
                  : 'border-slate-200 text-slate-600 hover:bg-slate-50'
              }`}
            >
              <input
                type="radio"
                name="jlptTarget"
                className="sr-only"
                checked={jlptTarget === ''}
                onChange={() => setJlptTarget('')}
              />
              None
            </label>
            {JLPT_LEVELS.map((level) => (
              <label
                key={level.value}
                className={`cursor-pointer rounded-lg border px-3 py-2 text-center text-sm transition ${
                  jlptTarget === level.value
                    ? 'border-rose-400 bg-rose-50 text-rose-700'
                    : 'border-slate-200 text-slate-600 hover:bg-slate-50'
                }`}
              >
                <input
                  type="radio"
                  name="jlptTarget"
                  className="sr-only"
                  checked={jlptTarget === level.value}
                  onChange={() => setJlptTarget(level.value)}
                />
                {level.label}
              </label>
            ))}
          </div>
        </fieldset>

        {error && <p className="text-sm text-rose-600">{error}</p>}

        <button
          type="submit"
          disabled={isSubmitting}
          className="rounded-lg bg-rose-500 px-4 py-2 text-sm font-semibold text-white transition hover:bg-rose-600 disabled:opacity-60"
        >
          {isSubmitting ? 'Saving…' : "Let's go"}
        </button>
      </form>
    </main>
  )
}
