import type { Citation, WSMessage } from '@/types'

export interface ChatWSOptions {
  onMessage: (msg: WSMessage) => void
  onError?: (error: Event) => void
  onClose?: (event: CloseEvent) => void
}

export interface MeetingEventsWSOptions {
  onMessage: (msg: WSMessage) => void
  onError?: (error: Event) => void
  onClose?: (event: CloseEvent) => void
}

function getWSBaseURL(): string {
  const baseURL = import.meta.env.VITE_WS_BASE_URL ?? ''
  if (baseURL) return baseURL
  const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
  return `${protocol}//${window.location.host}/api/v1`
}

export function createChatWebSocket(options: ChatWSOptions) {
  const url = `${getWSBaseURL()}/chat`
  const ws = new WebSocket(url)

  ws.onmessage = (event: MessageEvent) => {
    try {
      const data: WSMessage = JSON.parse(event.data)
      options.onMessage(data)
    } catch {
      // ignore non-JSON messages
    }
  }

  ws.onerror = (event) => {
    options.onError?.(event)
  }

  ws.onclose = (event) => {
    options.onClose?.(event)
  }

  function sendQuestion(question: string, meetingId?: string, scope?: 'current_meeting' | 'all_meetings') {
    ws.send(JSON.stringify({
      type: 'question',
      question,
      meeting_id: meetingId ?? null,
      scope: scope ?? 'current_meeting',
    }))
  }

  function close() {
    ws.close()
  }

  return { ws, sendQuestion, close }
}

export function createMeetingEventsWebSocket(meetingId: string, options: MeetingEventsWSOptions) {
  const url = `${getWSBaseURL()}/meetings/${meetingId}/events`
  const ws = new WebSocket(url)

  ws.onmessage = (event: MessageEvent) => {
    try {
      const data: WSMessage = JSON.parse(event.data)
      options.onMessage(data)
    } catch {
      // ignore non-JSON messages
    }
  }

  ws.onerror = (event) => {
    options.onError?.(event)
  }

  ws.onclose = (event) => {
    options.onClose?.(event)
  }

  function sendPing() {
    ws.send(JSON.stringify({ action: 'ping' }))
  }

  function close() {
    ws.close()
  }

  return { ws, sendPing, close }
}

export type { Citation }
