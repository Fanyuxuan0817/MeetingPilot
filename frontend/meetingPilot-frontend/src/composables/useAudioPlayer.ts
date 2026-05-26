import { ref, onUnmounted, provide, inject, type InjectionKey } from 'vue'
import WaveSurfer from 'wavesurfer.js'
import { useMeetingStore } from '@/stores/meeting'

export interface AudioPlayerState {
  currentTime: ReturnType<typeof ref<number>>
  duration: ReturnType<typeof ref<number>>
  isPlaying: ReturnType<typeof ref<boolean>>
  isReady: ReturnType<typeof ref<boolean>>
  loadError: ReturnType<typeof ref<string | null>>
  initPlayer: (container: HTMLElement, audioUrl: string) => void
  playPause: () => void
  seekTo: (time: number) => void
  destroy: () => void
}

const AudioPlayerKey: InjectionKey<AudioPlayerState> = Symbol('audioPlayer')

export function provideAudioPlayer(): AudioPlayerState {
  const meetingStore = useMeetingStore()

  let ws: WaveSurfer | null = null

  const currentTime = ref(0)
  const duration = ref(0)
  const isPlaying = ref(false)
  const isReady = ref(false)
  const loadError = ref<string | null>(null)

  function initPlayer(container: HTMLElement, audioUrl: string) {
    destroy()

    ws = WaveSurfer.create({
      container,
      waveColor: '#a8a29e',
      progressColor: '#d97706',
      height: 60,
      cursorColor: '#92400e',
      url: audioUrl,
    })

    meetingStore.setWaveSurfer(ws)

    ws.on('timeupdate', (time) => {
      currentTime.value = time
      meetingStore.updateCurrentTime(time)
    })

    ws.on('ready', () => {
      isReady.value = true
      loadError.value = null
      duration.value = ws!.getDuration()
    })

    ws.on('play', () => {
      isPlaying.value = true
      meetingStore.setPlaying(true)
    })

    ws.on('pause', () => {
      isPlaying.value = false
      meetingStore.setPlaying(false)
    })

    ws.on('error', (err) => {
      loadError.value = typeof err === 'string' ? err : (err as Error).message || '音频加载失败'
      isReady.value = false
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
    meetingStore.setWaveSurfer(null)
    currentTime.value = 0
    duration.value = 0
    isPlaying.value = false
    isReady.value = false
    loadError.value = null
    meetingStore.setPlaying(false)
    meetingStore.updateCurrentTime(0)
  }

  onUnmounted(destroy)

  const state: AudioPlayerState = {
    currentTime,
    duration,
    isPlaying,
    isReady,
    loadError,
    initPlayer,
    playPause,
    seekTo,
    destroy,
  }

  provide(AudioPlayerKey, state)
  return state
}

export function useAudioPlayer(): AudioPlayerState {
  const state = inject(AudioPlayerKey)
  if (!state) {
    throw new Error('useAudioPlayer must be called inside a component that called provideAudioPlayer')
  }
  return state
}
