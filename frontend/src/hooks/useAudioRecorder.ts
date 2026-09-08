import { useCallback, useRef, useState } from 'react'

export type RecorderStatus = 'idle' | 'recording' | 'stopped' | 'unsupported' | 'denied'

interface AudioRecorder {
  status: RecorderStatus
  audioBlob: Blob | null
  start: () => Promise<void>
  stop: () => void
  reset: () => void
}

function isSupported(): boolean {
  return (
    typeof navigator !== 'undefined' &&
    Boolean(navigator.mediaDevices?.getUserMedia) &&
    typeof window !== 'undefined' &&
    Boolean(window.MediaRecorder)
  )
}

export function useAudioRecorder(): AudioRecorder {
  const [status, setStatus] = useState<RecorderStatus>(isSupported() ? 'idle' : 'unsupported')
  const [audioBlob, setAudioBlob] = useState<Blob | null>(null)
  const mediaRecorderRef = useRef<MediaRecorder | null>(null)
  const chunksRef = useRef<Blob[]>([])
  const streamRef = useRef<MediaStream | null>(null)

  const start = useCallback(async () => {
    if (!isSupported()) {
      setStatus('unsupported')
      return
    }
    setAudioBlob(null)
    chunksRef.current = []
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true })
      streamRef.current = stream
      const recorder = new MediaRecorder(stream)
      mediaRecorderRef.current = recorder
      recorder.ondataavailable = (event) => {
        if (event.data.size > 0) chunksRef.current.push(event.data)
      }
      recorder.onstop = () => {
        setAudioBlob(new Blob(chunksRef.current, { type: recorder.mimeType || 'audio/webm' }))
        streamRef.current?.getTracks().forEach((track) => track.stop())
        streamRef.current = null
      }
      recorder.start()
      setStatus('recording')
    } catch {
      setStatus('denied')
    }
  }, [])

  const stop = useCallback(() => {
    mediaRecorderRef.current?.stop()
    setStatus('stopped')
  }, [])

  const reset = useCallback(() => {
    setAudioBlob(null)
    setStatus(isSupported() ? 'idle' : 'unsupported')
  }, [])

  return { status, audioBlob, start, stop, reset }
}
