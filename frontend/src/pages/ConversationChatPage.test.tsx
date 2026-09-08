import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { MemoryRouter, Route, Routes } from 'react-router-dom'
import { beforeEach, describe, expect, it, vi } from 'vitest'
import * as conversationApi from '../services/conversationApi'
import { ApiError } from '../services/httpErrors'
import { useAuthStore } from '../stores/authStore'
import type { ConversationSessionDetail } from '../types/conversation'
import ConversationChatPage from './ConversationChatPage'

const testUser = { id: '1', email: 'test@example.com', created_at: '2026-01-01T00:00:00Z' }

const testSession: ConversationSessionDetail = {
  id: 'session-1',
  scenario: 'ramen_shop',
  character: { key: 'momo', name: 'Momo', emoji: '🐱', specialty: 'casual conversation' },
  level: 'N5',
  started_at: '2026-01-01T00:00:00Z',
  messages: [
    {
      role: 'character',
      content: 'いらっしゃいませ！何にしますか？',
      translation: 'Welcome! What would you like to order?',
      created_at: '2026-01-01T00:00:00Z',
    },
  ],
}

function renderPage() {
  const queryClient = new QueryClient({ defaultOptions: { queries: { retry: false } } })
  return render(
    <QueryClientProvider client={queryClient}>
      <MemoryRouter initialEntries={['/conversation/session-1']}>
        <Routes>
          <Route path="/conversation" element={<div>scenarios page</div>} />
          <Route path="/conversation/:sessionId" element={<ConversationChatPage />} />
        </Routes>
      </MemoryRouter>
    </QueryClientProvider>,
  )
}

describe('ConversationChatPage', () => {
  beforeEach(() => {
    useAuthStore.setState({ token: 'a-token', user: testUser, isAuthenticated: true })
    vi.restoreAllMocks()
  })

  it('shows the conversation and sends a message', async () => {
    const user = userEvent.setup()
    vi.spyOn(conversationApi, 'fetchConversationSession').mockResolvedValue(testSession)
    vi.spyOn(conversationApi, 'sendConversationMessage').mockResolvedValue({
      user_message: {
        role: 'user',
        content: 'ラーメンをください。',
        translation: null,
        created_at: '2026-01-01T00:01:00Z',
      },
      character_message: {
        role: 'character',
        content: 'はい、少々お待ちください。',
        translation: 'Sure, please wait a moment.',
        created_at: '2026-01-01T00:01:05Z',
      },
      xp_earned: 3,
      total_xp: 3,
    })

    renderPage()

    expect(await screen.findByText('いらっしゃいませ！何にしますか？')).toBeInTheDocument()

    const input = screen.getByPlaceholderText('Type in Japanese…')
    await user.type(input, 'ラーメンをください。')
    await user.click(screen.getByRole('button', { name: 'Send' }))

    expect(conversationApi.sendConversationMessage).toHaveBeenCalledWith(
      'a-token',
      'session-1',
      'ラーメンをください。',
    )
    expect(await screen.findByText('はい、少々お待ちください。')).toBeInTheDocument()
    expect(screen.getByText('+3 XP earned')).toBeInTheDocument()
  })

  it('shows an error message when sending fails', async () => {
    const user = userEvent.setup()
    vi.spyOn(conversationApi, 'fetchConversationSession').mockResolvedValue(testSession)
    vi.spyOn(conversationApi, 'sendConversationMessage').mockRejectedValue(new Error('boom'))

    renderPage()

    const input = await screen.findByPlaceholderText('Type in Japanese…')
    await user.type(input, 'ラーメンをください。')
    await user.click(screen.getByRole('button', { name: 'Send' }))

    expect(
      await screen.findByText('The character could not respond. Please try again.'),
    ).toBeInTheDocument()
  })

  it('redirects to the scenario picker for an unknown session', async () => {
    vi.spyOn(conversationApi, 'fetchConversationSession').mockRejectedValue(
      new ApiError(404, 'not found'),
    )

    renderPage()

    expect(await screen.findByText('scenarios page')).toBeInTheDocument()
  })
})
