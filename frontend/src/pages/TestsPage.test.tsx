import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { render, screen } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import { beforeEach, describe, expect, it, vi } from 'vitest'
import * as testApi from '../services/testApi'
import { useAuthStore } from '../stores/authStore'
import TestsPage from './TestsPage'

const testUser = { id: '1', email: 'test@example.com', created_at: '2026-01-01T00:00:00Z' }

function renderPage() {
  const queryClient = new QueryClient({ defaultOptions: { queries: { retry: false } } })
  return render(
    <QueryClientProvider client={queryClient}>
      <MemoryRouter>
        <TestsPage />
      </MemoryRouter>
    </QueryClientProvider>,
  )
}

describe('TestsPage', () => {
  beforeEach(() => {
    useAuthStore.setState({ token: 'a-token', user: testUser, isAuthenticated: true })
    vi.restoreAllMocks()
  })

  it('lists the available tests', async () => {
    vi.spyOn(testApi, 'fetchTests').mockResolvedValue([
      { id: 't1', title: 'N5 Vocabulary Test', category: 'vocabulary', level: 'N5', question_count: 12 },
      { id: 't2', title: 'N5 Mixed Test', category: 'mixed', level: 'N5', question_count: 20 },
    ])

    renderPage()

    expect(await screen.findByText('N5 Vocabulary Test')).toBeInTheDocument()
    expect(screen.getByText('N5 Mixed Test')).toBeInTheDocument()
    expect(screen.getByText(/12 questions/)).toBeInTheDocument()
  })
})
