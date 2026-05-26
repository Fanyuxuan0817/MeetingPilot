<template>
  <div class="meeting-detail h-screen flex flex-col bg-soft-cream">
    <!-- 顶部导航栏 -->
    <header class="bg-white border-b border-primary-100 px-6 py-3 flex items-center justify-between shrink-0">
      <div class="flex items-center gap-3">
        <el-button text circle @click="$router.push('/')">
          <el-icon><ArrowLeft /></el-icon>
        </el-button>
        <div>
          <h1 class="text-base font-semibold text-brown-800">
            {{ meetingStore.currentMeeting?.title || '加载中...' }}
          </h1>
          <p class="text-xs text-brown-400">
            {{ meetingStore.currentMeeting ? formatDate(meetingStore.currentMeeting.created_at) : '' }}
            <el-tag v-if="meetingStore.currentMeeting" :type="statusTagType(meetingStore.currentMeeting.status)" size="small" round class="ml-2">
              {{ statusLabel(meetingStore.currentMeeting.status) }}
            </el-tag>
          </p>
        </div>
      </div>
      <div class="flex items-center gap-2">
        <button
          class="px-4 py-1.5 rounded-full bg-primary-400 hover:bg-primary-500 text-white text-sm font-medium shadow-soft transition-all duration-200 flex items-center gap-1.5 active:scale-95"
          @click="handleRunAgents"
        >
          <el-icon :size="14"><MagicStick /></el-icon>运行 Agent
        </button>
      </div>
    </header>

    <!-- 音频播放器 -->
    <div class="shrink-0 px-6 py-3 bg-white/50 backdrop-blur-sm">
      <Waveform v-if="audioUrl" :url="audioUrl" />
      <div v-else class="h-[108px] flex items-center justify-center text-secondary-700 text-sm bg-soft-cream rounded-xl">
        <el-icon class="mr-1"><Headset /></el-icon>
        暂无音频文件
      </div>
    </div>

    <!-- 主内容区：双栏布局 -->
    <div class="flex-1 flex overflow-hidden">
      <!-- 左侧：转录文本 -->
      <div class="w-[55%] flex flex-col border-r border-primary-100">
        <div class="px-4 py-2 bg-white/60 border-b border-primary-100 flex items-center justify-between shrink-0">
          <h2 class="text-sm font-semibold text-brown-700 flex items-center gap-1.5">
            <el-icon :size="16" class="text-primary-500"><Document /></el-icon>
            转录文本
          </h2>
          <span class="text-xs text-brown-400">{{ meetingStore.transcripts.length }} 条片段</span>
        </div>
        <div class="flex-1 overflow-y-auto p-4">
          <TranscriptList />
        </div>
      </div>

      <!-- 右侧：AI 分析面板 -->
      <div class="w-[45%] flex flex-col bg-white/40">
        <el-tabs v-model="activeTab" class="flex-1 flex flex-col">
          <el-tab-pane label="智能纪要" name="summary" class="h-full">
            <div class="h-full p-4">
              <SummaryPanel :meeting-id="meetingId" />
            </div>
          </el-tab-pane>
          <el-tab-pane label="待办追踪" name="actions" class="h-full">
            <div class="h-full p-4">
              <ActionPanel :meeting-id="meetingId" />
            </div>
          </el-tab-pane>
          <el-tab-pane label="智能问答" name="chat" class="h-full">
            <div class="h-full p-4">
              <AgentChat :meeting-id="meetingId" />
            </div>
          </el-tab-pane>
        </el-tabs>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, onMounted, onUnmounted } from 'vue'
import { useRoute } from 'vue-router'
import { ArrowLeft, MagicStick, Document, Headset } from '@element-plus/icons-vue'
import { useMeetingStore } from '@/stores/meeting'
import { useAgentStore } from '@/stores/agent'
import { provideAudioPlayer } from '@/composables/useAudioPlayer'
import { MeetingStatus } from '@/types'
import Waveform from '@/components/audio/Waveform.vue'
import TranscriptList from '@/components/transcript/TranscriptList.vue'
import SummaryPanel from '@/components/summary/SummaryPanel.vue'
import ActionPanel from '@/components/meeting/ActionPanel.vue'
import AgentChat from '@/components/qa/AgentChat.vue'

const route = useRoute()
const meetingStore = useMeetingStore()
const agentStore = useAgentStore()
const { destroy } = provideAudioPlayer()

const meetingId = computed(() => route.params.id as string)
const activeTab = ref('summary')

const audioUrl = computed(() => {
  const url = meetingStore.currentMeeting?.audio_url
  return url || ''
})

onMounted(() => {
  loadMeeting()
})

onUnmounted(() => {
  destroy()
  agentStore.resetForNewMeeting()
})

watch(meetingId, () => {
  loadMeeting()
})

async function loadMeeting() {
  if (!meetingId.value) return
  destroy()
  agentStore.resetForNewMeeting()
  try {
    await meetingStore.loadMeetingData(meetingId.value)
    await Promise.all([
      agentStore.loadSummary(meetingId.value).catch(() => {}),
      agentStore.loadActions(meetingId.value).catch(() => {}),
    ])
  } catch (err) {
    console.error('Failed to load meeting:', err)
  }
}

async function handleRunAgents() {
  try {
    await meetingStore.triggerAgents(meetingId.value)
  } catch (err) {
    console.error('Failed to run agents:', err)
  }
}

function statusTagType(status: MeetingStatus) {
  switch (status) {
    case MeetingStatus.COMPLETED: return 'success'
    case MeetingStatus.ANALYZING: return 'warning'
    case MeetingStatus.TRANSCRIBING: return 'info'
    case MeetingStatus.FAILED: return 'danger'
    default: return 'info'
  }
}

function statusLabel(status: MeetingStatus) {
  switch (status) {
    case MeetingStatus.CREATED: return '已创建'
    case MeetingStatus.UPLOADING: return '上传中'
    case MeetingStatus.TRANSCRIBING: return '转录中'
    case MeetingStatus.ANALYZING: return '分析中'
    case MeetingStatus.COMPLETED: return '已完成'
    case MeetingStatus.FAILED: return '失败'
    default: return status
  }
}

function formatDate(dateStr: string): string {
  const d = new Date(dateStr)
  return `${d.getFullYear()}/${d.getMonth() + 1}/${d.getDate()} ${d.getHours()}:${d.getMinutes().toString().padStart(2, '0')}`
}
</script>

<style scoped>
.meeting-detail :deep(.el-tabs) {
  display: flex;
  flex-direction: column;
}
.meeting-detail :deep(.el-tabs__content) {
  flex: 1;
  overflow: hidden;
}
.meeting-detail :deep(.el-tab-pane) {
  height: 100%;
}
</style>
