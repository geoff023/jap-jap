import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { render, screen } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import { beforeEach, describe, expect, it, vi } from 'vitest'
import * as testApi from '../services/testApi'
import { useAuthStore } from '../stores/authStore'
import TestHistoryPage from './TestHistoryPage'

const testUser = { id: '1', email: 'test@example.com', created_at: '2026-01-01T00:00:00Z' }

function renderPage() {
  const queryClient = new QueryClient({ defaultOptions: { queries: { retry: false } } })
  return render(
    <QueryClientProvider client={queryClient}>
      <MemoryRouter>
        <TestHistoryPage />
      </MemoryRouter>
    </QueryClientProvider>,
  )
}

describe('TestHistoryPage', () => {
  beforeEach(() => {
    useAuthStore.setState({ token: 'a-token', user: testUser, isAuthenticated: true })
    vi.restoreAllMocks()
  })

  it('shows an empty state with no attempts yet', async () => {
    vi.spyOn(testApi, 'fetchAttemptHistory').mockResolvedValue([])

    renderPage()

    expect(
      await screen.findByText("You haven't taken any tests yet. Not enough data yet."),
    ).toBeInTheDocument()
  })

  it('lists past attempts', async () => {
    vi.spyOn(testApi, 'fetchAttemptHistory').mockResolvedValue([
      {
        id: 'attempt-1',
        test_id: 't1',
        test_title: 'N5 Vocabulary Test',
        category: 'vocabulary',
        level: 'N5',
        score: 8,
        total: 12,
        xp_earned: 80,
        completed_at: '2026-01-01T00:00:00Z',
      },
    ])

    renderPage()

    expect(await screen.findByText('N5 Vocabulary Test')).toBeInTheDocument()
    expect(screen.getByText('8 / 12 correct · +80 XP')).toBeInTheDocument()
  })
})
