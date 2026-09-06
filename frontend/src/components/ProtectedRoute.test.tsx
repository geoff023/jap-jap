import { render, screen } from '@testing-library/react'
import { MemoryRouter, Route, Routes } from 'react-router-dom'
import { beforeEach, describe, expect, it } from 'vitest'
import { useAuthStore } from '../stores/authStore'
import ProtectedRoute from './ProtectedRoute'

function renderProtected() {
  return render(
    <MemoryRouter initialEntries={['/dashboard']}>
      <Routes>
        <Route path="/login" element={<div>Login page</div>} />
        <Route
          path="/dashboard"
          element={
            <ProtectedRoute>
              <div>Secret dashboard</div>
            </ProtectedRoute>
          }
        />
      </Routes>
    </MemoryRouter>,
  )
}

describe('ProtectedRoute', () => {
  beforeEach(() => {
    useAuthStore.setState({ token: null, user: null, isAuthenticated: false })
  })

  it('redirects to /login when not authenticated', () => {
    renderProtected()

    expect(screen.getByText('Login page')).toBeInTheDocument()
    expect(screen.queryByText('Secret dashboard')).not.toBeInTheDocument()
  })

  it('renders the protected content when authenticated', () => {
    useAuthStore.getState().setAuth('token', {
      id: '1',
      email: 'test@example.com',
      created_at: '2026-01-01T00:00:00Z',
    })

    renderProtected()

    expect(screen.getByText('Secret dashboard')).toBeInTheDocument()
  })
})
