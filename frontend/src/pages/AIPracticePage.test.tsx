import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { MemoryRouter } from 'react-router-dom'
import { beforeEach, describe, expect, it, vi } from 'vitest'
import * as aiGenerationApi from '../services/aiGenerationApi'
import { useAuthStore } from '../stores/authStore'
import AIPracticePage from './AIPracticePage'

const testUser = { id: '1', email: 'test@example.com', created_at: '2026-01-01T00:00:00Z' }

function renderPage() {
  return render(
    <MemoryRouter>
      <AIPracticePage />
    </MemoryRouter>,
  )
}

describe('AIPracticePage', () => {
  beforeEach(() => {
    useAuthStore.setState({ token: 'a-token', user: testUser, isAuthenticated: true })
    vi.restoreAllMocks()
  })

  it('generates a question, submits an answer, and shows the result', async () => {
    const user = userEvent.setup()
    vi.spyOn(aiGenerationApi, 'generateVocabularyQuestion').mockResolvedValue({
      id: 'q1',
      category: 'vocabulary',
      level: 'N5',
      concept: '食べる',
      prompt: 'What does "食べる" mean?',
      options: ['to eat', 'to drink', 'to see', 'to go'],
    })
    vi.spyOn(aiGenerationApi, 'submitGeneratedQuestion').mockResolvedValue({
      correct: true,
      correct_answer: 'to eat',
      explanation: "食べる means 'to eat'.",
      xp_earned: 10,
      total_xp: 10,
    })

    renderPage()

    await user.click(screen.getByRole('button', { name: 'Generate a question' }))

    expect(await screen.findByText('What does "食べる" mean?')).toBeInTheDocument()
    await user.click(screen.getByRole('radio', { name: 'to eat' }))
    await user.click(screen.getByRole('button', { name: 'Submit answer' }))

    expect(aiGenerationApi.submitGeneratedQuestion).toHaveBeenCalledWith(
      'a-token',
      'q1',
      'to eat',
    )
    expect(await screen.findByText('Correct!')).toBeInTheDocument()
    expect(screen.getByText("食べる means 'to eat'.")).toBeInTheDocument()
  })

  it('shows an error message when generation fails', async () => {
    const user = userEvent.setup()
    vi.spyOn(aiGenerationApi, 'generateVocabularyQuestion').mockRejectedValue(new Error('boom'))

    renderPage()

    await user.click(screen.getByRole('button', { name: 'Generate a question' }))

    expect(
      await screen.findByText('Could not generate a question. Please try again.'),
    ).toBeInTheDocument()
  })
})
