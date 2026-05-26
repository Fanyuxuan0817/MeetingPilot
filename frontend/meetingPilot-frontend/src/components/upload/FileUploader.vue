<script setup lang="ts">
import { ref, computed } from 'vue'
import { UploadFilled, Document, Close } from '@element-plus/icons-vue'

const ACCEPTED_FORMATS = [
  'audio/mpeg',
  'audio/mp3',
  'audio/wav',
  'audio/x-wav',
  'audio/webm',
  'audio/ogg',
  'audio/flac',
  'audio/x-m4a',
  'audio/mp4',
  'video/mp4',
]

const ACCEPTED_EXTENSIONS = ['.mp3', '.wav', '.webm', '.ogg', '.flac', '.m4a', '.mp4']

const MAX_FILE_SIZE = 500 * 1024 * 1024

const props = defineProps<{
  disabled?: boolean
}>()

const emit = defineEmits<{
  (e: 'select', file: File): void
  (e: 'error', message: string): void
}>()

const isDragging = ref(false)
const selectedFile = ref<File | null>(null)
const fileInputRef = ref<HTMLInputElement | null>(null)

const formattedSize = computed(() => {
  if (!selectedFile.value) return ''
  const bytes = selectedFile.value.size
  if (bytes < 1024) return `${bytes} B`
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`
})

function isValidFile(file: File): string | null {
  const ext = '.' + file.name.split('.').pop()?.toLowerCase()
  if (!ACCEPTED_EXTENSIONS.includes(ext) && !ACCEPTED_FORMATS.includes(file.type)) {
    return `不支持的文件格式 ${ext}，请上传 ${ACCEPTED_EXTENSIONS.join('、')} 格式的音频文件`
  }
  if (file.size > MAX_FILE_SIZE) {
    return '文件大小不能超过 500MB'
  }
  return null
}

function handleDragOver(e: DragEvent) {
  e.preventDefault()
  if (!props.disabled) isDragging.value = true
}

function handleDragLeave(e: DragEvent) {
  e.preventDefault()
  isDragging.value = false
}

function handleDrop(e: DragEvent) {
  e.preventDefault()
  isDragging.value = false
  if (props.disabled) return

  const files = e.dataTransfer?.files
  if (!files || files.length === 0) return

  const file = files[0]
  const error = isValidFile(file)
  if (error) {
    emit('error', error)
    return
  }

  selectedFile.value = file
  emit('select', file)
}

function handleClick() {
  if (props.disabled) return
  fileInputRef.value?.click()
}

function handleFileChange(e: Event) {
  const input = e.target as HTMLInputElement
  const files = input.files
  if (!files || files.length === 0) return

  const file = files[0]
  const error = isValidFile(file)
  if (error) {
    emit('error', error)
    input.value = ''
    return
  }

  selectedFile.value = file
  emit('select', file)
}

function clearFile() {
  selectedFile.value = null
  if (fileInputRef.value) fileInputRef.value.value = ''
}

defineExpose({ clearFile, selectedFile })
</script>

<template>
  <div class="w-full">
    <input
      ref="fileInputRef"
      type="file"
      :accept="ACCEPTED_EXTENSIONS.join(',')"
      class="hidden"
      @change="handleFileChange"
    />

    <div
      v-if="!selectedFile"
      :class="[
        'relative flex flex-col items-center justify-center w-full min-h-[280px] rounded-3xl border-2 border-dashed cursor-pointer transition-all duration-300',
        disabled
          ? 'border-brown-200 bg-brown-50 cursor-not-allowed opacity-60'
          : isDragging
            ? 'border-primary-400 bg-primary-50 scale-[1.02] shadow-soft-lg'
            : 'border-primary-200 bg-white hover:border-primary-300 hover:bg-primary-50/30 hover:shadow-soft',
      ]"
      @click="handleClick"
      @dragover="handleDragOver"
      @dragleave="handleDragLeave"
      @drop="handleDrop"
    >
      <div
        :class="[
          'w-20 h-20 rounded-full flex items-center justify-center mb-4 transition-all duration-300',
          isDragging ? 'bg-primary-400 scale-110' : 'bg-primary-100',
        ]"
      >
        <el-icon :size="36" :class="isDragging ? 'text-white' : 'text-primary-400'">
          <UploadFilled />
        </el-icon>
      </div>

      <p class="text-base font-semibold text-brown-700 mb-1">
        {{ isDragging ? '松开即可上传' : '拖拽音频文件到此处' }}
      </p>
      <p class="text-sm text-brown-400 mb-4">或点击选择文件</p>

      <div class="flex flex-wrap justify-center gap-2">
        <span
          v-for="ext in ACCEPTED_EXTENSIONS"
          :key="ext"
          class="px-2.5 py-0.5 rounded-full bg-primary-50 text-primary-600 text-xs font-medium"
        >
          {{ ext }}
        </span>
      </div>

      <p class="text-xs text-brown-300 mt-3">最大支持 500MB</p>
    </div>

    <div
      v-else
      class="flex items-center gap-4 w-full p-5 rounded-2xl bg-white border border-primary-100 shadow-soft"
    >
      <div class="w-12 h-12 rounded-xl bg-primary-100 flex items-center justify-center shrink-0">
        <el-icon :size="24" class="text-primary-500"><Document /></el-icon>
      </div>

      <div class="flex-1 min-w-0">
        <p class="text-sm font-semibold text-brown-800 truncate">{{ selectedFile.name }}</p>
        <p class="text-xs text-brown-400 mt-0.5">{{ formattedSize }}</p>
      </div>

      <button
        v-if="!disabled"
        class="w-8 h-8 rounded-lg flex items-center justify-center text-brown-400 hover:bg-red-50 hover:text-red-400 transition-colors duration-200"
        @click.stop="clearFile"
      >
        <el-icon :size="16"><Close /></el-icon>
      </button>
    </div>
  </div>
</template>
