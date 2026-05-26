<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { ArrowLeft, Microphone } from '@element-plus/icons-vue'
import FileUploader from '@/components/upload/FileUploader.vue'
import ProcessingProgress from '@/components/upload/ProcessingProgress.vue'
import type { ProcessingPhase } from '@/components/upload/ProcessingProgress.vue'
import AgentFlowChart from '@/components/upload/AgentFlowChart.vue'
import type { AgentNodeKey } from '@/components/upload/AgentFlowChart.vue'
import { useMeetingUpload } from '@/composables/useMeetingUpload'
import { useMeetingStore } from '@/stores/meeting'
import type { MeetingJobItem } from '@/types'

const router = useRouter()
const meetingStore = useMeetingStore()
const { uploadProgress, isUploading, isPolling, upload, reset: resetUpload } = useMeetingUpload()

type PageStep = 'form' | 'processing' | 'done'

const currentStep = ref<PageStep>('form')
const selectedFile = ref<File | null>(null)
const meetingTitle = ref('')
const meetingDescription = ref('')
const language = ref('zh')
const enableDiarization = ref(true)
const currentMeetingId = ref<string | null>(null)
const processingPhase = ref<ProcessingPhase>('idle')
const activeAgent = ref<AgentNodeKey | null>(null)
const completedAgents = ref<AgentNodeKey[]>([])
const errorMessage = ref<string | null>(null)

const canSubmit = computed(() => {
  return selectedFile.value && meetingTitle.value.trim() && !isUploading.value && !isPolling.value
})

const uploaderRef = ref<InstanceType<typeof FileUploader> | null>(null)

function handleFileSelect(file: File) {
  selectedFile.value = file
  if (!meetingTitle.value.trim()) {
    const nameWithoutExt = file.name.replace(/\.[^/.]+$/, '')
    meetingTitle.value = nameWithoutExt
  }
}

function handleFileError(message: string) {
  ElMessage.error(message)
}

function goBack() {
  if (currentStep.value === 'processing') {
    return
  }
  router.push({ name: 'dashboard' })
}

async function handleSubmit() {
  if (!selectedFile.value || !meetingTitle.value.trim()) return

  currentStep.value = 'processing'
  processingPhase.value = 'uploading'
  errorMessage.value = null
  completedAgents.value = []
  activeAgent.value = null

  try {
    const job = await upload(selectedFile.value, {
      title: meetingTitle.value.trim(),
      description: meetingDescription.value.trim() || undefined,
      language: language.value || undefined,
      enable_speaker_diarization: enableDiarization.value,
    })

    currentMeetingId.value = job.meeting_id
    processingPhase.value = 'transcribing'
    activeAgent.value = 'transcriber'

    startJobPolling(job.meeting_id)
  } catch (err: unknown) {
    const msg = err instanceof Error ? err.message : '上传失败，请重试'
    errorMessage.value = msg
    processingPhase.value = 'failed'
    ElMessage.error(msg)
  }
}

