import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { render, screen } from '@testing-library/react'
import { MemoryRouter, Route, Routes } from 'react-router-dom'
import { beforeEach, describe, expect, it, vi } from 'vitest'
import * as speechApi from '../services/speechApi'
import { useAuthStore } from '../stores/authStore'
import SpeakingHistoryPage from './SpeakingHistoryPage'

const testUser = { id: '1', email: 'test@example.com', created_at: '2026-01-01T00:00:00Z' }

function renderPage() {
  const queryClient = new QueryClient()
  return render(
    <QueryClientProvider client={queryClient}>
      <MemoryRouter initialEntries={['/speaking/history']}>
        <Routes>
          <Route path="/speaking/history" element={<SpeakingHistoryPage />} />
        </Routes>
      </MemoryRouter>
    </QueryClientProvider>,
  )
}

describe('SpeakingHistoryPage', () => {
  beforeEach(() => {
    useAuthStore.setState({ token: 'a-token', user: testUser, isAuthenticated: true })
    vi.restoreAllMocks()
  })

  it('shows a message when there are no past attempts', async () => {
    vi.spyOn(speechApi, 'fetchSpeakingAttempts').mockResolvedValue([])

    renderPage()

    expect(await screen.findByText('No attempts yet. Not enough data yet.')).toBeInTheDocument()
  })

  it('lists past speaking attempts', async () => {
    vi.spyOn(speechApi, 'fetchSpeakingAttempts').mockResolvedValue([
      {
        id: 'attempt-1',
        prompt_key: 'n5-greeting',
        level: 'N5',
        target_text: 'おはようございます',
        transcript: 'おはようございます',
        correct: true,
        similarity: 1,
        xp_earned: 10,
        created_at: '2026-01-01T00:00:00Z',
      },
    ])

    renderPage()

    expect(await screen.findByText('おはようございます')).toBeInTheDocument()
    expect(screen.getByText('Heard: おはようございます')).toBeInTheDocument()
    expect(screen.getByText('+10 XP')).toBeInTheDocument()
  })
})
