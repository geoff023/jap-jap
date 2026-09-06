import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { MemoryRouter } from 'react-router-dom'
import { beforeEach, describe, expect, it, vi } from 'vitest'
import * as authApi from '../services/authApi'
import { useAuthStore } from '../stores/authStore'
import LoginPage from './LoginPage'

describe('LoginPage', () => {
  beforeEach(() => {
    useAuthStore.setState({ token: null, user: null, isAuthenticated: false })
    vi.restoreAllMocks()
  })

  it('logs in and updates the auth store on valid credentials', async () => {
    const user = userEvent.setup()
    vi.spyOn(authApi, 'login').mockResolvedValue({
      access_token: 'a-token',
      token_type: 'bearer',
      user: { id: '1', email: 'test@example.com', created_at: '2026-01-01T00:00:00Z' },
    })

    render(
      <MemoryRouter>
        <LoginPage />
      </MemoryRouter>,
    )

    await user.type(screen.getByLabelText('Email'), 'test@example.com')
    await user.type(screen.getByLabelText('Password'), 'supersecret1')
    await user.click(screen.getByRole('button', { name: /log in/i }))

    expect(authApi.login).toHaveBeenCalledWith('test@example.com', 'supersecret1')
    expect(await screen.findByRole('button', { name: /log in/i })).toBeInTheDocument()
    expect(useAuthStore.getState().isAuthenticated).toBe(true)
  })

  it('shows an error message when login fails', async () => {
    const user = userEvent.setup()
    vi.spyOn(authApi, 'login').mockRejectedValue(
      new authApi.ApiError(401, 'Invalid email or password'),
    )

    render(
      <MemoryRouter>
        <LoginPage />
      </MemoryRouter>,
    )

    await user.type(screen.getByLabelText('Email'), 'test@example.com')
    await user.type(screen.getByLabelText('Password'), 'wrongpassword')
    await user.click(screen.getByRole('button', { name: /log in/i }))

    expect(await screen.findByText('Invalid email or password')).toBeInTheDocument()
    expect(useAuthStore.getState().isAuthenticated).toBe(false)
  })
})
