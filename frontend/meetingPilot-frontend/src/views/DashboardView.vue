<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import {
  Search,
  Plus,
  Calendar,
  Clock,
  Document,
  Microphone,
  Check,
  Warning,
  Loading,
  Close,
  ArrowRight,
  PriceTag,
} from '@element-plus/icons-vue'
import { useMeetingStore } from '@/stores/meeting'
import { MeetingStatus } from '@/types'
import type { MeetingRead } from '@/types'

const router = useRouter()
const meetingStore = useMeetingStore()

const searchKeyword = ref('')
const statusFilter = ref<MeetingStatus | ''>('')

const filteredMeetings = computed(() => {
  let list = meetingStore.meetings
  if (searchKeyword.value.trim()) {
    const kw = searchKeyword.value.trim().toLowerCase()
    list = list.filter(
      (m) =>
        m.title.toLowerCase().includes(kw) ||
        (m.description ?? '').toLowerCase().includes(kw) ||
        m.tags.some((t) => t.toLowerCase().includes(kw)),
    )
  }
  if (statusFilter.value) {
    list = list.filter((m) => m.status === statusFilter.value)
  }
  return list
})

function goToDetail(meetingId: string) {
  router.push({ name: 'meeting-detail', params: { id: meetingId } })
}

function formatDate(dateStr: string): string {
  const d = new Date(dateStr)
  return `${d.getFullYear()}/${d.getMonth() + 1}/${d.getDate()}`
}

function formatDuration(seconds: number | null): string {
  if (!seconds) return '--:--'
  const m = Math.floor(seconds / 60)
  const s = Math.floor(seconds % 60)
  return `${m}:${s.toString().padStart(2, '0')}`
}

function statusConfig(status: MeetingStatus) {
  switch (status) {
    case MeetingStatus.CREATED:
      return { label: '已创建', type: 'info' as const, icon: Document }
    case MeetingStatus.UPLOADING:
      return { label: '上传中', type: 'warning' as const, icon: Loading }
    case MeetingStatus.TRANSCRIBING:
      return { label: '转录中', type: 'warning' as const, icon: Microphone }
    case MeetingStatus.ANALYZING:
      return { label: '分析中', type: 'warning' as const, icon: Loading }
    case MeetingStatus.COMPLETED:
      return { label: '已完成', type: 'success' as const, icon: Check }
    case MeetingStatus.FAILED:
      return { label: '失败', type: 'danger' as const, icon: Close }
    default:
      return { label: status, type: 'info' as const, icon: Document }
  }
}

function statusBgClass(status: MeetingStatus) {
  switch (status) {
    case MeetingStatus.COMPLETED:
      return 'bg-green-50 border-green-200'
    case MeetingStatus.ANALYZING:
    case MeetingStatus.TRANSCRIBING:
    case MeetingStatus.UPLOADING:
      return 'bg-amber-50 border-amber-200'
    case MeetingStatus.FAILED:
      return 'bg-red-50 border-red-200'
    default:
      return 'bg-white border-primary-100'
  }
}

const statusOptions = [
  { value: '', label: '全部状态' },
  { value: MeetingStatus.CREATED, label: '已创建' },
  { value: MeetingStatus.UPLOADING, label: '上传中' },
  { value: MeetingStatus.TRANSCRIBING, label: '转录中' },
  { value: MeetingStatus.ANALYZING, label: '分析中' },
  { value: MeetingStatus.COMPLETED, label: '已完成' },
  { value: MeetingStatus.FAILED, label: '失败' },
]

onMounted(() => {
  loadMeetings()
})

async function loadMeetings() {
  try {
    await meetingStore.loadMeetings()
  } catch (err) {
    console.error('Failed to load meetings:', err)
  }
}

function handleCreateMeeting() {
  router.push({ name: 'upload' })
}
</script>

