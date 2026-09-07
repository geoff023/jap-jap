import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { render, screen } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import { beforeEach, describe, expect, it, vi } from 'vitest'
import * as progressApi from '../services/progressApi'
import { useAuthStore } from '../stores/authStore'
import MistakesPage from './MistakesPage'

const testUser = { id: '1', email: 'test@example.com', created_at: '2026-01-01T00:00:00Z' }

function renderPage() {
  const queryClient = new QueryClient({ defaultOptions: { queries: { retry: false } } })
  return render(
    <QueryClientProvider client={queryClient}>
      <MemoryRouter>
        <MistakesPage />
      </MemoryRouter>
    </QueryClientProvider>,
  )
}

describe('MistakesPage', () => {
  beforeEach(() => {
    useAuthStore.setState({ token: 'a-token', user: testUser, isAuthenticated: true })
    vi.restoreAllMocks()
  })

  it('shows an empty state with no mistakes', async () => {
    vi.spyOn(progressApi, 'fetchMistakes').mockResolvedValue([])

    renderPage()

    expect(
      await screen.findByText('No recurring mistakes yet. Not enough data yet.'),
    ).toBeInTheDocument()
  })

  it('lists recurring mistakes with occurrence count and mastery', async () => {
    vi.spyOn(progressApi, 'fetchMistakes').mockResolvedValue([
      {
        category: 'grammar',
        concept: 'particle-ni',
        occurrences: 7,
        mastery: 0.42,
        last_seen: '2026-01-01T00:00:00Z',
      },
    ])

    renderPage()

    expect(await screen.findByText('particle-ni')).toBeInTheDocument()
    expect(screen.getByText('7× missed')).toBeInTheDocument()
    expect(screen.getByText(/Mastery 42%/)).toBeInTheDocument()
  })
})
