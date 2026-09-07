import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { MemoryRouter } from 'react-router-dom'
import { beforeEach, describe, expect, it, vi } from 'vitest'
import * as activityApi from '../services/activityApi'
import * as aiApi from '../services/aiApi'
import { useAuthStore } from '../stores/authStore'
import type { QuizResponse } from '../types/activity'
import QuizPage from './QuizPage'

const testUser = { id: '1', email: 'test@example.com', created_at: '2026-01-01T00:00:00Z' }

const quiz: QuizResponse = {
  category: 'vocabulary',
  level: 'N5',
  questions: [
    { item_id: 'v1', prompt: '食べる', options: ['to eat', 'to drink', 'to see', 'to go'] },
    { item_id: 'v2', prompt: '飲む', options: ['to eat', 'to drink', 'to see', 'to go'] },
  ],
}

function renderPage() {
  const queryClient = new QueryClient({ defaultOptions: { queries: { retry: false } } })
  return render(
    <QueryClientProvider client={queryClient}>
      <MemoryRouter>
        <QuizPage />
      </MemoryRouter>
    </QueryClientProvider>,
  )
}

describe('QuizPage', () => {
  beforeEach(() => {
    useAuthStore.setState({ token: 'a-token', user: testUser, isAuthenticated: true })
    vi.restoreAllMocks()
  })

  it('collects answers across questions and submits them together', async () => {
    const user = userEvent.setup()
    vi.spyOn(activityApi, 'fetchQuiz').mockResolvedValue(quiz)
    vi.spyOn(activityApi, 'submitQuiz').mockResolvedValue({
      correct_count: 1,
      total: 2,
      xp_earned: 10,
      total_xp: 10,
      results: [
        { item_id: 'v1', correct: true, correct_answer: 'to eat' },
        { item_id: 'v2', correct: false, correct_answer: 'to drink' },
      ],
    })

    renderPage()

    expect(await screen.findByText('食べる')).toBeInTheDocument()
    await user.click(screen.getByRole('radio', { name: 'to eat' }))
    await user.click(screen.getByRole('button', { name: 'Next' }))

    expect(await screen.findByText('飲む')).toBeInTheDocument()
    await user.click(screen.getByRole('radio', { name: 'to go' }))
    await user.click(screen.getByRole('button', { name: 'Finish' }))

    expect(activityApi.submitQuiz).toHaveBeenCalledWith('a-token', {
      category: 'vocabulary',
      level: 'N5',
      answers: [
        { item_id: 'v1', selected: 'to eat' },
        { item_id: 'v2', selected: 'to go' },
      ],
    })
    expect(await screen.findByText('1 / 2 correct')).toBeInTheDocument()
  })

  it('asks the AI Tutor to explain an incorrect answer', async () => {
    const user = userEvent.setup()
    vi.spyOn(activityApi, 'fetchQuiz').mockResolvedValue(quiz)
    vi.spyOn(activityApi, 'submitQuiz').mockResolvedValue({
      correct_count: 1,
      total: 2,
      xp_earned: 10,
      total_xp: 10,
      results: [
        { item_id: 'v1', correct: true, correct_answer: 'to eat' },
        { item_id: 'v2', correct: false, correct_answer: 'to drink' },
      ],
    })
    vi.spyOn(aiApi, 'explainMistake').mockResolvedValue({
      concept: '飲む',
      explanation: '飲む means "to drink", not "to see".',
      tip: 'Remember: 飲む = drink.',
    })

    renderPage()

    await user.click(await screen.findByRole('radio', { name: 'to eat' }))
    await user.click(screen.getByRole('button', { name: 'Next' }))
    await user.click(await screen.findByRole('radio', { name: 'to see' }))
    await user.click(screen.getByRole('button', { name: 'Finish' }))

    await screen.findByText('1 / 2 correct')
    await user.click(screen.getByRole('button', { name: '🤖 Ask AI Tutor' }))

    expect(aiApi.explainMistake).toHaveBeenCalledWith(
      'a-token',
      'vocabulary',
      '飲む',
      'to see',
      'to drink',
    )
    expect(await screen.findByText('飲む means "to drink", not "to see".')).toBeInTheDocument()
  })
})
