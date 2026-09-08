import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { MemoryRouter, Route, Routes } from 'react-router-dom'
import { beforeEach, describe, expect, it, vi } from 'vitest'
import * as useAudioRecorderModule from '../hooks/useAudioRecorder'
import * as speechApi from '../services/speechApi'
import { useAuthStore } from '../stores/authStore'
import SpeakingPracticePage from './SpeakingPracticePage'

vi.mock('../hooks/useAudioRecorder')

const testUser = { id: '1', email: 'test@example.com', created_at: '2026-01-01T00:00:00Z' }

const testPrompt = {
  key: 'n5-greeting',
  level: 'N5' as const,
  target_text: 'おはようございます',
  target_reading: 'おはようございます',
  target_translation: 'Good morning.',
}

function mockRecorder(overrides: Partial<ReturnType<typeof useAudioRecorderModule.useAudioRecorder>>) {
  vi.mocked(useAudioRecorderModule.useAudioRecorder).mockReturnValue({
    status: 'idle',
    audioBlob: null,
    start: vi.fn(),
    stop: vi.fn(),
    reset: vi.fn(),
    ...overrides,
  })
}

function renderPage() {
  const queryClient = new QueryClient()
  return render(
    <QueryClientProvider client={queryClient}>
      <MemoryRouter initialEntries={['/speaking']}>
        <Routes>
          <Route path="/speaking" element={<SpeakingPracticePage />} />
        </Routes>
      </MemoryRouter>
    </QueryClientProvider>,
  )
}

describe('SpeakingPracticePage', () => {
  beforeEach(() => {
    useAuthStore.setState({ token: 'a-token', user: testUser, isAuthenticated: true })
    vi.restoreAllMocks()
    mockRecorder({})
  })

  it('lists prompts and shows the target phrase after selecting one', async () => {
    const user = userEvent.setup()
    vi.spyOn(speechApi, 'fetchSpeakingPrompts').mockResolvedValue([testPrompt])

    renderPage()

    expect(await screen.findByText('おはようございます')).toBeInTheDocument()
    await user.click(screen.getByText('Good morning.'))

    expect(screen.getByText('Good morning.')).toBeInTheDocument()
    expect(screen.getByRole('button', { name: '🎙️ Start recording' })).toBeInTheDocument()
  })

  it('submits the recording and shows the result', async () => {
    const user = userEvent.setup()
    vi.spyOn(speechApi, 'fetchSpeakingPrompts').mockResolvedValue([testPrompt])
    vi.spyOn(speechApi, 'submitSpeakingAttempt').mockResolvedValue({
      transcript: 'おはようございます',
      target_text: 'おはようございます',
      correct: true,
      similarity: 1,
      xp_earned: 10,
      total_xp: 10,
    })
    mockRecorder({ status: 'stopped', audioBlob: new Blob(['audio']) })

    renderPage()

    await user.click(await screen.findByText('Good morning.'))
    await user.click(screen.getByRole('button', { name: 'Submit recording' }))

    expect(speechApi.submitSpeakingAttempt).toHaveBeenCalledWith(
      'a-token',
      'n5-greeting',
      expect.any(Blob),
    )
    expect(await screen.findByText('Nice pronunciation!')).toBeInTheDocument()
    expect(screen.getByText('100% match · +10 XP')).toBeInTheDocument()
  })

  it('shows an error message when submission fails', async () => {
    const user = userEvent.setup()
    vi.spyOn(speechApi, 'fetchSpeakingPrompts').mockResolvedValue([testPrompt])
    vi.spyOn(speechApi, 'submitSpeakingAttempt').mockRejectedValue(new Error('boom'))
    mockRecorder({ status: 'stopped', audioBlob: new Blob(['audio']) })

    renderPage()

    await user.click(await screen.findByText('Good morning.'))
    await user.click(screen.getByRole('button', { name: 'Submit recording' }))

    expect(
      await screen.findByText('Could not check your pronunciation. Please try again.'),
    ).toBeInTheDocument()
  })

  it('shows a message when recording is unsupported', async () => {
    const user = userEvent.setup()
    vi.spyOn(speechApi, 'fetchSpeakingPrompts').mockResolvedValue([testPrompt])
    mockRecorder({ status: 'unsupported' })

    renderPage()

    await user.click(await screen.findByText('Good morning.'))

    expect(
      screen.getByText("Your browser doesn't support audio recording."),
    ).toBeInTheDocument()
  })
})
