import os

base = r"e:\workspace\MeetingPilot\MeetingPilot\frontend\meetingPilot-frontend\src"

def write(rel, content):
    fp = os.path.join(base, rel)
    os.makedirs(os.path.dirname(fp), exist_ok=True)
    with open(fp, "w", encoding="utf-8") as f:
        f.write(content)
    print("Created:", fp)

action_panel = """<template>
  <div class="action-panel h-full flex flex-col">
    <div v-if="agentStore.isActionsLoading" v-loading="true" class="flex-1 min-h-[200px]"></div>
    <div v-else-if="agentStore.actions.length === 0" class="flex-1 flex flex-col items-center justify-center py-12 text-brown-400">
      <el-icon :size="48" class="mb-4 text-primary-200"><List /></el-icon>
      <p class="text-sm mb-4">暂无待办事项</p>
      <el-button type="primary" round :loading="isExtracting" @click="handleExtract">提取待办</el-button>
    </div>
    <div v-else class="flex-1 overflow-y-auto pr-1 space-y-2">
      <div v-for="item in agentStore.actions" :key="item.id"
        class="bg-white rounded-xl p-3 shadow-soft border border-primary-100 transition-all duration-200 hover:shadow-soft-lg"
        :class="{ 'opacity-60': item.status === ActionStatus.DONE || item.status === ActionStatus.CANCELED }">
        <div class="flex items-start gap-2.5">
          <el-checkbox :model-value="item.status === ActionStatus.DONE" class="mt-0.5 shrink-0"
            @change="handleToggleDone(item)" />
          <div class="flex-1 min-w-0">
            <p class="text-sm text-brown-700 leading-relaxed"
              :class="{ 'line-through text-brown-400': item.status === ActionStatus.DONE }">
              {{ item.task }}
            </p>
            <div class="flex items-center gap-2 mt-1.5 flex-wrap">
              <el-tag :type="priorityTagType(item.priority)" size="small" round>{{ priorityLabel(item.priority) }}</el-tag>
              <span v-if="item.owner" class="text-xs text-brown-400 flex items-center gap-0.5">
                <el-icon :size="12"><User /></el-icon>{{ item.owner }}
              </span>
              <span v-if="item.deadline" class="text-xs text-brown-400 flex items-center gap-0.5">
                <el-icon :size="12"><Clock /></el-icon>{{ formatDate(item.deadline) }}
              </span>
            </div>
          </div>
          <el-dropdown trigger="click" @command="(cmd: string) => handleCommand(cmd, item)">
            <el-button text size="small" class="text-brown-400"><el-icon><MoreFilled /></el-icon></el-button>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item command="doing" :disabled="item.status === ActionStatus.DOING">进行中</el-dropdown-item>
                <el-dropdown-item command="cancel" :disabled="item.status === ActionStatus.CANCELED">取消</el-dropdown-item>
                <el-dropdown-item command="sync">同步到飞书</el-dropdown-item>
                <el-dropdown-item command="delete" divided>删除</el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </div>
      <div class="text-right pt-2">
        <el-button size="small" round :loading="isExtracting" @click="handleExtract">重新提取</el-button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { ElMessageBox, ElMessage } from 'element-plus'
import { List, User, Clock, MoreFilled } from '@element-plus/icons-vue'
import { useAgentStore } from '@/stores/agent'
import { ActionStatus, Priority, type ActionItemRead } from '@/types'

const props = defineProps<{ meetingId: string }>()
const agentStore = useAgentStore()
const isExtracting = ref(false)

async function handleToggleDone(item: ActionItemRead) {
  const newStatus = item.status === ActionStatus.DONE ? ActionStatus.TODO : ActionStatus.DONE
  await agentStore.editAction(item.id, { status: newStatus })
}

async function handleExtract() {
  isExtracting.value = true
  try { await agentStore.triggerExtractActions(props.meetingId) } finally { isExtracting.value = false }
}

async function handleCommand(command: string, item: ActionItemRead) {
  switch (command) {
    case 'doing': await agentStore.editAction(item.id, { status: ActionStatus.DOING }); break
    case 'cancel': await agentStore.editAction(item.id, { status: ActionStatus.CANCELED }); break
    case 'sync':
      try { await agentStore.syncActionToExternal(item.id); ElMessage.success('已同步到飞书') }
      catch { ElMessage.error('同步失败') }
      break
    case 'delete':
      await ElMessageBox.confirm('确定删除此待办项？', '删除确认', { confirmButtonText: '删除', cancelButtonText: '取消', type: 'warning' })
      await agentStore.removeAction(item.id)
      break
  }
}

function priorityTagType(priority: Priority) {
  switch (priority) { case Priority.URGENT: return 'danger'; case Priority.HIGH: return 'warning'; case Priority.MEDIUM: return 'info'; case Priority.LOW: return ''; default: return 'info' }
}

function priorityLabel(priority: Priority) {
  switch (priority) { case Priority.URGENT: return '紧急'; case Priority.HIGH: return '高'; case Priority.MEDIUM: return '中'; case Priority.LOW: return '低'; default: return priority }
}

function formatDate(dateStr: string | null) {
  if (!dateStr) return ''
  const d = new Date(dateStr)
  return d.getMonth() + 1 + '/' + d.getDate()
}
</script>
"""

write("components/meeting/ActionPanel.vue", action_panel)
