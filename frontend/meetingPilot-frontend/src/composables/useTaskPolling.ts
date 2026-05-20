import { ref, onUnmounted } from 'vue'

export function useTaskPolling() {
  const isPolling = ref(false)
  let timer: ReturnType<typeof setInterval> | null = null

  function startPolling(callback: () => Promise<boolean>, interval = 3000) {
    stopPolling()
    isPolling.value = true

    timer = window.setInterval(async () => {
      const isFinished = await callback()
      if (isFinished) stopPolling()
    }, interval)
  }

  function stopPolling() {
    if (timer) {
      clearInterval(timer)
      timer = null
    }
    isPolling.value = false
  }

  onUnmounted(stopPolling)

  return {
    isPolling,
    startPolling,
    stopPolling,
  }
}
