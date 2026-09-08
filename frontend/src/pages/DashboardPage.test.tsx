import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { MemoryRouter, Route, Routes } from 'react-router-dom'
import { beforeEach, describe, expect, it, vi } from 'vitest'
import { ApiError } from '../services/httpErrors'
import * as profileApi from '../services/profileApi'
import * as recommendationsApi from '../services/recommendationsApi'
import { useAuthStore } from '../stores/authStore'
import type { LearnerProfile } from '../types/profile'
import DashboardPage from './DashboardPage'

const testUser = { id: '1', email: 'test@example.com', created_at: '2026-01-01T00:00:00Z' }

const testProfile: LearnerProfile = {
  user_id: '1',
  goals: ['anime_manga', 'jlpt'],
  experience: 'knows_hiragana',
  preferred_level: 'N5',
  estimated_level: null,
  jlpt_target: 'N3',
  xp: 0,
  onboarding_completed: true,
  created_at: '2026-01-01T00:00:00Z',
  updated_at: '2026-01-01T00:00:00Z',
}

function renderDashboard() {
  const queryClient = new QueryClient({ defaultOptions: { queries: { retry: false } } })
  return render(
    <QueryClientProvider client={queryClient}>
      <MemoryRouter initialEntries={['/dashboard']}>
        <Routes>
          <Route path="/dashboard" element={<DashboardPage />} />
          <Route path="/onboarding" element={<div>Onboarding page</div>} />
        </Routes>
      </MemoryRouter>
    </QueryClientProvider>,
  )
}

describe('DashboardPage', () => {
  beforeEach(() => {
    useAuthStore.setState({ token: 'a-token', user: testUser, isAuthenticated: true })
    vi.restoreAllMocks()
    vi.spyOn(recommendationsApi, 'fetchRecommendations').mockResolvedValue({ recommendations: [] })
  })

  it('redirects to onboarding when no profile exists yet', async () => {
    vi.spyOn(profileApi, 'fetchProfile').mockRejectedValue(new ApiError(404, 'not found'))

    renderDashboard()

    expect(await screen.findByText('Onboarding page')).toBeInTheDocument()
  })

  it('shows the profile summary once loaded', async () => {
    vi.spyOn(profileApi, 'fetchProfile').mockResolvedValue(testProfile)

    renderDashboard()

    expect(await screen.findByText('Anime / manga, JLPT')).toBeInTheDocument()
    expect(screen.getByText('JLPT goal').nextElementSibling).toHaveTextContent('N3')
    expect(screen.getByText('Not enough data yet.')).toBeInTheDocument()
  })

  it('changes the preferred level without restriction when a level button is clicked', async () => {
    const user = userEvent.setup()
    vi.spyOn(profileApi, 'fetchProfile').mockResolvedValue(testProfile)
    vi.spyOn(profileApi, 'updateProfile').mockResolvedValue({ ...testProfile, preferred_level: 'N2' })

    renderDashboard()

    await screen.findByText('Anime / manga, JLPT')
    await user.click(screen.getByRole('button', { name: 'N2' }))

    expect(profileApi.updateProfile).toHaveBeenCalledWith('a-token', { preferred_level: 'N2' })
  })

  it('shows recommendations with a link to act on them', async () => {
    vi.spyOn(profileApi, 'fetchProfile').mockResolvedValue(testProfile)
    vi.spyOn(recommendationsApi, 'fetchRecommendations').mockResolvedValue({
      recommendations: [
        {
          category: 'vocabulary',
          reason: 'weak_mastery',
          message: 'Your vocabulary mastery is 33% — review some flashcards or try another quiz.',
          mastery: 0.33,
          action_label: 'Practice vocabulary',
          action_path: '/quiz',
        },
      ],
    })

    renderDashboard()

    expect(await screen.findByText('Recommended for you')).toBeInTheDocument()
    expect(
      screen.getByText('Your vocabulary mastery is 33% — review some flashcards or try another quiz.'),
    ).toBeInTheDocument()
    expect(screen.getByRole('link', { name: 'Practice vocabulary' })).toHaveAttribute(
      'href',
      '/quiz',
    )
  })

  it('shows no recommendations panel when there is nothing to recommend', async () => {
    vi.spyOn(profileApi, 'fetchProfile').mockResolvedValue(testProfile)
    vi.spyOn(recommendationsApi, 'fetchRecommendations').mockResolvedValue({ recommendations: [] })

    renderDashboard()

    await screen.findByText('Anime / manga, JLPT')
    expect(screen.queryByText('Recommended for you')).not.toBeInTheDocument()
  })
})
