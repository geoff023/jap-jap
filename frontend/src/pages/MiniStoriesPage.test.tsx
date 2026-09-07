import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { MemoryRouter } from 'react-router-dom'
import { beforeEach, describe, expect, it, vi } from 'vitest'
import * as aiGenerationApi from '../services/aiGenerationApi'
import { useAuthStore } from '../stores/authStore'
import MiniStoriesPage from './MiniStoriesPage'

const testUser = { id: '1', email: 'test@example.com', created_at: '2026-01-01T00:00:00Z' }

function renderPage() {
  return render(
    <MemoryRouter>
      <MiniStoriesPage />
    </MemoryRouter>,
  )
}

describe('MiniStoriesPage', () => {
  beforeEach(() => {
    useAuthStore.setState({ token: 'a-token', user: testUser, isAuthenticated: true })
    vi.restoreAllMocks()
  })

  it('generates a story, answers comprehension questions, and shows the score', async () => {
    const user = userEvent.setup()
    vi.spyOn(aiGenerationApi, 'generateMiniStory').mockResolvedValue({
      id: 'story-1',
      title: 'A Trip to the Store',
      level: 'N5',
      story: '今日、店に行きました。',
      translation: 'Today, I went to the store.',
      vocab_highlights: ['店'],
      comprehension_questions: [
        { index: 0, prompt: 'Where did they go?', options: ['school', 'the store', 'home', 'park'] },
      ],
    })
    vi.spyOn(aiGenerationApi, 'submitComprehension').mockResolvedValue({
      score: 1,
      total: 1,
      xp_earned: 10,
      total_xp: 10,
      results: [
        {
          index: 0,
          selected: 'the store',
          correct: true,
          correct_answer: 'the store',
          explanation: 'The story says they went to the store.',
        },
      ],
    })

    renderPage()

    await user.click(screen.getByRole('button', { name: 'Generate a story' }))

    expect(await screen.findByText('A Trip to the Store')).toBeInTheDocument()
    await user.click(screen.getByRole('radio', { name: 'the store' }))
    await user.click(screen.getByRole('button', { name: 'Submit answers' }))

    expect(aiGenerationApi.submitComprehension).toHaveBeenCalledWith('a-token', 'story-1', [
      { index: 0, selected: 'the store' },
    ])
    expect(await screen.findByText('1 / 1 correct · +10 XP earned')).toBeInTheDocument()
  })

  it('shows an error message when generation fails', async () => {
    const user = userEvent.setup()
    vi.spyOn(aiGenerationApi, 'generateMiniStory').mockRejectedValue(new Error('boom'))

    renderPage()

    await user.click(screen.getByRole('button', { name: 'Generate a story' }))

    expect(
      await screen.findByText('Could not generate a story. Please try again.'),
    ).toBeInTheDocument()
  })
})
