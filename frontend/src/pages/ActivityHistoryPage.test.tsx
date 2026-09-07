import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { render, screen } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import { beforeEach, describe, expect, it, vi } from 'vitest'
import * as activityApi from '../services/activityApi'
import * as testApi from '../services/testApi'
import { useAuthStore } from '../stores/authStore'
import ActivityHistoryPage from './ActivityHistoryPage'

const testUser = { id: '1', email: 'test@example.com', created_at: '2026-01-01T00:00:00Z' }

function renderPage() {
  const queryClient = new QueryClient({ defaultOptions: { queries: { retry: false } } })
  return render(
    <QueryClientProvider client={queryClient}>
      <MemoryRouter>
        <ActivityHistoryPage />
      </MemoryRouter>
    </QueryClientProvider>,
  )
}

describe('ActivityHistoryPage', () => {
  beforeEach(() => {
    useAuthStore.setState({ token: 'a-token', user: testUser, isAuthenticated: true })
    vi.restoreAllMocks()
  })

  it('merges activities and test attempts into one timeline, newest first', async () => {
    vi.spyOn(activityApi, 'fetchActivityHistory').mockResolvedValue([
      {
        category: 'vocabulary',
        activity_type: 'flashcards',
        level: 'N5',
        correct_count: null,
        known_count: 3,
        total: 5,
        xp_earned: 15,
        created_at: '2026-01-01T00:00:00Z',
      },
    ])
    vi.spyOn(testApi, 'fetchAttemptHistory').mockResolvedValue([
      {
        id: 'attempt-1',
        test_id: 't1',
        test_title: 'N5 Grammar Test',
        category: 'grammar',
        level: 'N5',
        score: 6,
        total: 8,
        xp_earned: 60,
        completed_at: '2026-01-02T00:00:00Z',
      },
    ])

    renderPage()

    expect(await screen.findByText('N5 Grammar Test')).toBeInTheDocument()
    expect(screen.getByText('Flashcards')).toBeInTheDocument()

    const titles = screen.getAllByText(/N5 Grammar Test|Flashcards/).map((el) => el.textContent)
    expect(titles).toEqual(['N5 Grammar Test', 'Flashcards'])
  })

  it('shows an empty state with no history', async () => {
    vi.spyOn(activityApi, 'fetchActivityHistory').mockResolvedValue([])
    vi.spyOn(testApi, 'fetchAttemptHistory').mockResolvedValue([])

    renderPage()

    expect(await screen.findByText('No activity yet. Not enough data yet.')).toBeInTheDocument()
  })
})
