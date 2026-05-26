<template>
  <div class="summary-panel h-full flex flex-col">
    <div v-if="agentStore.isSummaryLoading" v-loading="true" class="flex-1 min-h-[200px]"></div>

    <div v-else-if="!agentStore.summary" class="flex-1 flex flex-col items-center justify-center py-12 text-brown-400">
      <el-icon :size="48" class="mb-4 text-primary-200"><Document /></el-icon>
      <p class="text-sm mb-4">暂无智能纪要</p>
      <button
        class="px-5 py-2 rounded-full bg-primary-400 hover:bg-primary-500 text-white text-sm font-medium shadow-soft transition-all duration-200 active:scale-95 disabled:opacity-50 disabled:cursor-not-allowed"
        :disabled="isGenerating"
        @click="handleGenerate"
      >
        {{ isGenerating ? '生成中...' : '生成纪要' }}
      </button>
    </div>

    <div v-else class="flex-1 overflow-y-auto pr-1 space-y-5">
      <section>
        <h3 class="text-sm font-semibold text-brown-700 mb-2 flex items-center gap-1.5">
          <el-icon :size="16" class="text-primary-500"><Memo /></el-icon>
          概述
        </h3>
        <p class="text-sm text-brown-600 leading-relaxed bg-soft-cream rounded-xl p-3">
          {{ agentStore.summary.summary.overview }}
        </p>
      </section>

      <section v-if="agentStore.summary.summary.topics.length > 0">
        <h3 class="text-sm font-semibold text-brown-700 mb-2 flex items-center gap-1.5">
          <el-icon :size="16" class="text-secondary-500"><ChatDotRound /></el-icon>
          讨论主题
        </h3>
        <div class="space-y-2">
          <div v-for="(topic, idx) in agentStore.summary.summary.topics" :key="idx"
            class="bg-white rounded-xl p-3 shadow-soft border border-primary-100">
            <h4 class="text-sm font-medium text-brown-800 mb-1">{{ topic.title }}</h4>
            <p class="text-xs text-brown-500 leading-relaxed">{{ topic.content }}</p>
          </div>
        </div>
      </section>

      <section v-if="agentStore.summary.summary.decisions.length > 0">
        <h3 class="text-sm font-semibold text-brown-700 mb-2 flex items-center gap-1.5">
          <el-icon :size="16" class="text-accent-500"><Stamp /></el-icon>
          决策记录
        </h3>
        <div class="space-y-2">
          <div v-for="(d, idx) in agentStore.summary.summary.decisions" :key="idx"
            class="bg-soft-warm rounded-xl p-3 border border-accent-100">
            <span class="text-xs font-semibold text-accent-600">{{ d.topic }}</span>
            <p class="text-sm text-brown-600 mt-1">{{ d.decision }}</p>
          </div>
        </div>
      </section>

      <section v-if="agentStore.summary.summary.risks.length > 0">
        <h3 class="text-sm font-semibold text-brown-700 mb-2 flex items-center gap-1.5">
          <el-icon :size="16" class="text-red-400"><Warning /></el-icon>
          风险提示
        </h3>
        <div class="space-y-2">
          <div v-for="(risk, idx) in agentStore.summary.summary.risks" :key="idx"
            class="rounded-xl p-3 border" :class="riskLevelClass(risk.level)">
            <div class="flex items-center gap-2 mb-1">
              <el-tag :type="riskLevelTag(risk.level)" size="small" round>{{ riskLevelLabel(risk.level) }}</el-tag>
              <span class="text-sm font-medium text-brown-800">{{ risk.title }}</span>
            </div>
            <p class="text-xs text-brown-500">{{ risk.description }}</p>
          </div>
        </div>
      </section>

      <section v-if="agentStore.summary.summary.open_questions.length > 0">
        <h3 class="text-sm font-semibold text-brown-700 mb-2 flex items-center gap-1.5">
          <el-icon :size="16" class="text-primary-400"><QuestionFilled /></el-icon>
          待解决问题
        </h3>
        <ul class="space-y-1.5">
          <li v-for="(q, idx) in agentStore.summary.summary.open_questions" :key="idx"
            class="text-sm text-brown-600 flex items-start gap-2">
            <span class="text-primary-400 mt-0.5 shrink-0">&#9679;</span>
            {{ q }}
          </li>
        </ul>
      </section>

      <div class="text-right pt-2">
        <button
          class="px-4 py-1.5 rounded-full bg-white hover:bg-primary-50 text-primary-600 text-xs font-medium border border-primary-200 shadow-soft transition-all duration-200 active:scale-95 disabled:opacity-50 disabled:cursor-not-allowed"
          :disabled="isGenerating"
          @click="handleGenerate"
        >
          {{ isGenerating ? '生成中...' : '重新生成' }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from "vue";
import { Document, Memo, ChatDotRound, Stamp, Warning, QuestionFilled } from "@element-plus/icons-vue";
import { useAgentStore } from "@/stores/agent";
import { RiskLevel } from "@/types";

const props = defineProps<{ meetingId: string }>();

const agentStore = useAgentStore();
const isGenerating = ref(false);

async function handleGenerate() {
  isGenerating.value = true;
  try {
    await agentStore.generateSummary(props.meetingId);
  } finally {
    isGenerating.value = false;
  }
}

function riskLevelClass(level: RiskLevel) {
  switch (level) {
    case RiskLevel.HIGH: return "bg-red-50 border-red-200";
    case RiskLevel.MEDIUM: return "bg-accent-50 border-accent-200";
    case RiskLevel.LOW: return "bg-primary-50 border-primary-200";
    default: return "bg-slate-50 border-slate-200";
  }
}

function riskLevelTag(level: RiskLevel) {
  switch (level) {
    case RiskLevel.HIGH: return "danger";
    case RiskLevel.MEDIUM: return "warning";
    case RiskLevel.LOW: return "info";
    default: return "info";
  }
}

function riskLevelLabel(level: RiskLevel) {
  switch (level) {
    case RiskLevel.HIGH: return "高";
    case RiskLevel.MEDIUM: return "中";
    case RiskLevel.LOW: return "低";
    default: return level;
  }
}
</script>
