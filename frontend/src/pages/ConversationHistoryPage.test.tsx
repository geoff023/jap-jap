import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { render, screen } from '@testing-library/react'
import { MemoryRouter, Route, Routes } from 'react-router-dom'
import { beforeEach, describe, expect, it, vi } from 'vitest'
import * as conversationApi from '../services/conversationApi'
import { useAuthStore } from '../stores/authStore'
import ConversationHistoryPage from './ConversationHistoryPage'

const testUser = { id: '1', email: 'test@example.com', created_at: '2026-01-01T00:00:00Z' }

function renderPage() {
  const queryClient = new QueryClient()
  return render(
    <QueryClientProvider client={queryClient}>
      <MemoryRouter initialEntries={['/conversation/history']}>
        <Routes>
          <Route path="/conversation/history" element={<ConversationHistoryPage />} />
        </Routes>
      </MemoryRouter>
    </QueryClientProvider>,
  )
}

describe('ConversationHistoryPage', () => {
  beforeEach(() => {
    useAuthStore.setState({ token: 'a-token', user: testUser, isAuthenticated: true })
    vi.restoreAllMocks()
  })

  it('shows a message when there are no past conversations', async () => {
    vi.spyOn(conversationApi, 'fetchConversationSessions').mockResolvedValue([])

    renderPage()

    expect(
      await screen.findByText('No conversations yet. Not enough data yet.'),
    ).toBeInTheDocument()
  })

  it('lists past conversation sessions', async () => {
    vi.spyOn(conversationApi, 'fetchConversationSessions').mockResolvedValue([
      {
        id: 'session-1',
        scenario: 'ramen_shop',
        character_name: 'Momo',
        character_emoji: '🐱',
        level: 'N5',
        started_at: '2026-01-01T00:00:00Z',
        last_message_at: '2026-01-01T00:05:00Z',
        message_count: 3,
      },
    ])

    renderPage()

    expect(await screen.findByText('Ramen Shop')).toBeInTheDocument()
    expect(screen.getByText('with Momo · N5')).toBeInTheDocument()
    expect(screen.getByRole('link', { name: /Ramen Shop/ })).toHaveAttribute(
      'href',
      '/conversation/session-1',
    )
  })
})
