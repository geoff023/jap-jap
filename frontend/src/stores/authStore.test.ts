import { beforeEach, describe, expect, it } from 'vitest'
import { useAuthStore } from './authStore'

const testUser = { id: '1', email: 'test@example.com', created_at: '2026-01-01T00:00:00Z' }

describe('authStore', () => {
  beforeEach(() => {
    useAuthStore.setState({ token: null, user: null, isAuthenticated: false })
  })

  it('starts unauthenticated', () => {
    expect(useAuthStore.getState().isAuthenticated).toBe(false)
    expect(useAuthStore.getState().user).toBeNull()
  })

  it('setAuth stores the token and user and marks authenticated', () => {
    useAuthStore.getState().setAuth('a-token', testUser)

    const state = useAuthStore.getState()
    expect(state.token).toBe('a-token')
    expect(state.user).toEqual(testUser)
    expect(state.isAuthenticated).toBe(true)
  })

  it('clearAuth resets to the unauthenticated state', () => {
    useAuthStore.getState().setAuth('a-token', testUser)
    useAuthStore.getState().clearAuth()

    const state = useAuthStore.getState()
    expect(state.token).toBeNull()
    expect(state.user).toBeNull()
    expect(state.isAuthenticated).toBe(false)
  })
})
