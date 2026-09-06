import type { AuthResponse, User } from '../types/auth'
import { API_BASE_URL } from './api'

export class ApiError extends Error {
  status: number

  constructor(status: number, message: string) {
    super(message)
    this.status = status
  }
}

interface ErrorBody {
  detail?: string | { msg: string }[]
}

async function parseErrorMessage(response: Response): Promise<string> {
  try {
    const body: ErrorBody = await response.json()
    if (typeof body.detail === 'string') return body.detail
    if (Array.isArray(body.detail)) return body.detail.map((d) => d.msg).join(', ')
  } catch {
    // response had no JSON body
  }
  return `Request failed with status ${response.status}`
}

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
