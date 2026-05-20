import { describe, it, expect, beforeEach, vi } from 'vitest'
import { setActivePinia, createPinia } from 'pinia'
import { useAgentStore } from '@/stores/agent'
import * as summariesApi from '@/api/summaries'
import * as actionsApi from '@/api/actions'
import * as decisionsApi from '@/api/decisions'
import { ActionStatus } from '@/types'

vi.mock('@/api/summaries')
vi.mock('@/api/actions')
vi.mock('@/api/decisions')

describe('useAgentStore', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    vi.clearAllMocks()
    localStorage.clear()
  })

  describe('state initialization', () => {
    it('should have correct default values', () => {
      const store = useAgentStore()
      expect(store.summary).toBeNull()
      expect(store.actions).toEqual([])
      expect(store.decisions).toEqual([])
      expect(store.conflicts).toEqual([])
      expect(store.chatMessages).toEqual([])
      expect(store.isStreaming).toBe(false)
      expect(store.agentJobs).toEqual([])
      expect(store.isSummaryLoading).toBe(false)
      expect(store.isActionsLoading).toBe(false)
      expect(store.isDecisionsLoading).toBe(false)
      expect(store.isConflictsLoading).toBe(false)
      expect(store.error).toBeNull()
    })
  })

  describe('getters', () => {
    it('hasConflicts returns false when no conflicts', () => {
      const store = useAgentStore()
      expect(store.hasConflicts).toBe(false)
    })

    it('hasConflicts returns true when conflicts exist', () => {
      const store = useAgentStore()
      store.$patch({ conflicts: [{ id: '1', description: 'conflict' } as any] })
      expect(store.hasConflicts).toBe(true)
    })

    it('pendingActions filters out DONE and CANCELED', () => {
      const store = useAgentStore()
      store.$patch({
        actions: [
          { id: '1', status: ActionStatus.PENDING } as any,
          { id: '2', status: ActionStatus.IN_PROGRESS } as any,
          { id: '3', status: ActionStatus.DONE } as any,
          { id: '4', status: ActionStatus.CANCELED } as any,
        ],
      })

      expect(store.pendingActions).toHaveLength(2)
      expect(store.pendingActions.map((a) => a.id)).toEqual(['1', '2'])
    })
  })

  describe('sync actions', () => {
    it('appendChatMessage adds message to list', () => {
      const store = useAgentStore()
      const msg = { id: '1', role: 'user' as const, content: 'Hello', timestamp: Date.now() }
      store.appendChatMessage(msg)
      expect(store.chatMessages).toHaveLength(1)
      expect(store.chatMessages[0]).toEqual(msg)
    })

    it('updateLastAssistantMessage appends chunk to last assistant message', () => {
      const store = useAgentStore()
      store.appendChatMessage({ id: '1', role: 'user', content: 'Q', timestamp: 1 })
      store.appendChatMessage({ id: '2', role: 'assistant', content: 'Hello', timestamp: 2 })

      store.updateLastAssistantMessage(' world')

      expect(store.chatMessages[1].content).toBe('Hello world')
    })

    it('updateLastAssistantMessage does nothing if last message is from user', () => {
      const store = useAgentStore()
      store.appendChatMessage({ id: '1', role: 'user', content: 'Q', timestamp: 1 })

      store.updateLastAssistantMessage('chunk')

      expect(store.chatMessages[0].content).toBe('Q')
    })

    it('setStreaming updates isStreaming', () => {
      const store = useAgentStore()
      store.setStreaming(true)
      expect(store.isStreaming).toBe(true)
      store.setStreaming(false)
      expect(store.isStreaming).toBe(false)
    })

    it('clearChat empties chatMessages', () => {
      const store = useAgentStore()
      store.appendChatMessage({ id: '1', role: 'user', content: 'Hi', timestamp: 1 })
      store.clearChat()
      expect(store.chatMessages).toEqual([])
    })

    it('clearError resets error to null', () => {
      const store = useAgentStore()
      store.$patch({ error: { detail: 'fail' } })
      store.clearError()
      expect(store.error).toBeNull()
    })

    it('resetForNewMeeting clears all state', () => {
      const store = useAgentStore()
      store.$patch({
        summary: { id: '1' } as any,
        actions: [{ id: '1' } as any],
        decisions: [{ id: '1' } as any],
        conflicts: [{ id: '1' } as any],
        chatMessages: [{ id: '1', role: 'user', content: 'hi', timestamp: 1 }],
        isStreaming: true,
        agentJobs: [{ id: '1' } as any],
        error: { detail: 'fail' },
        isSummaryLoading: true,
        isActionsLoading: true,
        isDecisionsLoading: true,
        isConflictsLoading: true,
      })

      store.resetForNewMeeting()

      expect(store.summary).toBeNull()
      expect(store.actions).toEqual([])
      expect(store.decisions).toEqual([])
      expect(store.conflicts).toEqual([])
      expect(store.chatMessages).toEqual([])
      expect(store.isStreaming).toBe(false)
      expect(store.agentJobs).toEqual([])
      expect(store.error).toBeNull()
      expect(store.isSummaryLoading).toBe(false)
      expect(store.isActionsLoading).toBe(false)
      expect(store.isDecisionsLoading).toBe(false)
      expect(store.isConflictsLoading).toBe(false)
    })
  })

  describe('loadSummary', () => {
    it('updates summary on success', async () => {
      const mockSummary = { id: '1', meeting_id: 'm1', topics: [], overall_summary: 'test' }
      vi.mocked(summariesApi.getMeetingSummary).mockResolvedValue(mockSummary as any)

      const store = useAgentStore()
      await store.loadSummary('m1')

      expect(store.summary).toEqual(mockSummary)
      expect(store.isSummaryLoading).toBe(false)
      expect(store.error).toBeNull()
    })

    it('toggles isSummaryLoading during request', async () => {
      let resolveFn!: (v: any) => void
      const promise = new Promise((resolve) => { resolveFn = resolve })
      vi.mocked(summariesApi.getMeetingSummary).mockReturnValue(promise as any)

      const store = useAgentStore()
      const loadPromise = store.loadSummary('m1')

      expect(store.isSummaryLoading).toBe(true)

      resolveFn({ id: '1', meeting_id: 'm1', topics: [], overall_summary: 'test' })
      await loadPromise

      expect(store.isSummaryLoading).toBe(false)
    })

    it('resets isSummaryLoading on error', async () => {
      vi.mocked(summariesApi.getMeetingSummary).mockRejectedValue(new Error('Not found'))

      const store = useAgentStore()
      await expect(store.loadSummary('m1')).rejects.toThrow()

      expect(store.isSummaryLoading).toBe(false)
      expect(store.error).toBeTruthy()
    })
  })

  describe('loadActions', () => {
    it('updates actions on success', async () => {
      const mockActions = { items: [{ id: '1', description: 'Do something' }], total: 1 }
      vi.mocked(actionsApi.getMeetingActions).mockResolvedValue(mockActions as any)

      const store = useAgentStore()
      await store.loadActions('m1')

      expect(store.actions).toEqual(mockActions.items)
      expect(store.isActionsLoading).toBe(false)
    })

    it('resets isActionsLoading on error', async () => {
      vi.mocked(actionsApi.getMeetingActions).mockRejectedValue(new Error('Fail'))

      const store = useAgentStore()
      await expect(store.loadActions('m1')).rejects.toThrow()

      expect(store.isActionsLoading).toBe(false)
      expect(store.error).toBeTruthy()
    })
  })

  describe('loadDecisions', () => {
    it('updates decisions on success', async () => {
      const mockDecisions = { items: [{ id: '1', content: 'Decided X' }], total: 1 }
      vi.mocked(decisionsApi.getMeetingDecisions).mockResolvedValue(mockDecisions as any)

      const store = useAgentStore()
      await store.loadDecisions('m1')

      expect(store.decisions).toEqual(mockDecisions.items)
      expect(store.isDecisionsLoading).toBe(false)
    })

    it('resets isDecisionsLoading on error', async () => {
      vi.mocked(decisionsApi.getMeetingDecisions).mockRejectedValue(new Error('Fail'))

      const store = useAgentStore()
      await expect(store.loadDecisions('m1')).rejects.toThrow()

      expect(store.isDecisionsLoading).toBe(false)
    })
  })

  describe('loadConflicts', () => {
    it('updates conflicts on success', async () => {
      const mockConflicts = { items: [{ id: '1', description: 'Conflict' }], total: 1 }
      vi.mocked(decisionsApi.getMeetingConflicts).mockResolvedValue(mockConflicts as any)

      const store = useAgentStore()
      await store.loadConflicts('m1')

      expect(store.conflicts).toEqual(mockConflicts.items)
      expect(store.isConflictsLoading).toBe(false)
    })

    it('resets isConflictsLoading on error', async () => {
      vi.mocked(decisionsApi.getMeetingConflicts).mockRejectedValue(new Error('Fail'))

      const store = useAgentStore()
      await expect(store.loadConflicts('m1')).rejects.toThrow()

      expect(store.isConflictsLoading).toBe(false)
    })
  })

  describe('addAction', () => {
    it('appends action to list on success', async () => {
      const newAction = { id: '1', description: 'New action', status: ActionStatus.PENDING }
      vi.mocked(actionsApi.createAction).mockResolvedValue(newAction as any)

      const store = useAgentStore()
      await store.addAction('m1', { description: 'New action' } as any)

      expect(store.actions).toHaveLength(1)
      expect(store.actions[0]).toEqual(newAction)
    })

    it('does not modify state on failure', async () => {
      vi.mocked(actionsApi.createAction).mockRejectedValue(new Error('Bad request'))

      const store = useAgentStore()
      await expect(store.addAction('m1', {} as any)).rejects.toThrow()

      expect(store.actions).toHaveLength(0)
      expect(store.error).toBeTruthy()
    })
  })

  describe('SSR safety', () => {
    it('does not access other stores at module level', () => {
      const store = useAgentStore()
      expect(store).toBeDefined()
    })
  })
})
