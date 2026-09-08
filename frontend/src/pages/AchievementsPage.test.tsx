import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { render, screen } from '@testing-library/react'
import { MemoryRouter, Route, Routes } from 'react-router-dom'
import { beforeEach, describe, expect, it, vi } from 'vitest'
import * as achievementsApi from '../services/achievementsApi'
import { useAuthStore } from '../stores/authStore'
import AchievementsPage from './AchievementsPage'

const testUser = { id: '1', email: 'test@example.com', created_at: '2026-01-01T00:00:00Z' }

function renderPage() {
  const queryClient = new QueryClient()
  return render(
    <QueryClientProvider client={queryClient}>
      <MemoryRouter initialEntries={['/achievements']}>
        <Routes>
          <Route path="/achievements" element={<AchievementsPage />} />
        </Routes>
      </MemoryRouter>
    </QueryClientProvider>,
  )
}

describe('AchievementsPage', () => {
  beforeEach(() => {
    useAuthStore.setState({ token: 'a-token', user: testUser, isAuthenticated: true })
    vi.restoreAllMocks()
  })

  it('shows the unlocked count and each achievement', async () => {
    vi.spyOn(achievementsApi, 'fetchAchievements').mockResolvedValue([
      {
        key: 'first_steps',
        name: 'First Steps',
        description: 'Complete your first quiz, flashcard set, or test.',
        emoji: '🎯',
        earned: true,
        unlocked_at: '2026-01-01T00:00:00Z',
      },
      {
        key: 'century_club',
        name: 'Century Club',
        description: 'Earn 100 XP.',
        emoji: '💯',
        earned: false,
        unlocked_at: null,
      },
    ])

    renderPage()

    expect(await screen.findByText('1 / 2 unlocked')).toBeInTheDocument()
    expect(screen.getByText('First Steps')).toBeInTheDocument()
    expect(screen.getByText('Century Club')).toBeInTheDocument()
    expect(screen.getByText(/Unlocked/)).toBeInTheDocument()
  })
})
