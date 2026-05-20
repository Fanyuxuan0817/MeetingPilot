<template>
  <div class="waveform-container bg-soft-cream p-4 rounded-xl shadow-soft">
    <div v-if="!isReady && !loadError" v-loading="true" class="h-[60px]"></div>
    <div v-else-if="loadError" class="h-[60px] flex items-center justify-center text-secondary-700 text-sm">
      <el-icon class="mr-1"><WarningFilled /></el-icon>
      {{ loadError }}
    </div>
    <div v-show="isReady && !loadError" ref="waveformRef"></div>

    <div class="controls flex items-center justify-center gap-3 mt-3">
      <el-button @click="playPause" circle size="large" :disabled="!isReady">
        <el-icon :size="20">
          <VideoPause v-if="store.isPlaying" />
          <VideoPlay v-else />
        </el-icon>
      </el-button>
      <span v-if="isReady" class="text-sm text-brown-500 tabular-nums">
        {{ formatTime(store.currentTime) }} / {{ formatTime(duration) }}
      </span>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, watch } from 'vue'
import { VideoPlay, VideoPause, WarningFilled } from '@element-plus/icons-vue'
import { useWaveSurfer } from '@/composables/useWaveSurfer'
import { useMeetingStore } from '@/stores/meeting'

const props = defineProps<{ url: string }>()

const store = useMeetingStore()
const waveformRef = ref<HTMLElement | null>(null)
const { isReady, duration, loadError, initWaveform, playPause, destroy } = useWaveSurfer()

onMounted(() => {
  if (waveformRef.value) {
    initWaveform(waveformRef.value, props.url)
  }
})

watch(
  () => props.url,
  (newUrl) => {
    if (waveformRef.value) {
      initWaveform(waveformRef.value, newUrl)
    }
  },
)

onUnmounted(() => {
  destroy()
})

function formatTime(seconds: number): string {
  const m = Math.floor(seconds / 60)
  const s = Math.floor(seconds % 60)
  return `${m}:${s.toString().padStart(2, '0')}`
}
</script>
