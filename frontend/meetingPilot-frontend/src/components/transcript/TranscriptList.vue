<template>
  <div class="transcript-list">
    <div v-if="store.transcripts.length === 0" class="empty-hint text-center py-12 text-brown-400">
      暂无转录内容
    </div>
    <div v-else class="transcript-items space-y-1 overflow-y-auto max-h-[480px] pr-1">
      <div
        v-for="chunk in store.transcripts"
        :id="`chunk-${chunk.id}`"
        :key="chunk.id"
        class="chunk-item px-3 py-2 rounded-lg cursor-pointer transition-colors duration-200"
        :class="activeChunkId === chunk.id
          ? 'bg-secondary-100 border-l-3 border-secondary-500'
          : 'hover:bg-soft-cream'"
        @click="handleClick(chunk)"
      >
        <div class="flex items-baseline gap-2">
          <span class="speaker text-xs font-semibold text-secondary-600 shrink-0">
            {{ chunk.speaker }}
          </span>
          <span class="timestamp text-[11px] text-brown-400 tabular-nums shrink-0">
            {{ formatTime(chunk.start) }}
          </span>
        </div>
        <p class="content text-sm text-brown-700 mt-0.5 leading-relaxed">
          {{ chunk.content }}
        </p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useMeetingStore } from '@/stores/meeting'
import { useTranscriptHighlight } from '@/composables/useTranscriptHighlight'
import { useAudioPlayer } from '@/composables/useAudioPlayer'
import type { TranscriptChunkRead } from '@/types'

const store = useMeetingStore()
const { activeChunkId, highlightChunk } = useTranscriptHighlight()
const { seekTo } = useAudioPlayer()

function handleClick(chunk: TranscriptChunkRead) {
  highlightChunk(chunk.id)
  seekTo(chunk.start)
}

function formatTime(seconds: number): string {
  const m = Math.floor(seconds / 60)
  const s = Math.floor(seconds % 60)
  return `${m}:${s.toString().padStart(2, '0')}`
}
</script>
