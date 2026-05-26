<template>
  <div class="chat-bubble flex gap-3" :class="message.role === 'user' ? 'flex-row-reverse' : 'flex-row'">
    <div class="avatar shrink-0 w-8 h-8 rounded-full flex items-center justify-center text-xs font-bold"
      :class="message.role === 'user' ? 'bg-secondary-200 text-secondary-700' : 'bg-primary-200 text-primary-700'">
      {{ message.role === 'user' ? '我' : 'AI' }}
    </div>
    <div class="message-content max-w-[80%] rounded-2xl px-4 py-2.5 text-sm leading-relaxed"
      :class="message.role === 'user'
        ? 'bg-secondary-100 text-brown-700 rounded-tr-sm'
        : 'bg-white text-brown-700 shadow-soft rounded-tl-sm border border-primary-100'">
      <p class="whitespace-pre-wrap">{{ message.content }}</p>
      <div v-if="message.citations && message.citations.length > 0" class="mt-2 pt-2 border-t border-primary-100">
        <p class="text-xs text-brown-400 mb-1">引用来源</p>
        <div class="flex flex-wrap gap-1.5">
          <el-tag v-for="(c, idx) in message.citations" :key="idx" size="small" round type="info"
            class="cursor-pointer" @click="emit('jump', c.start)">
            {{ c.speaker }} {{ formatTime(c.start) }}
          </el-tag>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { ChatMessage } from '@/types'

const props = defineProps<{ message: ChatMessage }>()
const emit = defineEmits<{ jump: [time: number] }>()

function formatTime(seconds: number): string {
  const m = Math.floor(seconds / 60)
  const s = Math.floor(seconds % 60)
  return `${m}:${s.toString().padStart(2, '0')}`
}
</script>