function startJobPolling(meetingId: string) {
  const pollInterval = setInterval(async () => {
    try {
      const jobsRes = await meetingStore.fetchMeetingJobs(meetingId)
      const jobs = jobsRes.jobs

      const transcriberJob = jobs.find((j: MeetingJobItem) => j.type === 'transcription')
      const summaryJob = jobs.find((j: MeetingJobItem) => j.type === 'summary')
      const actionJob = jobs.find((j: MeetingJobItem) => j.type === 'action_extraction')
      const qaJob = jobs.find((j: MeetingJobItem) => j.type === 'qa_indexing')

      const allAgentJobs = [summaryJob, actionJob, qaJob].filter(Boolean) as MeetingJobItem[]
      const anyAgentDone = allAgentJobs.some((j: MeetingJobItem) => j.status === 'completed')

      if (transcriberJob) {
        if (transcriberJob.status === 'completed') {
          if (!completedAgents.value.includes('transcriber')) {
            completedAgents.value.push('transcriber')
          }
          processingPhase.value = 'analyzing'

          if (summaryJob?.status === 'running') {
            activeAgent.value = 'summarizer'
          } else if (actionJob?.status === 'running') {
            activeAgent.value = 'action_extractor'
          } else if (qaJob?.status === 'running') {
            activeAgent.value = 'qa_agent'
          } else if (anyAgentDone) {
            if (summaryJob?.status === 'completed' && !completedAgents.value.includes('summarizer')) {
              completedAgents.value.push('summarizer')
            }
            if (actionJob?.status === 'completed' && !completedAgents.value.includes('action_extractor')) {
              completedAgents.value.push('action_extractor')
            }
            if (qaJob?.status === 'completed' && !completedAgents.value.includes('qa_agent')) {
              completedAgents.value.push('qa_agent')
            }
          }
        } else if (transcriberJob.status === 'running') {
          activeAgent.value = 'transcriber'
          processingPhase.value = 'transcribing'
        } else if (transcriberJob.status === 'failed') {
          processingPhase.value = 'failed'
          errorMessage.value = '转录失败，请重试'
          clearInterval(pollInterval)
          return
        }
      }

      if (anyAgentDone) {
        if (summaryJob?.status === 'completed' && !completedAgents.value.includes('summarizer')) {
          completedAgents.value.push('summarizer')
        }
        if (actionJob?.status === 'completed' && !completedAgents.value.includes('action_extractor')) {
          completedAgents.value.push('action_extractor')
        }
        if (qaJob?.status === 'completed' && !completedAgents.value.includes('qa_agent')) {
          completedAgents.value.push('qa_agent')
        }
      }

      if (summaryJob?.status === 'running') activeAgent.value = 'summarizer'
      else if (actionJob?.status === 'running') activeAgent.value = 'action_extractor'
      else if (qaJob?.status === 'running') activeAgent.value = 'qa_agent'

      const allDone =
        (!transcriberJob || transcriberJob.status === 'completed') &&
        (!summaryJob || summaryJob.status === 'completed') &&
        (!actionJob || actionJob.status === 'completed') &&
        (!qaJob || qaJob.status === 'completed')
      const anyFailed =
        transcriberJob?.status === 'failed' ||
        summaryJob?.status === 'failed' ||
        actionJob?.status === 'failed' ||
        qaJob?.status === 'failed'

      if (anyFailed) {
        processingPhase.value = 'failed'
        errorMessage.value = '部分处理步骤失败'
        clearInterval(pollInterval)
        return
      }

      if (allDone) {
        processingPhase.value = 'completed'
        activeAgent.value = null
        completedAgents.value = ['transcriber', 'summarizer', 'action_extractor', 'qa_agent']
        clearInterval(pollInterval)
        await meetingStore.loadMeetings()
      }
    } catch {
      clearInterval(pollInterval)
      processingPhase.value = 'failed'
      errorMessage.value = '获取处理状态失败'
    }
  }, 3000)
}

function goToDetail() {
  if (currentMeetingId.value) {
    router.push({ name: 'meeting-detail', params: { id: currentMeetingId.value } })
  }
}

function goToDashboard() {
  router.push({ name: 'dashboard' })
}

function handleRetry() {
  currentStep.value = 'form'
  processingPhase.value = 'idle'
  errorMessage.value = null
  completedAgents.value = []
  activeAgent.value = null
  resetUpload()
  if (uploaderRef.value) {
    uploaderRef.value.clearFile()
  }
  selectedFile.value = null
  currentMeetingId.value = null
}

watch(processingPhase, (val) => {
  if (val === 'completed') {
    currentStep.value = 'done'
  }
})
</script>

