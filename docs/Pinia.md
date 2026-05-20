# MeetingPilot 前端架构文档：状态与逻辑管理

## 1. 核心理念：逻辑三层拆分

为了提高代码的**鲁棒性** 和可维护性，我们将逻辑分为三层：

1. **Pinia Stores**：全局“单线联系人”，负责持有跨页面共享的数据（如：当前选中的会议、用户信息）。
2. **Composables (组合式函数)**：逻辑“工具箱”，负责封装可复用的复杂交互（如：音频播放控制、定时任务轮询）。
3. **UI Components**：视觉“呈现者”，只通过调用 Store 和 Composables 来获取数据或触发动作。

---

## 2. 状态设计：Pinia Store 实战

以会议详情为例，我们需要在多个组件（波形图、转录列表、AI总结）间共享“当前会议”和“当前播放时间”。

### 2.1 定义 Meeting Store (`src/stores/meeting.ts`)

```typescript
import { defineStore } from 'pinia'
import type { Meeting, TranscriptChunk } from '@/types/meeting'
import { getMeeting, getTranscripts } from '@/api/meetings'

export const useMeetingStore = defineStore('meeting', () => {
  // --- 状态 (State) ---
  const currentMeeting = ref<Meeting | null>(null)
  const transcripts = ref<TranscriptChunk[]>([])
  const currentTime = ref(0) // 全局同步的音频播放进度
  const isLoading = ref(false)

  // --- 异步流处理 (Actions) ---
  async function loadMeetingData(id: string) {
    isLoading.value = true
    try {
      // 并发请求会议详情和转录内容
      const [meetingRes, transcriptRes] = await Promise.all([
        getMeeting(id),
        getTranscripts(id)
      ])
      currentMeeting.value = meetingRes.data
      transcripts.value = transcriptRes.data
    } finally {
      isLoading.value = false
    }
  }

  function updateCurrentTime(time: number) {
    currentTime.value = time
  }

  return {
    currentMeeting,
    transcripts,
    currentTime,
    isLoading,
    loadMeetingData,
    updateCurrentTime
  }
})

```

---

## 3. 逻辑复用：Composables 实战

复杂的第三方库初始化（如 WaveSurfer.js）或长周期逻辑（轮询）如果不抽离，会使 `.vue` 文件变得臃肿。

### 3.1 音频控制逻辑 (`src/composables/useAudioPlayer.ts`)

```typescript
import WaveSurfer from 'wavesurfer.js'
import { useMeetingStore } from '@/stores/meeting'

export function useAudioPlayer() {
  const meetingStore = useMeetingStore()
  let ws: WaveSurfer | null = null

  // 初始化波形图
  const initPlayer = (container: HTMLElement, audioUrl: string) => {
    ws = WaveSurfer.create({
      container,
      waveColor: '#D1C4E9', // 淡淡的粉紫色
      progressColor: '#7E57C2',
      url: audioUrl,
    })

    // 核心：将播放器的进度同步到 Pinia 状态
    ws.on('timeupdate', (time) => {
      meetingStore.updateCurrentTime(time)
    })
  }

  const playPause = () => ws?.playPause()
  
  const seekTo = (time: number) => {
    if (ws) {
      const duration = ws.getDuration()
      ws.seekTo(time / duration)
    }
  }

  return { initPlayer, playPause, seekTo }
}

```

### 3.2 任务状态轮询 (`src/composables/useTaskPolling.ts`)

当会议正在“转录中”或“分析中”时，前端需要定时检查进度。

```typescript
export function useTaskPolling() {
  const timer = ref<number | null>(null)

  const startPolling = (callback: () => Promise<boolean>, interval = 3000) => {
    stopPolling()
    timer.value = window.setInterval(async () => {
      const isFinished = await callback() // 回调函数返回 true 则停止
      if (isFinished) stopPolling()
    }, interval)
  }

  const stopPolling = () => {
    if (timer.value) {
      clearInterval(timer.value)
      timer.value = null
    }
  }

  // 组件卸载时自动停止轮询，防止内存泄漏（鲁棒性体现）
  onUnmounted(stopPolling)

  return { startPolling, stopPolling }
}

```

---

## 4. 在组件中消费 (The "Clean" UI)

现在，你的 UI 组件（如 `MeetingDetail.vue`）会变得非常干净：

```vue
<script setup lang="ts">
import { useMeetingStore } from '@/stores/meeting'
import { useAudioPlayer } from '@/composables/useAudioPlayer'

const route = useRoute()
const store = useMeetingStore()
const { initPlayer, playPause } = useAudioPlayer()
const waveformRef = ref<HTMLElement>()

// 1. 进入页面加载数据
onMounted(async () => {
  await store.loadMeetingData(route.params.id as string)
  
  // 2. 数据加载后初始化播放器
  if (store.currentMeeting?.audio_url && waveformRef.value) {
    initPlayer(waveformRef.value, store.currentMeeting.audio_url)
  }
})
</script>

<template>
  <div class="meeting-detail p-4">
    <h1 class="text-xl font-bold">{{ store.currentMeeting?.title }}</h1>
    
    <div ref="waveformRef" class="my-4"></div>
    
    <el-button @click="playPause">播放 / 暂停</el-button>
    
    <TranscriptList :data="store.transcripts" :current-time="store.currentTime" />
  </div>
</template>

```

---

## 5. 总结：这套方案好在哪里？

1. **数据单向流动**：所有组件共享同一个 `currentTime`，当你点击“转录文字”跳转时间时，波形图会自动跟着跳，无需组件间手动传递事件。
2. **易于测试**：你可以单独测试 `useTaskPolling` 逻辑，甚至不需要启动浏览器。
3. **专注 UI**：作为全栈开发者，你可以快速更换 UI 框架（比如从 Element Plus 换成更“可爱”的自定义组件），而核心的业务逻辑（Store 和 Composables）一行代码都不用改。

