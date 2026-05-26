<template>
  <div class="max-w-3xl mx-auto p-6 space-y-6">
    <h1 class="text-2xl font-bold text-brown-800">🐱 音文联动测试</h1>

    <div class="flex gap-2 flex-wrap">
      <el-button size="small" @click="testLoading">
        🔄 测试加载状态
      </el-button>
      <el-button size="small" @click="testError">
        ❌ 测试加载失败
      </el-button>
      <el-button size="small" @click="testEmpty">
        📭 测试空数据
      </el-button>
      <el-button size="small" @click="testNormal">
        ✅ 恢复正常
      </el-button>
    </div>

    <Waveform :url="audioUrl" />

    <div class="bg-white rounded-xl shadow-soft p-4">
      <h2 class="text-lg font-semibold text-brown-700 mb-3">转录文本</h2>
      <TranscriptList />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import Waveform from '@/components/audio/Waveform.vue'
import TranscriptList from '@/components/transcript/TranscriptList.vue'
import { useMeetingStore } from '@/stores/meeting'
import { useAudioPlayer } from '@/composables/useAudioPlayer'
import type { TranscriptChunkRead } from '@/types'

const store = useMeetingStore()
const { destroy } = useAudioPlayer()

const audioUrl = ref('https://cdn.freesound.org/previews/612/612095_5674468-lq.mp3')

const mockTranscripts: TranscriptChunkRead[] = [
  { id: 'chunk-1', meeting_id: 'test', speaker: '说话人A', content: '大家好，欢迎参加今天的项目评审会议。', start: 0, end: 2, confidence: 0.95, updated_at: null },
  { id: 'chunk-2', meeting_id: 'test', speaker: '说话人B', content: '谢谢，我先来汇报一下进展情况。', start: 2.2, end: 4.5, confidence: 0.92, updated_at: null },
  { id: 'chunk-3', meeting_id: 'test', speaker: '说话人A', content: '好的，请开始吧。', start: 4.7, end: 6, confidence: 0.88, updated_at: null },
  { id: 'chunk-4', meeting_id: 'test', speaker: '说话人B', content: '本季度完成了三个核心模块的开发。', start: 6.2, end: 8.5, confidence: 0.91, updated_at: null },
  { id: 'chunk-5', meeting_id: 'test', speaker: '说话人C', content: '测试覆盖率目前达到了百分之八十五。', start: 8.7, end: 11, confidence: 0.87, updated_at: null },
  { id: 'chunk-6', meeting_id: 'test', speaker: '说话人A', content: '下个季度目标可以设定在百分之九十。', start: 11.2, end: 13.5, confidence: 0.93, updated_at: null },
  { id: 'chunk-7', meeting_id: 'test', speaker: '说话人C', content: '同意，我们会继续优化测试流程。', start: 13.7, end: 15.5, confidence: 0.90, updated_at: null },
]

store.transcripts = mockTranscripts

function testLoading() {
  destroy()
  audioUrl.value = ''
  setTimeout(() => {
    audioUrl.value = 'https://cdn.freesound.org/previews/612/612095_5674468-lq.mp3'
  }, 100)
}

function testError() {
  destroy()
  audioUrl.value = 'https://invalid-url.example.com/not-exist.mp3'
}

function testEmpty() {
  store.transcripts = []
}

function testNormal() {
  audioUrl.value = 'https://cdn.freesound.org/previews/612/612095_5674468-lq.mp3'
  store.transcripts = mockTranscripts
}
</script>
