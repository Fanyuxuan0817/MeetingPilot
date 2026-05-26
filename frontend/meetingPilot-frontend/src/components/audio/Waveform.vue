<template>
  <div class="waveform-container bg-soft-cream p-4 rounded-xl shadow-soft">
    <div v-if="!isReady" v-loading="true" class="h-[60px]"></div>
    <div v-show="isReady" ref="waveformRef"></div>

    <div class="controls flex items-center justify-center gap-3 mt-3">
      <button
        @click="playPause"
        :disabled="!isReady"
        class="w-12 h-12 rounded-full bg-primary-400 hover:bg-primary-500 disabled:bg-primary-200 text-white shadow-soft transition-all duration-200 flex items-center justify-center active:scale-95"
      >
        <el-icon :size="22">
          <VideoPause v-if="isPlaying" />
          <VideoPlay v-else />
        </el-icon>
      </button>
      <span v-if="isReady" class="text-sm text-brown-500 tabular-nums">
        {{ formatTime(currentTime) }} / {{ formatTime(duration) }}
      </span>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch } from 'vue'
import { VideoPlay, VideoPause } from '@element-plus/icons-vue'
import { useAudioPlayer } from '@/composables/useAudioPlayer'

const props = defineProps<{ url: string }>()

const waveformRef = ref<HTMLElement | null>(null)
const { currentTime, duration, isPlaying, isReady, initPlayer, playPause, destroy } = useAudioPlayer()

onMounted(() => {
  if (waveformRef.value) {
    initPlayer(waveformRef.value, props.url)
  }
})

watch(
  () => props.url,
  (newUrl) => {
    if (waveformRef.value) {
      initPlayer(waveformRef.value, newUrl)
    }
  },
)

function formatTime(seconds: number | undefined): string {
  if (seconds === undefined) return '0:00'
  const m = Math.floor(seconds / 60)
  const s = Math.floor(seconds % 60)
  return `${m}:${s.toString().padStart(2, '0')}`
}
</script>
