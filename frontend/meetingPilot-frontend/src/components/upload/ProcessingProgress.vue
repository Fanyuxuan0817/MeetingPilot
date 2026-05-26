<script setup lang="ts">
import { computed } from 'vue'
import { Upload, Microphone, Cpu, Check, Warning } from '@element-plus/icons-vue'

export type ProcessingPhase = 'idle' | 'uploading' | 'transcribing' | 'analyzing' | 'completed' | 'failed'

const props = defineProps<{
  phase: ProcessingPhase
  progress: number
  errorMessage?: string | null
}>()

const phases = computed(() => [
  {
    key: 'uploading' as const,
    label: '正在上传',
    icon: Upload,
    description: '音频文件上传中...',
  },
  {
    key: 'transcribing' as const,
    label: '正在转录',
    icon: Microphone,
    description: 'AI 语音转文字中...',
  },
  {
    key: 'analyzing' as const,
    label: 'Agent 分析',
    icon: Cpu,
    description: '智能体正在分析会议内容...',
  },
])

const currentPhaseIndex = computed(() => {
  const idx = phases.value.findIndex((p) => p.key === props.phase)
  return idx === -1 ? -1 : idx
})

const progressPercent = computed(() => Math.min(100, Math.max(0, props.progress)))

function phaseState(key: ProcessingPhase): 'pending' | 'active' | 'done' {
  if (props.phase === 'failed') {
    return phases.value.findIndex((p) => p.key === key) <= currentPhaseIndex.value ? 'active' : 'pending'
  }
  const idx = phases.value.findIndex((p) => p.key === key)
  if (idx < currentPhaseIndex.value) return 'done'
  if (idx === currentPhaseIndex.value) return 'active'
  return 'pending'
}

const statusMessage = computed(() => {
  if (props.phase === 'idle') return '准备上传...'
  if (props.phase === 'failed') return props.errorMessage ?? '处理失败'
  if (props.phase === 'completed') return '处理完成！'
  const current = phases.value.find((p) => p.key === props.phase)
  return current?.description ?? '处理中...'
})
</script>

<template>
  <div class="w-full max-w-lg mx-auto">
    <div class="flex items-center justify-between mb-6">
      <div
        v-for="(phase, index) in phases"
        :key="phase.key"
        class="flex items-center"
        :class="index < phases.length - 1 ? 'flex-1' : ''"
      >
        <div class="flex flex-col items-center">
          <div
            :class="[
              'w-12 h-12 rounded-2xl flex items-center justify-center transition-all duration-500',
              phaseState(phase.key) === 'done'
                ? 'bg-green-400 shadow-md shadow-green-200'
                : phaseState(phase.key) === 'active'
                  ? 'bg-primary-400 shadow-md shadow-primary-200 animate-pulse-soft'
                  : 'bg-brown-100',
            ]"
          >
            <el-icon
              v-if="phaseState(phase.key) === 'done'"
              :size="20"
              color="#fff"
            >
              <Check />
            </el-icon>
            <el-icon
              v-else
              :size="20"
              :color="phaseState(phase.key) === 'active' ? '#fff' : '#a8a29e'"
            >
              <component :is="phase.icon" />
            </el-icon>
          </div>
          <span
            :class="[
              'text-xs font-medium mt-2 transition-colors duration-300',
              phaseState(phase.key) === 'done'
                ? 'text-green-500'
                : phaseState(phase.key) === 'active'
                  ? 'text-primary-600'
                  : 'text-brown-300',
            ]"
          >
            {{ phase.label }}
          </span>
        </div>

        <div
          v-if="index < phases.length - 1"
          :class="[
            'flex-1 h-0.5 mx-3 rounded-full transition-all duration-700',
            phaseState(phase.key) === 'done'
              ? 'bg-green-400'
              : phaseState(phase.key) === 'active'
                ? 'bg-gradient-to-r from-primary-400 to-primary-200'
                : 'bg-brown-100',
          ]"
        />
      </div>
    </div>

    <div class="relative w-full h-3 bg-brown-100 rounded-full overflow-hidden mb-4">
      <div
        :class="[
          'h-full rounded-full transition-all duration-500 ease-out',
          phase === 'failed'
            ? 'bg-red-400'
            : phase === 'completed'
              ? 'bg-green-400'
              : 'bg-gradient-to-r from-primary-400 via-primary-300 to-secondary-400',
        ]"
        :style="{ width: `${progressPercent}%` }"
      />
      <div
        v-if="phase !== 'idle' && phase !== 'completed' && phase !== 'failed'"
        class="absolute top-0 left-0 h-full w-20 bg-gradient-to-r from-transparent via-white/40 to-transparent animate-shimmer rounded-full"
        :style="{ transform: `translateX(${progressPercent}%)` }"
      />
    </div>

    <div class="flex items-center justify-between">
      <p
        :class="[
          'text-sm font-medium',
          phase === 'failed'
            ? 'text-red-500'
            : phase === 'completed'
              ? 'text-green-500'
              : 'text-brown-500',
        ]"
      >
        <el-icon v-if="phase === 'failed'" :size="14" class="mr-1 align-middle"><Warning /></el-icon>
        {{ statusMessage }}
      </p>
      <span class="text-sm font-semibold text-brown-400">{{ progressPercent }}%</span>
    </div>
  </div>
</template>

<style scoped>
@keyframes pulse-soft {
  0%, 100% { transform: scale(1); }
  50% { transform: scale(1.08); }
}

@keyframes shimmer {
  0% { transform: translateX(-100%); }
  100% { transform: translateX(500%); }
}

.animate-pulse-soft {
  animation: pulse-soft 2s ease-in-out infinite;
}

.animate-shimmer {
  animation: shimmer 2s ease-in-out infinite;
}
</style>
