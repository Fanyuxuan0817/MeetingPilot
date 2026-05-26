<template>
  <div class="agent-chat h-full flex flex-col">
    <div class="flex-1 overflow-y-auto pr-1 space-y-4 py-2">
      <div v-if="agentStore.chatMessages.length === 0" class="flex flex-col items-center justify-center h-full text-brown-400">
        <el-icon :size="48" class="mb-3 text-primary-200"><ChatDotRound /></el-icon>
        <p class="text-sm mb-1">智能问答助手</p>
        <p class="text-xs text-brown-300">输入问题，AI 将基于会议内容回答</p>
      </div>
      <ChatBubble
        v-for="msg in agentStore.chatMessages"
        :key="msg.id"
        :message="msg"
        @jump="handleJump"
      />
      <div v-if="agentStore.isStreaming" class="flex gap-3">
        <div class="w-8 h-8 rounded-full bg-primary-200 text-primary-700 flex items-center justify-center text-xs font-bold shrink-0">AI</div>
        <div class="bg-white rounded-2xl rounded-tl-sm px-4 py-2.5 shadow-soft border border-primary-100">
          <el-icon class="animate-pulse text-primary-400"><Loading /></el-icon>
        </div>
      </div>
    </div>

    <div class="mt-3 pt-3 border-t border-primary-100">
      <div class="flex gap-2">
        <el-input
          v-model="question"
          placeholder="输入问题..."
          round
          @keydown.enter.prevent="handleSend"
        />
        <button
          class="w-10 h-10 rounded-full bg-primary-400 hover:bg-primary-500 disabled:bg-primary-200 text-white shadow-soft transition-all duration-200 flex items-center justify-center shrink-0 active:scale-95"
          :disabled="!question.trim() || agentStore.isStreaming"
          @click="handleSend"
        >
          <el-icon :size="18"><Promotion /></el-icon>
        </button>
      </div>
      <div class="flex items-center gap-2 mt-2">
        <div class="inline-flex rounded-full bg-primary-50 p-0.5">
          <button
            class="px-3 py-1 rounded-full text-xs font-medium transition-all duration-200"
            :class="scope === 'current_meeting' ? 'bg-primary-400 text-white shadow-soft' : 'text-primary-600 hover:bg-primary-100'"
            @click="scope = 'current_meeting'"
          >
            当前会议
          </button>
          <button
            class="px-3 py-1 rounded-full text-xs font-medium transition-all duration-200"
            :class="scope === 'all_meetings' ? 'bg-primary-400 text-white shadow-soft' : 'text-primary-600 hover:bg-primary-100'"
            @click="scope = 'all_meetings'"
          >
            全部会议
          </button>
        </div>
        <button
          v-if="agentStore.chatMessages.length > 0"
          class="px-3 py-1 rounded-full text-xs text-brown-400 hover:text-brown-600 hover:bg-brown-100 transition-all duration-200 flex items-center gap-1"
          @click="handleClear"
        >
          <el-icon :size="12"><Delete /></el-icon>清空
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import { ChatDotRound, Loading, Promotion, Delete } from '@element-plus/icons-vue'
import { useAgentStore } from '@/stores/agent'
import { useWebSocket } from '@/composables/useWebSocket'
import { useAudioPlayer } from '@/composables/useAudioPlayer'
import ChatBubble from './ChatBubble.vue'
import type { ChatMessage } from '@/types'

const props = defineProps<{ meetingId: string }>()

const agentStore = useAgentStore()
const { connect, send, disconnect } = useWebSocket()
const { seekTo } = useAudioPlayer()

const question = ref('')
const scope = ref<'current_meeting' | 'all_meetings'>('current_meeting')

onMounted(() => {
  connect('chat')
})

onUnmounted(() => {
  disconnect()
})

function handleSend() {
  const q = question.value.trim()
  if (!q || agentStore.isStreaming) return

  const userMsg: ChatMessage = {
    id: `user-${Date.now()}`,
    role: 'user',
    content: q,
    timestamp: Date.now(),
  }
  agentStore.appendChatMessage(userMsg)

  const assistantMsg: ChatMessage = {
    id: `assistant-${Date.now()}`,
    role: 'assistant',
    content: '',
    timestamp: Date.now(),
  }
  agentStore.appendChatMessage(assistantMsg)
  agentStore.setStreaming(true)

  send({
    question: q,
    meeting_id: props.meetingId,
    scope: scope.value,
  })

  question.value = ''
}

function handleJump(time: number) {
  seekTo(time)
}

function handleClear() {
  agentStore.clearChat()
}
</script>
