import { ref, onUnmounted } from 'vue'
import type { WSMessage } from '@/types'
import {
  createChatWebSocket,
  createMeetingEventsWebSocket,
} from '@/api/chat'
import { useAgentStore } from '@/stores/agent'

type WSConnectionType = 'chat' | 'events'

export function useWebSocket() {
  const agentStore = useAgentStore()

  const isConnected = ref(false)
  const lastMessage = ref<WSMessage | null>(null)

  let wsHandle: ReturnType<typeof createChatWebSocket> | ReturnType<typeof createMeetingEventsWebSocket> | null = null
  let reconnectAttempts = 0
  const maxReconnectAttempts = 3
  let reconnectTimer: ReturnType<typeof setTimeout> | null = null

  function connect(type: WSConnectionType, meetingId?: string) {
    disconnect()

    const onMessage = (msg: WSMessage) => {
      lastMessage.value = msg

      if (type === 'chat') {
        if (msg.type === 'chunk' && msg.message) {
          agentStore.updateLastAssistantMessage(msg.message)
        } else if (msg.type === 'end') {
          agentStore.setStreaming(false)
        } else if (msg.type === 'error') {
          agentStore.setStreaming(false)
        }
      }
    }

    const onError = () => {
      isConnected.value = false
      attemptReconnect(type, meetingId)
    }

    const onClose = () => {
      isConnected.value = false
    }

    if (type === 'chat') {
      wsHandle = createChatWebSocket({
        onMessage,
        onError,
        onClose,
      })
    } else if (type === 'events' && meetingId) {
      wsHandle = createMeetingEventsWebSocket(meetingId, {
        onMessage,
        onError,
        onClose,
      })
    }

    isConnected.value = true
    reconnectAttempts = 0
  }

  function attemptReconnect(type: WSConnectionType, meetingId?: string) {
    if (reconnectAttempts >= maxReconnectAttempts) return

    const delay = Math.pow(2, reconnectAttempts) * 1000
    reconnectAttempts++

    reconnectTimer = setTimeout(() => {
      connect(type, meetingId)
    }, delay)
  }

  function send(data: Record<string, unknown>) {
    if (wsHandle && 'sendQuestion' in wsHandle) {
      wsHandle.sendQuestion(
        data.question as string,
        data.meeting_id as string | undefined,
        data.scope as 'current_meeting' | 'all_meetings' | undefined,
      )
    } else if (wsHandle && 'sendPing' in wsHandle) {
      wsHandle.sendPing()
    }
  }

  function disconnect() {
    if (reconnectTimer) {
      clearTimeout(reconnectTimer)
      reconnectTimer = null
    }
    if (wsHandle) {
      wsHandle.close()
      wsHandle = null
    }
    isConnected.value = false
    reconnectAttempts = 0
  }

  onUnmounted(disconnect)

  return {
    isConnected,
    lastMessage,
    connect,
    send,
    disconnect,
  }
}