<template>
  <div class="min-h-screen bg-soft-cream">
    <!-- 顶部导航栏 -->
    <header class="bg-white/80 backdrop-blur-md border-b border-primary-100 sticky top-0 z-10">
      <div class="max-w-6xl mx-auto px-6 py-4 flex items-center justify-between">
        <div class="flex items-center gap-3">
          <div
            class="w-10 h-10 rounded-2xl bg-primary-400 flex items-center justify-center shadow-soft"
          >
            <el-icon :size="20" color="#fff"><Microphone /></el-icon>
          </div>
          <div>
            <h1 class="text-xl font-bold text-brown-800 tracking-tight">MeetingPilot</h1>
            <p class="text-xs text-brown-400">智能会议助手</p>
          </div>
        </div>

        <button
          class="px-5 py-2.5 rounded-full bg-primary-400 hover:bg-primary-500 text-white text-sm font-semibold shadow-soft transition-all duration-200 flex items-center gap-2 active:scale-95"
          @click="handleCreateMeeting"
        >
          <el-icon :size="16"><Plus /></el-icon>
          新建会议
        </button>
      </div>
    </header>

    <!-- 主内容区 -->
    <main class="max-w-6xl mx-auto px-6 py-8">
      <!-- 搜索与筛选 -->
      <div class="flex flex-col sm:flex-row gap-3 mb-8">
        <div class="flex-1 relative">
          <el-input
            v-model="searchKeyword"
            placeholder="搜索会议标题、描述或标签..."
            size="large"
            clearable
            class="search-input"
          >
            <template #prefix>
              <el-icon class="text-brown-400"><Search /></el-icon>
            </template>
          </el-input>
        </div>
        <el-select
          v-model="statusFilter"
          placeholder="筛选状态"
          size="large"
          clearable
          class="w-40 status-select"
        >
          <el-option
            v-for="opt in statusOptions"
            :key="opt.value"
            :label="opt.label"
            :value="opt.value"
          />
        </el-select>
      </div>

      <!-- 统计卡片 -->
      <div class="grid grid-cols-2 sm:grid-cols-4 gap-4 mb-8">
        <div
          class="bg-white rounded-2xl p-4 border border-primary-100 shadow-soft hover:shadow-soft-lg transition-shadow duration-300"
        >
          <div class="text-2xl font-bold text-primary-600">{{ meetingStore.meetings.length }}</div>
          <div class="text-sm text-brown-500 mt-1">全部会议</div>
        </div>
        <div
          class="bg-white rounded-2xl p-4 border border-primary-100 shadow-soft hover:shadow-soft-lg transition-shadow duration-300"
        >
          <div class="text-2xl font-bold text-green-500">
            {{ meetingStore.meetings.filter((m) => m.status === MeetingStatus.COMPLETED).length }}
          </div>
          <div class="text-sm text-brown-500 mt-1">已完成</div>
        </div>
        <div
          class="bg-white rounded-2xl p-4 border border-primary-100 shadow-soft hover:shadow-soft-lg transition-shadow duration-300"
        >
          <div class="text-2xl font-bold text-amber-500">
            {{ meetingStore.meetings.filter((m) => m.status === MeetingStatus.TRANSCRIBING || m.status === MeetingStatus.ANALYZING).length }}
          </div>
          <div class="text-sm text-brown-500 mt-1">处理中</div>
        </div>
        <div
          class="bg-white rounded-2xl p-4 border border-primary-100 shadow-soft hover:shadow-soft-lg transition-shadow duration-300"
        >
          <div class="text-2xl font-bold text-primary-400">
            {{ meetingStore.meetings.filter((m) => m.tags.length > 0).length }}
          </div>
          <div class="text-sm text-brown-500 mt-1">已打标签</div>
        </div>
      </div>

      <!-- 会议列表 -->
      <div v-if="meetingStore.isLoading" class="space-y-4">
        <el-skeleton v-for="i in 4" :key="i" animated>
          <template #template>
            <div class="flex items-center gap-4 p-4">
              <el-skeleton-item variant="circle" style="width: 48px; height: 48px" />
              <div class="flex-1">
                <el-skeleton-item variant="text" style="width: 30%; margin-bottom: 8px" />
                <el-skeleton-item variant="text" style="width: 60%" />
              </div>
            </div>
          </template>
        </el-skeleton>
      </div>

      <div v-else-if="filteredMeetings.length === 0" class="text-center py-20">
        <div
          class="w-20 h-20 rounded-full bg-primary-100 flex items-center justify-center mx-auto mb-4"
        >
          <el-icon :size="32" class="text-primary-400"><Document /></el-icon>
        </div>
        <h3 class="text-lg font-semibold text-brown-700 mb-1">暂无会议记录</h3>
        <p class="text-sm text-brown-400">点击右上角「新建会议」开始你的第一次记录吧</p>
      </div>

      <div v-else class="space-y-4">
        <div
          v-for="meeting in filteredMeetings"
          :key="meeting.id"
          :class="[
            'group rounded-2xl border p-5 cursor-pointer transition-all duration-300 hover:shadow-soft-lg hover:-translate-y-0.5',
            statusBgClass(meeting.status),
          ]"
          @click="goToDetail(meeting.id)"
        >
          <div class="flex items-start justify-between gap-4">
            <div class="flex-1 min-w-0">
              <div class="flex items-center gap-2 mb-2">
                <h3 class="text-base font-semibold text-brown-800 truncate">
                  {{ meeting.title }}
                </h3>
                <el-tag
                  :type="statusConfig(meeting.status).type"
                  size="small"
                  round
                  class="shrink-0"
                >
                  <el-icon :size="12" class="mr-0.5">
                    <component :is="statusConfig(meeting.status).icon" />
                  </el-icon>
                  {{ statusConfig(meeting.status).label }}
                </el-tag>
              </div>

              <p
                v-if="meeting.description"
                class="text-sm text-brown-500 mb-3 line-clamp-1"
              >
                {{ meeting.description }}
              </p>

              <div class="flex flex-wrap items-center gap-3 text-xs text-brown-400">
                <span class="flex items-center gap-1">
                  <el-icon :size="12"><Calendar /></el-icon>
                  {{ formatDate(meeting.created_at) }}
                </span>
                <span class="flex items-center gap-1">
                  <el-icon :size="12"><Clock /></el-icon>
                  {{ formatDuration(meeting.duration) }}
                </span>
                <span
                  v-if="meeting.language"
                  class="px-2 py-0.5 rounded-full bg-primary-50 text-primary-600"
                >
                  {{ meeting.language }}
                </span>
              </div>

              <div v-if="meeting.tags.length" class="flex flex-wrap gap-1.5 mt-3">
                <span
                  v-for="tag in meeting.tags"
                  :key="tag"
                  class="inline-flex items-center gap-1 px-2.5 py-1 rounded-full bg-primary-100 text-primary-700 text-xs font-medium"
                >
                  <el-icon :size="10"><PriceTag /></el-icon>
                  {{ tag }}
                </span>
              </div>
            </div>

            <div
              class="shrink-0 w-10 h-10 rounded-xl bg-primary-50 flex items-center justify-center text-primary-400 group-hover:bg-primary-400 group-hover:text-white transition-all duration-300"
            >
              <el-icon :size="18"><ArrowRight /></el-icon>
            </div>
          </div>
        </div>
      </div>
    </main>
  </div>
</template>

<style scoped>
.search-input :deep(.el-input__wrapper) {
  border-radius: 1rem;
  box-shadow: 0 2px 12px rgba(234, 179, 8, 0.08);
  background-color: #fff;
  padding: 4px 16px;
}

.status-select :deep(.el-input__wrapper) {
  border-radius: 1rem;
  box-shadow: 0 2px 12px rgba(234, 179, 8, 0.08);
  background-color: #fff;
}

.line-clamp-1 {
  display: -webkit-box;
  -webkit-line-clamp: 1;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
</style>