<template>
  <div class="min-h-screen bg-soft-cream">
    <header class="bg-white/80 backdrop-blur-md border-b border-primary-100 sticky top-0 z-10">
      <div class="max-w-3xl mx-auto px-6 py-4 flex items-center gap-4">
        <button
          class="w-10 h-10 rounded-xl flex items-center justify-center text-brown-400 hover:bg-primary-50 hover:text-primary-500 transition-all duration-200"
          :class="{ 'pointer-events-none opacity-50': currentStep === 'processing' }"
          @click="goBack"
        >
          <el-icon :size="20"><ArrowLeft /></el-icon>
        </button>
        <div class="flex items-center gap-3">
          <div
            class="w-9 h-9 rounded-xl bg-primary-400 flex items-center justify-center shadow-soft"
          >
            <el-icon :size="18" color="#fff"><Microphone /></el-icon>
          </div>
          <div>
            <h1 class="text-lg font-bold text-brown-800">上传会议录音</h1>
            <p class="text-xs text-brown-400">上传音频文件，AI 将自动转录和分析</p>
          </div>
        </div>
      </div>
    </header>

    <main class="max-w-3xl mx-auto px-6 py-10">
      <transition name="fade-slide" mode="out-in">
        <div v-if="currentStep === 'form'" key="form" class="space-y-8">
          <FileUploader
            ref="uploaderRef"
            :disabled="isUploading"
            @select="handleFileSelect"
            @error="handleFileError"
          />

          <transition name="fade">
            <div v-if="selectedFile" class="space-y-5">
              <div class="bg-white rounded-2xl border border-primary-100 shadow-soft p-6 space-y-5">
                <div>
                  <label class="block text-sm font-semibold text-brown-700 mb-2">会议标题</label>
                  <el-input
                    v-model="meetingTitle"
                    placeholder="输入会议标题..."
                    size="large"
                    maxlength="100"
                    show-word-limit
                  />
                </div>

                <div>
                  <label class="block text-sm font-semibold text-brown-700 mb-2">会议描述</label>
                  <el-input
                    v-model="meetingDescription"
                    type="textarea"
                    placeholder="简要描述会议内容（可选）..."
                    :rows="3"
                    maxlength="500"
                    show-word-limit
                  />
                </div>

                <div class="grid grid-cols-2 gap-4">
                  <div>
                    <label class="block text-sm font-semibold text-brown-700 mb-2">音频语言</label>
                    <el-select v-model="language" size="large" class="w-full">
                      <el-option label="中文" value="zh" />
                      <el-option label="English" value="en" />
                      <el-option label="日本語" value="ja" />
                      <el-option label="自动检测" value="" />
                    </el-select>
                  </div>
                  <div>
                    <label class="block text-sm font-semibold text-brown-700 mb-2">说话人分离</label>
                    <div
                      class="flex items-center h-[40px] px-4 rounded-xl bg-soft-cream border border-primary-100"
                    >
                      <el-switch v-model="enableDiarization" />
                      <span class="ml-3 text-sm text-brown-500">
                        {{ enableDiarization ? '已开启' : '已关闭' }}
                      </span>
                    </div>
                  </div>
                </div>
              </div>

              <div class="flex justify-center">
                <button
                  :class="[
                    'px-8 py-3 rounded-full text-white text-base font-semibold shadow-soft transition-all duration-300 active:scale-95',
                    canSubmit
                      ? 'bg-primary-400 hover:bg-primary-500 hover:shadow-soft-lg'
                      : 'bg-brown-200 cursor-not-allowed',
                  ]"
                  :disabled="!canSubmit"
                  @click="handleSubmit"
                >
                  开始处理
                </button>
              </div>
            </div>
          </transition>
        </div>

        <div v-else-if="currentStep === 'processing'" key="processing" class="space-y-10">
          <div class="text-center mb-2">
            <h2 class="text-xl font-bold text-brown-800 mb-1">正在处理你的会议</h2>
            <p class="text-sm text-brown-400">AI 正在努力工作中，请耐心等待...</p>
          </div>

          <ProcessingProgress
            :phase="processingPhase"
            :progress="uploadProgress"
            :error-message="errorMessage"
          />

          <AgentFlowChart
            :active-agent="activeAgent"
            :completed-agents="completedAgents"
            :failed="processingPhase === 'failed'"
          />

          <div v-if="processingPhase === 'failed'" class="text-center">
            <button
              class="px-6 py-2.5 rounded-full bg-red-50 text-red-500 text-sm font-semibold hover:bg-red-100 transition-colors duration-200"
              @click="handleRetry"
            >
              重新上传
            </button>
          </div>
        </div>

        <div v-else-if="currentStep === 'done'" key="done" class="text-center space-y-6 py-10">
          <div class="w-24 h-24 rounded-full bg-green-100 flex items-center justify-center mx-auto animate-bounce-in">
            <svg width="40" height="40" viewBox="0 0 40 40" fill="none">
              <path
                d="M10 20L17 27L30 13"
                stroke="#4ade80"
                stroke-width="3"
                stroke-linecap="round"
                stroke-linejoin="round"
              />
            </svg>
          </div>
          <div>
            <h2 class="text-2xl font-bold text-brown-800 mb-2">处理完成！</h2>
            <p class="text-sm text-brown-400">你的会议已经成功转录和分析</p>
          </div>
          <div class="flex items-center justify-center gap-4">
            <button
              class="px-6 py-2.5 rounded-full bg-primary-400 hover:bg-primary-500 text-white text-sm font-semibold shadow-soft transition-all duration-200 active:scale-95"
              @click="goToDetail"
            >
              查看会议详情
            </button>
            <button
              class="px-6 py-2.5 rounded-full bg-white border border-primary-200 text-primary-600 text-sm font-semibold hover:bg-primary-50 transition-all duration-200"
              @click="goToDashboard"
            >
              返回首页
            </button>
          </div>
        </div>
      </transition>
    </main>
  </div>
</template>

<style scoped>
.fade-slide-enter-active,
.fade-slide-leave-active {
  transition: all 0.3s ease;
}

.fade-slide-enter-from {
  opacity: 0;
  transform: translateY(12px);
}

.fade-slide-leave-to {
  opacity: 0;
  transform: translateY(-12px);
}

.fade-enter-active,
.fade-leave-active {
  transition: all 0.3s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
  transform: translateY(8px);
}

@keyframes bounce-in {
  0% {
    transform: scale(0);
    opacity: 0;
  }
  50% {
    transform: scale(1.15);
  }
  100% {
    transform: scale(1);
    opacity: 1;
  }
}

.animate-bounce-in {
  animation: bounce-in 0.5s ease-out;
}
</style>
