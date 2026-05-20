import { ref, onUnmounted } from 'vue'
import WaveSurfer from 'wavesurfer.js'
import { useMeetingStore } from '@/stores/meeting'

export function useAudioPlayer() {
  const meetingStore = useMeetingStore()

  let ws: WaveSurfer | null = null

  const currentTime = ref(0)
  const duration = ref(0)
  const isPlaying = ref(false)

  function initPlayer(container: HTMLElement, audioUrl: string) {
    destroy()

    ws = WaveSurfer.create({
      container,
      waveColor: '#D1C4E9',
      progressColor: '#7E57C2',
      url: audioUrl,
    })

    ws.on('timeupdate', (time) => {
      currentTime.value = time
      meetingStore.updateCurrentTime(time)
    })

    ws.on('ready', () => {
      duration.value = ws!.getDuration()
    })

    ws.on('play', () => {
      isPlaying.value = true
    })

    ws.on('pause', () => {
      isPlaying.value = false
    })
  }

  function playPause() {
    ws?.playPause()
  }

  function seekTo(time: number) {
    if (ws) {
      const d = ws.getDuration()
      if (d > 0) ws.seekTo(time / d)
    }
  }

  function destroy() {
    if (ws) {
      ws.destroy()
      ws = null
    }
    currentTime.value = 0
    duration.value = 0
    isPlaying.value = false
  }

  onUnmounted(destroy)

  return {
    currentTime,
    duration,
    isPlaying,
    initPlayer,
    playPause,
    seekTo,
    destroy,
  }
}
