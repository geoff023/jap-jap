import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { MemoryRouter, Route, Routes } from 'react-router-dom'
import { beforeEach, describe, expect, it, vi } from 'vitest'
import * as aiApi from '../services/aiApi'
import * as testApi from '../services/testApi'
import { useAuthStore } from '../stores/authStore'
import TestResultPage from './TestResultPage'

const testUser = { id: '1', email: 'test@example.com', created_at: '2026-01-01T00:00:00Z' }

function renderPage() {
  const queryClient = new QueryClient({ defaultOptions: { queries: { retry: false } } })
  return render(
    <QueryClientProvider client={queryClient}>
      <MemoryRouter initialEntries={['/tests/results/attempt-1']}>
        <Routes>
          <Route path="/tests/results/:attemptId" element={<TestResultPage />} />
        </Routes>
      </MemoryRouter>
    </QueryClientProvider>,
  )
}

describe('TestResultPage', () => {
  beforeEach(() => {
    useAuthStore.setState({ token: 'a-token', user: testUser, isAuthenticated: true })
    vi.restoreAllMocks()
  })

  it('shows the score and a breakdown of each answer', async () => {
    vi.spyOn(testApi, 'fetchAttemptDetail').mockResolvedValue({
      id: 'attempt-1',
      test_id: 't1',
      test_title: 'N5 Vocabulary Test',
      category: 'vocabulary',
      level: 'N5',
      score: 1,
      total: 2,
      xp_earned: 10,
      completed_at: '2026-01-01T00:00:00Z',
      answers: [
        {
          question_id: 'q1',
          concept: '食べる',
          selected: 'to eat',
          correct: true,
          correct_answer: 'to eat',
          explanation: '食べる (たべる) means "to eat".',
        },
        {
          question_id: 'q2',
          concept: '飲む',
          selected: 'to see',
          correct: false,
          correct_answer: 'to drink',
          explanation: '飲む (のむ) means "to drink".',
        },
      ],
    })

    renderPage()

    expect(await screen.findByText('N5 Vocabulary Test')).toBeInTheDocument()
    expect(screen.getByText('1 / 2 correct')).toBeInTheDocument()
    expect(screen.getByText('+10 XP earned')).toBeInTheDocument()
    expect(screen.getByText('Correct')).toBeInTheDocument()
    expect(screen.getByText('Incorrect — you chose "to see"')).toBeInTheDocument()
  })

  it('asks the AI Tutor for more on an incorrect answer', async () => {
    const user = userEvent.setup()
    vi.spyOn(testApi, 'fetchAttemptDetail').mockResolvedValue({
      id: 'attempt-1',
      test_id: 't1',
      test_title: 'N5 Vocabulary Test',
      category: 'vocabulary',
      level: 'N5',
      score: 0,
      total: 1,
      xp_earned: 0,
      completed_at: '2026-01-01T00:00:00Z',
      answers: [
        {
          question_id: 'q2',
          concept: '飲む',
          selected: 'to see',
          correct: false,
          correct_answer: 'to drink',
          explanation: '飲む (のむ) means "to drink".',
        },
      ],
    })
    vi.spyOn(aiApi, 'explainMistake').mockResolvedValue({
      concept: '飲む',
      explanation: '飲む means "to drink", not "to see".',
      tip: 'Remember: 飲む = drink.',
    })

    renderPage()

    await user.click(await screen.findByRole('button', { name: '🤖 Ask AI Tutor for more' }))

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
