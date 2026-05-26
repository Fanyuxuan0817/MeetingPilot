<script setup lang="ts">
import { computed, ref, watch, onUnmounted } from 'vue'
import { Microphone, Cpu, Document, List, ChatDotRound } from '@element-plus/icons-vue'

export type AgentNodeKey = 'transcriber' | 'summarizer' | 'action_extractor' | 'qa_agent'

interface AgentNode {
  key: AgentNodeKey
  label: string
  icon: typeof Microphone
  description: string
}

const nodes: AgentNode[] = [
  { key: 'transcriber', label: 'Transcriber', icon: Microphone, description: '语音转文字' },
  { key: 'summarizer', label: 'Summarizer', icon: Document, description: '智能纪要' },
  { key: 'action_extractor', label: 'Action Agent', icon: List, description: '待办提取' },
  { key: 'qa_agent', label: 'QA Agent', icon: ChatDotRound, description: '智能问答' },
]

const props = defineProps<{
  activeAgent: AgentNodeKey | null
  completedAgents: AgentNodeKey[]
  failed?: boolean
}>()

const nodeStates = computed(() => {
  const map = new Map<AgentNodeKey, 'pending' | 'active' | 'done'>()
  for (const node of nodes) {
    if (props.completedAgents.includes(node.key)) {
      map.set(node.key, 'done')
    } else if (props.activeAgent === node.key) {
      map.set(node.key, 'active')
    } else {
      map.set(node.key, 'pending')
    }
  }
  return map
})

function edgeState(from: AgentNodeKey, to: AgentNodeKey): 'pending' | 'active' | 'done' {
  const fromState = nodeStates.value.get(from)
  const toState = nodeStates.value.get(to)
  if (fromState === 'done' && (toState === 'done' || toState === 'active')) return 'done'
  if (fromState === 'done' && toState === 'active') return 'active'
  if (fromState === 'active') return 'active'
  return 'pending'
}

const pulsePhase = ref(0)
let animFrame: number | null = null

function animate() {
  pulsePhase.value = (pulsePhase.value + 0.02) % 1
  animFrame = requestAnimationFrame(animate)
}

watch(
  () => props.activeAgent,
  (val) => {
    if (val && !animFrame) {
      animate()
    } else if (!val && animFrame) {
      cancelAnimationFrame(animFrame)
      animFrame = null
    }
  },
  { immediate: true },
)

onUnmounted(() => {
  if (animFrame) cancelAnimationFrame(animFrame)
})

const pulseOpacity = computed(() => {
  return 0.4 + Math.sin(pulsePhase.value * Math.PI * 2) * 0.3
})
</script>

