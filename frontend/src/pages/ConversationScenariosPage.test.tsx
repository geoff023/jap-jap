import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { MemoryRouter, Route, Routes } from 'react-router-dom'
import { beforeEach, describe, expect, it, vi } from 'vitest'
import * as conversationApi from '../services/conversationApi'
import { useAuthStore } from '../stores/authStore'
import ConversationScenariosPage from './ConversationScenariosPage'

const testUser = { id: '1', email: 'test@example.com', created_at: '2026-01-01T00:00:00Z' }

function renderPage() {
  const queryClient = new QueryClient()
  return render(
    <QueryClientProvider client={queryClient}>
      <MemoryRouter initialEntries={['/conversation']}>
        <Routes>
          <Route path="/conversation" element={<ConversationScenariosPage />} />
          <Route path="/conversation/:sessionId" element={<div>chat page</div>} />
        </Routes>
      </MemoryRouter>
    </QueryClientProvider>,
  )
}

describe('ConversationScenariosPage', () => {
  beforeEach(() => {
    useAuthStore.setState({ token: 'a-token', user: testUser, isAuthenticated: true })
    vi.restoreAllMocks()
  })

  it('lists scenarios and starts a session on click', async () => {
    const user = userEvent.setup()
    vi.spyOn(conversationApi, 'fetchScenarios').mockResolvedValue([
      {
        key: 'ramen_shop',
        title: 'Ramen Shop',
        emoji: '🍜',
        description: "You've just sat down at the counter of a small ramen shop.",
        character: { key: 'momo', name: 'Momo', emoji: '🐱', specialty: 'casual conversation' },
      },
    ])
    vi.spyOn(conversationApi, 'startConversation').mockResolvedValue({
      id: 'session-1',
      scenario: 'ramen_shop',
      character: { key: 'momo', name: 'Momo', emoji: '🐱', specialty: 'casual conversation' },
      level: 'N5',
      started_at: '2026-01-01T00:00:00Z',
      messages: [
        {
          role: 'character',
          content: 'いらっしゃいませ！',
          translation: 'Welcome!',
          created_at: '2026-01-01T00:00:00Z',
        },
      ],
    })

    renderPage()

    expect(await screen.findByText('Ramen Shop')).toBeInTheDocument()
    await user.click(screen.getByText('Ramen Shop'))

    expect(conversationApi.startConversation).toHaveBeenCalledWith('a-token', 'ramen_shop', 'N5')
    expect(await screen.findByText('chat page')).toBeInTheDocument()
  })

  it('shows an error message when starting a session fails', async () => {
    const user = userEvent.setup()
    vi.spyOn(conversationApi, 'fetchScenarios').mockResolvedValue([
      {
        key: 'ramen_shop',
        title: 'Ramen Shop',
        emoji: '🍜',
        description: "You've just sat down at the counter of a small ramen shop.",
        character: { key: 'momo', name: 'Momo', emoji: '🐱', specialty: 'casual conversation' },
      },
    ])
    vi.spyOn(conversationApi, 'startConversation').mockRejectedValue(new Error('boom'))

    renderPage()

    await user.click(await screen.findByText('Ramen Shop'))

    expect(
      await screen.findByText('Could not start the conversation. Please try again.'),
    ).toBeInTheDocument()
  })
})
