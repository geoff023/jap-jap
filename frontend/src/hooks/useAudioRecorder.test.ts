import { act, renderHook } from '@testing-library/react'
import { beforeEach, describe, expect, it, vi } from 'vitest'
import { useAudioRecorder } from './useAudioRecorder'

class FakeMediaRecorder {
  static instances: FakeMediaRecorder[] = []
  state = 'inactive'
  mimeType = 'audio/webm'
  ondataavailable: ((event: { data: Blob }) => void) | null = null
  onstop: (() => void) | null = null
  stream: MediaStream

  constructor(stream: MediaStream) {
    this.stream = stream
    FakeMediaRecorder.instances.push(this)
  }

  start() {
    this.state = 'recording'
  }

  stop() {
    this.state = 'inactive'
    this.ondataavailable?.({ data: new Blob(['audio-data']) })
    this.onstop?.()
  }
}

describe('useAudioRecorder', () => {
  const stopTrack = vi.fn()

  beforeEach(() => {
    FakeMediaRecorder.instances = []
    stopTrack.mockClear()
    vi.stubGlobal('MediaRecorder', FakeMediaRecorder)
    const fakeStream = { getTracks: () => [{ stop: stopTrack }] } as unknown as MediaStream
    Object.defineProperty(navigator, 'mediaDevices', {
      value: { getUserMedia: vi.fn().mockResolvedValue(fakeStream) },
      configurable: true,
    })
  })

  it('starts idle, then records and produces an audio blob on stop', async () => {
    const { result } = renderHook(() => useAudioRecorder())
    expect(result.current.status).toBe('idle')

    await act(async () => {
      await result.current.start()
    })
    expect(result.current.status).toBe('recording')

    act(() => {
      result.current.stop()
    })
    expect(result.current.status).toBe('stopped')
    expect(result.current.audioBlob).toBeInstanceOf(Blob)
    expect(stopTrack).toHaveBeenCalled()
  })

  it('reports denied when microphone access is rejected', async () => {
    vi.mocked(navigator.mediaDevices.getUserMedia).mockRejectedValue(new Error('denied'))

    const { result } = renderHook(() => useAudioRecorder())
    await act(async () => {
      await result.current.start()
    })

    expect(result.current.status).toBe('denied')
    expect(result.current.audioBlob).toBeNull()
  })

  it('reports unsupported when MediaRecorder is unavailable', async () => {
    vi.stubGlobal('MediaRecorder', undefined)

    const { result } = renderHook(() => useAudioRecorder())
    expect(result.current.status).toBe('unsupported')
  })

  it('resets back to idle', async () => {
    const { result } = renderHook(() => useAudioRecorder())
    await act(async () => {
      await result.current.start()
    })
    act(() => {
      result.current.stop()
    })

    act(() => {
      result.current.reset()
    })
    expect(result.current.status).toBe('idle')
    expect(result.current.audioBlob).toBeNull()
  })
})