<template>
  <div class="w-full max-w-xl mx-auto py-6">
    <div class="relative flex flex-col items-center">
      <div class="flex items-start justify-center gap-0 w-full">
        <div class="flex flex-col items-center" style="width: 100px">
          <div
            :class="[
              'agent-node w-16 h-16 rounded-2xl flex items-center justify-center transition-all duration-500',
              nodeStates.get('transcriber') === 'done'
                ? 'bg-green-400 shadow-lg shadow-green-200/50'
                : nodeStates.get('transcriber') === 'active'
                  ? 'bg-primary-400 shadow-lg shadow-primary-200/50'
                  : 'bg-brown-100',
            ]"
            :style="
              nodeStates.get('transcriber') === 'active'
                ? { opacity: pulseOpacity }
                : {}
            "
          >
            <el-icon
              v-if="nodeStates.get('transcriber') === 'done'"
              :size="24"
              color="#fff"
            >
              <Cpu />
            </el-icon>
            <el-icon
              v-else
              :size="24"
              :color="nodeStates.get('transcriber') === 'active' ? '#fff' : '#a8a29e'"
            >
              <Microphone />
            </el-icon>
          </div>
          <span
            :class="[
              'text-xs font-semibold mt-2 transition-colors duration-300',
              nodeStates.get('transcriber') === 'done'
                ? 'text-green-500'
                : nodeStates.get('transcriber') === 'active'
                  ? 'text-primary-600'
                  : 'text-brown-300',
            ]"
          >
            Transcriber
          </span>
          <span
            :class="[
              'text-[10px] transition-colors duration-300',
              nodeStates.get('transcriber') === 'done'
                ? 'text-green-400'
                : nodeStates.get('transcriber') === 'active'
                  ? 'text-primary-400'
                  : 'text-brown-200',
            ]"
          >
            语音转文字
          </span>
        </div>
      </div>

      <div class="flex items-center justify-center w-full mt-2 mb-2">
        <svg width="320" height="40" viewBox="0 0 320 40" class="overflow-visible">
          <path
            d="M160 0 C160 20, 50 20, 50 40"
            :class="[
              'transition-all duration-700',
              edgeState('transcriber', 'summarizer') === 'done'
                ? 'stroke-green-400'
                : edgeState('transcriber', 'summarizer') === 'active'
                  ? 'stroke-primary-400'
                  : 'stroke-brown-200',
            ]"
            fill="none"
            stroke-width="2"
            stroke-dasharray="4 4"
          />
          <path
            d="M160 0 L160 40"
            :class="[
              'transition-all duration-700',
              edgeState('transcriber', 'action_extractor') === 'done'
                ? 'stroke-green-400'
                : edgeState('transcriber', 'action_extractor') === 'active'
                  ? 'stroke-primary-400'
                  : 'stroke-brown-200',
            ]"
            fill="none"
            stroke-width="2"
            stroke-dasharray="4 4"
          />
          <path
            d="M160 0 C160 20, 270 20, 270 40"
            :class="[
              'transition-all duration-700',
              edgeState('transcriber', 'qa_agent') === 'done'
                ? 'stroke-green-400'
                : edgeState('transcriber', 'qa_agent') === 'active'
                  ? 'stroke-primary-400'
                  : 'stroke-brown-200',
            ]"
            fill="none"
            stroke-width="2"
            stroke-dasharray="4 4"
          />

          <circle
            v-if="edgeState('transcriber', 'summarizer') === 'active'"
            r="3"
            fill="#facc15"
          >
            <animateMotion dur="1.5s" repeatCount="indefinite" path="M160 0 C160 20, 50 20, 50 40" />
          </circle>
          <circle
            v-if="edgeState('transcriber', 'action_extractor') === 'active'"
            r="3"
            fill="#facc15"
          >
            <animateMotion dur="1.5s" repeatCount="indefinite" path="M160 0 L160 40" />
          </circle>
          <circle
            v-if="edgeState('transcriber', 'qa_agent') === 'active'"
            r="3"
            fill="#facc15"
          >
            <animateMotion dur="1.5s" repeatCount="indefinite" path="M160 0 C160 20, 270 20, 270 40" />
          </circle>
        </svg>
      </div>

      <div class="flex items-start justify-center gap-8 w-full">
        <div
          v-for="agent in nodes.slice(1)"
          :key="agent.key"
          class="flex flex-col items-center"
          style="width: 100px"
        >
          <div
            :class="[
              'agent-node w-16 h-16 rounded-2xl flex items-center justify-center transition-all duration-500',
              nodeStates.get(agent.key) === 'done'
                ? 'bg-green-400 shadow-lg shadow-green-200/50'
                : nodeStates.get(agent.key) === 'active'
                  ? 'bg-primary-400 shadow-lg shadow-primary-200/50'
                  : 'bg-brown-100',
            ]"
            :style="
              nodeStates.get(agent.key) === 'active'
                ? { opacity: pulseOpacity }
                : {}
            "
          >
            <el-icon
              v-if="nodeStates.get(agent.key) === 'done'"
              :size="24"
              color="#fff"
            >
              <Cpu />
            </el-icon>
            <el-icon
              v-else
              :size="24"
              :color="nodeStates.get(agent.key) === 'active' ? '#fff' : '#a8a29e'"
            >
              <component :is="agent.icon" />
            </el-icon>
          </div>
          <span
            :class="[
              'text-xs font-semibold mt-2 transition-colors duration-300',
              nodeStates.get(agent.key) === 'done'
                ? 'text-green-500'
                : nodeStates.get(agent.key) === 'active'
                  ? 'text-primary-600'
                  : 'text-brown-300',
            ]"
          >
            {{ agent.label }}
          </span>
          <span
            :class="[
              'text-[10px] transition-colors duration-300',
              nodeStates.get(agent.key) === 'done'
                ? 'text-green-400'
                : nodeStates.get(agent.key) === 'active'
                  ? 'text-primary-400'
                  : 'text-brown-200',
            ]"
          >
            {{ agent.description }}
          </span>
        </div>
      </div>
    </div>
  </div>
</template>
