import { render, screen } from '@testing-library/react'
import { describe, expect, it, vi } from 'vitest'
import App from './App'

vi.stubGlobal(
  'fetch',
  vi.fn(() => Promise.reject(new Error('network unavailable in tests'))),
)

describe('App', () => {
  it('renders the JapJap landing page', async () => {
    render(<App />)

    const heading = await screen.findByRole('heading', { level: 1 })
    expect(heading).toHaveTextContent('JapJap')
    expect(screen.getByText('Explore')).toBeInTheDocument()
    expect(screen.getByText('Speak')).toBeInTheDocument()
    expect(screen.getByText('JLPT')).toBeInTheDocument()
  })

  it('does not crash when the backend health check fails', async () => {
    render(<App />)

    expect(await screen.findByText('Backend unavailable')).toBeInTheDocument()
  })
})
