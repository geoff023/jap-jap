import { render, screen, within } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { MemoryRouter } from 'react-router-dom'
import { beforeEach, describe, expect, it, vi } from 'vitest'
import * as profileApi from '../services/profileApi'
import { useAuthStore } from '../stores/authStore'
import OnboardingPage from './OnboardingPage'

const testUser = { id: '1', email: 'test@example.com', created_at: '2026-01-01T00:00:00Z' }

describe('OnboardingPage', () => {
  beforeEach(() => {
    useAuthStore.setState({ token: 'a-token', user: testUser, isAuthenticated: true })
    vi.restoreAllMocks()
  })

  it('shows an error when submitting without selecting a goal', async () => {
    const user = userEvent.setup()
    const submitSpy = vi.spyOn(profileApi, 'submitOnboarding')

    render(
      <MemoryRouter>
        <OnboardingPage />
      </MemoryRouter>,
    )

    await user.click(screen.getByRole('button', { name: "Let's go" }))

    expect(
      await screen.findByText('Pick at least one reason you are learning Japanese.'),
    ).toBeInTheDocument()
    expect(submitSpy).not.toHaveBeenCalled()
  })

  it('submits the selected answers and navigates to the dashboard', async () => {
    const user = userEvent.setup()
    vi.spyOn(profileApi, 'submitOnboarding').mockResolvedValue({
      user_id: '1',
      goals: ['anime_manga'],
      experience: 'knows_hiragana',
      preferred_level: 'N5',
      estimated_level: null,
      jlpt_target: null,
      xp: 0,
      onboarding_completed: true,
      created_at: '2026-01-01T00:00:00Z',
      updated_at: '2026-01-01T00:00:00Z',
    })

    render(
      <MemoryRouter>
        <OnboardingPage />
      </MemoryRouter>,
    )

    await user.click(screen.getByText('Anime / manga'))
    await user.click(screen.getByText('Know hiragana'))
    const startingLevelGroup = screen.getByRole('group', { name: 'Starting level' })
    await user.click(within(startingLevelGroup).getByRole('radio', { name: 'N5' }))
    await user.click(screen.getByRole('button', { name: "Let's go" }))

    expect(profileApi.submitOnboarding).toHaveBeenCalledWith('a-token', {
      goals: ['anime_manga'],
      experience: 'knows_hiragana',
      preferred_level: 'N5',
      jlpt_target: null,
    })
  })
})
