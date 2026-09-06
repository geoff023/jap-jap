import type { AuthResponse, User } from '../types/auth'
import { API_BASE_URL } from './api'
import { ApiError, parseErrorMessage } from './httpErrors'

export { ApiError } from './httpErrors'

async function postJson<T>(path: string, payload: unknown): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  })
  if (!response.ok) {
    throw new ApiError(response.status, await parseErrorMessage(response))
  }
  return response.json()
}

export function register(email: string, password: string): Promise<AuthResponse> {
  return postJson<AuthResponse>('/api/auth/register', { email, password })
}

export function login(email: string, password: string): Promise<AuthResponse> {
  return postJson<AuthResponse>('/api/auth/login', { email, password })
}

export async function logout(token: string): Promise<void> {
  await fetch(`${API_BASE_URL}/api/auth/logout`, {
    method: 'POST',
    headers: { Authorization: `Bearer ${token}` },
  })
}

export async function fetchMe(token: string): Promise<User> {
  const response = await fetch(`${API_BASE_URL}/api/users/me`, {
    headers: { Authorization: `Bearer ${token}` },
  })
  if (!response.ok) {
    throw new ApiError(response.status, await parseErrorMessage(response))
  }
  return response.json()
}
