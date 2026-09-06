import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { MemoryRouter, Route, Routes } from 'react-router-dom'
import { beforeEach, describe, expect, it, vi } from 'vitest'
import * as testApi from '../services/testApi'
import { useAuthStore } from '../stores/authStore'
import type { TestDetail } from '../types/test'
import TestTakingPage from './TestTakingPage'

const testUser = { id: '1', email: 'test@example.com', created_at: '2026-01-01T00:00:00Z' }

const testDetail: TestDetail = {
  id: 't1',
  title: 'N5 Vocabulary Test',
  category: 'vocabulary',
  level: 'N5',
  questions: [
    { id: 'q1', prompt: '食べる', options: ['to eat', 'to drink', 'to see', 'to go'] },
    { id: 'q2', prompt: '飲む', options: ['to eat', 'to drink', 'to see', 'to go'] },
  ],
}

function renderPage() {
  const queryClient = new QueryClient({ defaultOptions: { queries: { retry: false } } })
  return render(
    <QueryClientProvider client={queryClient}>
      <MemoryRouter initialEntries={['/tests/t1']}>
        <Routes>
          <Route path="/tests/:testId" element={<TestTakingPage />} />
          <Route path="/tests/results/:attemptId" element={<div>Result page</div>} />
        </Routes>
      </MemoryRouter>
    </QueryClientProvider>,
  )
}

describe('TestTakingPage', () => {
  beforeEach(() => {
    useAuthStore.setState({ token: 'a-token', user: testUser, isAuthenticated: true })
    vi.restoreAllMocks()
  })

  it('collects answers across questions and submits them together', async () => {
    const user = userEvent.setup()
    vi.spyOn(testApi, 'fetchTestDetail').mockResolvedValue(testDetail)
    vi.spyOn(testApi, 'submitTestAttempt').mockResolvedValue({
      id: 'attempt-1',
      test_id: 't1',
      test_title: 'N5 Vocabulary Test',
      category: 'vocabulary',
      level: 'N5',
      score: 2,
      total: 2,
      xp_earned: 20,
      total_xp: 20,
      completed_at: '2026-01-01T00:00:00Z',
      answers: [],
    })

    renderPage()

    expect(await screen.findByText('食べる')).toBeInTheDocument()
    await user.click(screen.getByRole('radio', { name: 'to eat' }))
    await user.click(screen.getByRole('button', { name: 'Next' }))

    expect(await screen.findByText('飲む')).toBeInTheDocument()
    await user.click(screen.getByRole('radio', { name: 'to drink' }))
    await user.click(screen.getByRole('button', { name: 'Finish test' }))

    expect(testApi.submitTestAttempt).toHaveBeenCalledWith('a-token', 't1', [
      { question_id: 'q1', selected: 'to eat' },
      { question_id: 'q2', selected: 'to drink' },
    ])
    expect(await screen.findByText('Result page')).toBeInTheDocument()
  })
})
