import { ref } from 'vue'
import WaveSurfer from 'wavesurfer.js'
import { useMeetingStore } from '@/stores/meeting'

let ws: WaveSurfer | null = null

const isReady = ref(false)
const duration = ref(0)
const loadError = ref<string | null>(null)

export function useWaveSurfer() {
  const store = useMeetingStore()

  function initWaveform(container: HTMLElement, url: string) {
    destroy()

    ws = WaveSurfer.create({
      container,
      waveColor: '#a8a29e',
      progressColor: '#d97706',
      height: 60,
      cursorColor: '#92400e',
      url,
    })

    ws.on('timeupdate', (time) => {
      store.updateCurrentTime(time)
    })

    ws.on('ready', () => {
      isReady.value = true
      loadError.value = null
      if (ws) {
        duration.value = ws.getDuration()
      }
    })

    ws.on('play', () => {
      store.setPlaying(true)
    })

    ws.on('pause', () => {
      store.setPlaying(false)
    })

    ws.on('error', (err) => {
      loadError.value = typeof err === 'string' ? err : (err as Error).message || '音频加载失败'
      isReady.value = false
    })
  }

  function seekTo(seconds: number) {
    if (!ws) return
    const d = ws.getDuration()
    if (d > 0) {
      ws.seekTo(seconds / d)
    }
  }

  function playPause() {
    ws?.playPause()
  }

  function play() {
    ws?.play()
  }

  function pause() {
    ws?.pause()
  }

  function destroy() {
    if (ws) {
      ws.destroy()
      ws = null
    }
    isReady.value = false
    duration.value = 0
    loadError.value = null
    store.setPlaying(false)
    store.updateCurrentTime(0)
  }

  return {
    isReady,
    duration,
    loadError,
    initWaveform,
    seekTo,
    playPause,
    play,
    pause,
    destroy,
  }
}
