import { ref, computed } from 'vue'
import { defineStore } from 'pinia'
import type {
  SummaryRead,
  ActionItemRead,
  ActionItemCreate,
  ActionItemUpdate,
  ActionListResponse,
  DecisionRead,
  DecisionConflictRead,
  DecisionListResponse,
  ConflictListResponse,
  ChatMessage,
  JobResponse,
  MeetingJobItem,
} from '@/types'
import { ActionStatus } from '@/types'
import { getMeetingSummary, generateMeetingSummary } from '@/api/summaries'
import {
  getMeetingActions,
  createAction,
  updateAction,
  deleteAction,
  extractActions,
  syncActionToFeishu,
} from '@/api/actions'
import type { SyncActionToFeishuParams } from '@/api/actions'
import { getMeetingDecisions, getMeetingConflicts, detectConflicts } from '@/api/decisions'

export const useAgentStore = defineStore('agent', () => {
  const summary = ref<SummaryRead | null>(null)
  const actions = ref<ActionItemRead[]>([])
  const decisions = ref<DecisionRead[]>([])
  const conflicts = ref<DecisionConflictRead[]>([])
  const chatMessages = ref<ChatMessage[]>([])
  const isStreaming = ref(false)
  const agentJobs = ref<MeetingJobItem[]>([])

  const isSummaryLoading = ref(false)
  const isActionsLoading = ref(false)
  const isDecisionsLoading = ref(false)
  const isConflictsLoading = ref(false)
  const error = ref<unknown>(null)

  const hasConflicts = computed(() => conflicts.value.length > 0)

  const pendingActions = computed(() =>
    actions.value.filter((a) => a.status !== ActionStatus.DONE && a.status !== ActionStatus.CANCELED),
  )

  function clearError() {
    error.value = null
  }

  async function loadSummary(meetingId: string) {
    isSummaryLoading.value = true
    error.value = null
    try {
      const res = await getMeetingSummary(meetingId) as SummaryRead
      summary.value = res
      return res
    } catch (err) {
      error.value = err
      throw err
    } finally {
      isSummaryLoading.value = false
    }
  }

  async function generateSummary(meetingId: string) {
    error.value = null
    try {
      return await generateMeetingSummary(meetingId) as Promise<JobResponse>
    } catch (err) {
      error.value = err
      throw err
    }
  }

  async function loadActions(meetingId: string) {
    isActionsLoading.value = true
    error.value = null
    try {
      const res = await getMeetingActions(meetingId) as ActionListResponse
      actions.value = res.items
      return res
    } catch (err) {
      error.value = err
      throw err
    } finally {
      isActionsLoading.value = false
    }
  }

  async function addAction(meetingId: string, data: ActionItemCreate) {
    error.value = null
    try {
      const res = await createAction(meetingId, data) as ActionItemRead
      actions.value.push(res)
      return res
    } catch (err) {
      error.value = err
      throw err
    }
  }

  async function editAction(actionId: string, data: ActionItemUpdate) {
    error.value = null
    try {
      const res = await updateAction(actionId, data) as ActionItemRead
      const idx = actions.value.findIndex((a) => a.id === actionId)
      if (idx !== -1) actions.value[idx] = res
      return res
    } catch (err) {
      error.value = err
      throw err
    }
  }

  async function removeAction(actionId: string) {
    error.value = null
    try {
      await deleteAction(actionId)
      actions.value = actions.value.filter((a) => a.id !== actionId)
    } catch (err) {
      error.value = err
      throw err
    }
  }

  async function triggerExtractActions(meetingId: string) {
    error.value = null
    try {
      return await extractActions(meetingId) as Promise<JobResponse>
    } catch (err) {
      error.value = err
      throw err
    }
  }

  async function syncActionToExternal(actionId: string, params?: SyncActionToFeishuParams) {
    error.value = null
    try {
      return await syncActionToFeishu(actionId, params)
    } catch (err) {
      error.value = err
      throw err
    }
  }

  async function loadDecisions(meetingId: string) {
    isDecisionsLoading.value = true
    error.value = null
    try {
      const res = await getMeetingDecisions(meetingId) as DecisionListResponse
      decisions.value = res.items
      return res
    } catch (err) {
      error.value = err
      throw err
    } finally {
      isDecisionsLoading.value = false
    }
  }

  async function loadConflicts(meetingId: string) {
    isConflictsLoading.value = true
    error.value = null
    try {
      const res = await getMeetingConflicts(meetingId) as ConflictListResponse
      conflicts.value = res.items
      return res
    } catch (err) {
      error.value = err
      throw err
    } finally {
      isConflictsLoading.value = false
    }
  }

  async function triggerDetectConflicts(meetingId: string) {
    error.value = null
    try {
      return await detectConflicts(meetingId) as Promise<JobResponse>
    } catch (err) {
      error.value = err
      throw err
    }
  }

  function appendChatMessage(msg: ChatMessage) {
    chatMessages.value.push(msg)
  }

  function updateLastAssistantMessage(chunk: string) {
    const last = chatMessages.value[chatMessages.value.length - 1]
    if (last && last.role === 'assistant') {
      last.content += chunk
    }
  }

  function setStreaming(value: boolean) {
    isStreaming.value = value
  }

  function setAgentJobs(jobs: MeetingJobItem[]) {
    agentJobs.value = jobs
  }

  function clearChat() {
    chatMessages.value = []
  }

  function resetForNewMeeting() {
    summary.value = null
    actions.value = []
    decisions.value = []
    conflicts.value = []
    chatMessages.value = []
    isStreaming.value = false
    agentJobs.value = []
    error.value = null
    isSummaryLoading.value = false
    isActionsLoading.value = false
    isDecisionsLoading.value = false
    isConflictsLoading.value = false
  }

  return {
    summary,
    actions,
    decisions,
    conflicts,
    chatMessages,
    isStreaming,
    agentJobs,
    isSummaryLoading,
    isActionsLoading,
    isDecisionsLoading,
    isConflictsLoading,
    error,
    hasConflicts,
    pendingActions,
    clearError,
    loadSummary,
    generateSummary,
    loadActions,
    addAction,
    editAction,
    removeAction,
    triggerExtractActions,
    syncActionToExternal,
    loadDecisions,
    loadConflicts,
    triggerDetectConflicts,
    appendChatMessage,
    updateLastAssistantMessage,
    setStreaming,
    setAgentJobs,
    clearChat,
    resetForNewMeeting,
  }
})
