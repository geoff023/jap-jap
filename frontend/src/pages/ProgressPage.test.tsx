import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { render, screen } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import { beforeEach, describe, expect, it, vi } from 'vitest'
import * as progressApi from '../services/progressApi'
import { useAuthStore } from '../stores/authStore'
import ProgressPage from './ProgressPage'

const testUser = { id: '1', email: 'test@example.com', created_at: '2026-01-01T00:00:00Z' }

function renderPage() {
  const queryClient = new QueryClient({ defaultOptions: { queries: { retry: false } } })
  return render(
    <QueryClientProvider client={queryClient}>
      <MemoryRouter>
        <ProgressPage />
      </MemoryRouter>
    </QueryClientProvider>,
  )
}

describe('ProgressPage', () => {
  beforeEach(() => {
    useAuthStore.setState({ token: 'a-token', user: testUser, isAuthenticated: true })
    vi.restoreAllMocks()
  })

  it('shows "Not enough data yet." everywhere when there is no activity', async () => {
    vi.spyOn(progressApi, 'fetchProgress').mockResolvedValue({
      overall: { mastery: null, has_data: false },
      skills: [
        { category: 'vocabulary', mastery: null, concepts_tracked: 0, has_data: false },
        { category: 'grammar', mastery: null, concepts_tracked: 0, has_data: false },
        { category: 'kanji', mastery: null, concepts_tracked: 0, has_data: false },
        { category: 'reading', mastery: null, concepts_tracked: 0, has_data: false },
        { category: 'listening', mastery: null, concepts_tracked: 0, has_data: false },
        { category: 'speaking', mastery: null, concepts_tracked: 0, has_data: false },
        { category: 'conversation', mastery: null, concepts_tracked: 0, has_data: false },
      ],
      estimated_jlpt_readiness: { jlpt_target: null, score: null, has_data: false },
    })

    renderPage()

    // overall (1) + all 7 skills (7) + estimated readiness (1) = 9
    expect(await screen.findAllByText('Not enough data yet.')).toHaveLength(9)
  })

  it('shows computed mastery percentages when data exists', async () => {
    vi.spyOn(progressApi, 'fetchProgress').mockResolvedValue({
      overall: { mastery: 0.75, has_data: true },
      skills: [
        { category: 'vocabulary', mastery: 0.75, concepts_tracked: 4, has_data: true },
        { category: 'grammar', mastery: null, concepts_tracked: 0, has_data: false },
        { category: 'kanji', mastery: null, concepts_tracked: 0, has_data: false },
        { category: 'reading', mastery: null, concepts_tracked: 0, has_data: false },
        { category: 'listening', mastery: null, concepts_tracked: 0, has_data: false },
        { category: 'speaking', mastery: null, concepts_tracked: 0, has_data: false },
        { category: 'conversation', mastery: null, concepts_tracked: 0, has_data: false },
      ],
      estimated_jlpt_readiness: { jlpt_target: 'N5', score: 0.75, has_data: true },
    })

    renderPage()

    expect(await screen.findByText('Overall Japanese')).toBeInTheDocument()
    expect(screen.getAllByText('75%')).toHaveLength(3)
    expect(screen.getByText('(goal: N5)')).toBeInTheDocument()
  })
})
