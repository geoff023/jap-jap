import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { MemoryRouter } from 'react-router-dom'
import { beforeEach, describe, expect, it, vi } from 'vitest'
import * as activityApi from '../services/activityApi'
import { useAuthStore } from '../stores/authStore'
import type { VocabularyItem } from '../types/activity'
import FlashcardsPage from './FlashcardsPage'

const testUser = { id: '1', email: 'test@example.com', created_at: '2026-01-01T00:00:00Z' }

const deck: VocabularyItem[] = [
  {
    id: 'v1',
    term: '食べる',
    reading: 'たべる',
    meaning: 'to eat',
    level: 'N5',
    example_sentence: null,
    example_translation: null,
  },
  {
    id: 'v2',
    term: '飲む',
    reading: 'のむ',
    meaning: 'to drink',
    level: 'N5',
    example_sentence: null,
    example_translation: null,
  },
]

function renderPage() {
  const queryClient = new QueryClient({ defaultOptions: { queries: { retry: false } } })
  return render(
    <QueryClientProvider client={queryClient}>
      <MemoryRouter>
        <FlashcardsPage />
      </MemoryRouter>
    </QueryClientProvider>,
  )
}

describe('FlashcardsPage', () => {
  beforeEach(() => {
    useAuthStore.setState({ token: 'a-token', user: testUser, isAuthenticated: true })
    vi.restoreAllMocks()
  })

  it('walks through the deck and reports XP earned on completion', async () => {
    const user = userEvent.setup()
    vi.spyOn(activityApi, 'fetchVocabulary').mockResolvedValue(deck)
    vi.spyOn(activityApi, 'completeFlashcards').mockResolvedValue({
      known_count: 1,
      total: 2,
      xp_earned: 5,
      total_xp: 5,
    })

    renderPage()

    expect(await screen.findByText('食べる')).toBeInTheDocument()
    await user.click(screen.getByRole('button', { name: 'Show answer' }))
    await user.click(screen.getByRole('button', { name: 'Know it' }))

    expect(await screen.findByText('飲む')).toBeInTheDocument()
    await user.click(screen.getByRole('button', { name: 'Show answer' }))
    await user.click(screen.getByRole('button', { name: 'Still learning' }))

    expect(await screen.findByText('Deck complete!')).toBeInTheDocument()
    expect(screen.getByText('+5 XP earned · 5 XP total')).toBeInTheDocument()
    expect(activityApi.completeFlashcards).toHaveBeenCalledWith('a-token', {
      category: 'vocabulary',
      level: 'N5',
      reviewed: [
        { item_id: 'v1', known: true },
        { item_id: 'v2', known: false },
      ],
    })
  })
})
