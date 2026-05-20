import { ref, watch } from 'vue'
import { useMeetingStore } from '@/stores/meeting'
import type { TranscriptChunkRead } from '@/types'

export function useTranscriptHighlight() {
  const meetingStore = useMeetingStore()

  const activeChunkId = ref<string | null>(null)

  function findChunkByTime(time: number, chunks: TranscriptChunkRead[]): TranscriptChunkRead | null {
    for (const chunk of chunks) {
      if (time >= chunk.start && time <= chunk.end) {
        return chunk
      }
    }
    return null
  }

  function highlightChunk(chunkId: string) {
    activeChunkId.value = chunkId

    const el = document.getElementById(`chunk-${chunkId}`)
    if (el) {
      el.scrollIntoView({ behavior: 'smooth', block: 'center' })
    }
  }

  function syncWithAudio(time: number) {
    const chunk = findChunkByTime(time, meetingStore.transcripts)
    if (chunk && chunk.id !== activeChunkId.value) {
      activeChunkId.value = chunk.id
    }
  }

  watch(
    () => meetingStore.currentTime,
    (time) => {
      syncWithAudio(time)
    },
  )

  return {
    activeChunkId,
    highlightChunk,
    syncWithAudio,
  }
}
