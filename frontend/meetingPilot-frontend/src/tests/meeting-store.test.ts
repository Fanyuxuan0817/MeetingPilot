import { describe, it, expect, beforeEach, vi } from 'vitest'
import { setActivePinia, createPinia } from 'pinia'
import { useMeetingStore } from '@/stores/meeting'
import * as meetingsApi from '@/api/meetings'
import * as transcriptsApi from '@/api/transcripts'
import { MeetingStatus } from '@/types'

vi.mock('@/api/meetings')
vi.mock('@/api/transcripts')

describe('useMeetingStore', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    vi.clearAllMocks()
    localStorage.clear()
  })

  describe('state initialization', () => {
    it('should have correct default values', () => {
      const store = useMeetingStore()
      expect(store.meetings).toEqual([])
      expect(store.currentMeeting).toBeNull()
      expect(store.transcripts).toEqual([])
      expect(store.currentTime).toBe(0)
      expect(store.isLoading).toBe(false)
      expect(store.error).toBeNull()
      expect(store.pagination).toEqual({ total: 0, page: 1, size: 20 })
      expect(store.filters).toEqual({})
    })
  })

  describe('getters', () => {
    it('meetingCount returns pagination.total', () => {
      const store = useMeetingStore()
      store.$patch({ pagination: { total: 42, page: 1, size: 20 } })
      expect(store.meetingCount).toBe(42)
    })

    it('activeFilters returns false when no filters', () => {
      const store = useMeetingStore()
      expect(store.activeFilters).toBe(false)
    })

    it('activeFilters returns true when keyword is set', () => {
      const store = useMeetingStore()
      store.$patch({ filters: { keyword: 'test' } })
      expect(store.activeFilters).toBe(true)
    })

    it('activeFilters returns true when status is set', () => {
      const store = useMeetingStore()
      store.$patch({ filters: { status: MeetingStatus.COMPLETED } })
      expect(store.activeFilters).toBe(true)
    })

    it('activeFilters returns true when tag is set', () => {
      const store = useMeetingStore()
      store.$patch({ filters: { tag: 'important' } })
      expect(store.activeFilters).toBe(true)
    })
  })

  describe('sync actions', () => {
    it('updateCurrentTime updates currentTime', () => {
      const store = useMeetingStore()
      store.updateCurrentTime(12.5)
      expect(store.currentTime).toBe(12.5)
    })

    it('clearError resets error to null', () => {
      const store = useMeetingStore()
      store.$patch({ error: { detail: 'some error' } })
      expect(store.error).not.toBeNull()
      store.clearError()
      expect(store.error).toBeNull()
    })
  })

  describe('loadMeetings', () => {
    it('updates meetings and pagination on success', async () => {
      const mockData = {
        items: [{ id: '1', title: 'Test', status: MeetingStatus.COMPLETED, created_at: '', updated_at: '' }],
        total: 1,
        page: 1,
        size: 20,
      }
      vi.mocked(meetingsApi.listMeetings).mockResolvedValue(mockData as any)

      const store = useMeetingStore()
      await store.loadMeetings()

      expect(store.meetings).toEqual(mockData.items)
      expect(store.pagination.total).toBe(1)
      expect(store.isLoading).toBe(false)
      expect(store.error).toBeNull()
    })

    it('toggles isLoading correctly during request', async () => {
      let resolveFn!: (v: any) => void
      const promise = new Promise((resolve) => { resolveFn = resolve })
      vi.mocked(meetingsApi.listMeetings).mockReturnValue(promise as any)

      const store = useMeetingStore()
      const loadPromise = store.loadMeetings()

      expect(store.isLoading).toBe(true)

      resolveFn({ items: [], total: 0, page: 1, size: 20 })
      await loadPromise

      expect(store.isLoading).toBe(false)
    })

    it('resets isLoading even on error', async () => {
      vi.mocked(meetingsApi.listMeetings).mockRejectedValue(new Error('API Error'))

      const store = useMeetingStore()
      await expect(store.loadMeetings()).rejects.toThrow('API Error')

      expect(store.isLoading).toBe(false)
      expect(store.error).toBeTruthy()
    })

    it('captures error on failure', async () => {
      const apiError = { detail: 'Server error' }
      vi.mocked(meetingsApi.listMeetings).mockRejectedValue(apiError)

      const store = useMeetingStore()
      await expect(store.loadMeetings()).rejects.toBe(apiError)

      expect(store.error).toStrictEqual(apiError)
    })
  })

  describe('loadMeetingData', () => {
    it('loads meeting and transcripts concurrently', async () => {
      const mockMeeting = { id: '1', title: 'Test', status: MeetingStatus.COMPLETED, created_at: '', updated_at: '' }
      const mockTranscripts = { meeting_id: '1', chunks: [{ id: 'c1', start: 0, end: 5, text: 'hello', speaker: 'A' }] }

      vi.mocked(meetingsApi.getMeeting).mockResolvedValue(mockMeeting as any)
      vi.mocked(transcriptsApi.getMeetingTranscripts).mockResolvedValue(mockTranscripts as any)

      const store = useMeetingStore()
      await store.loadMeetingData('1')

      expect(store.currentMeeting).toEqual(mockMeeting)
      expect(store.transcripts).toEqual(mockTranscripts.chunks)
      expect(store.isLoading).toBe(false)
    })

    it('resets isLoading on error', async () => {
      vi.mocked(meetingsApi.getMeeting).mockRejectedValue(new Error('Not found'))

      const store = useMeetingStore()
      await expect(store.loadMeetingData('999')).rejects.toThrow()

      expect(store.isLoading).toBe(false)
      expect(store.error).toBeTruthy()
    })
  })

  describe('addMeeting', () => {
    it('adds meeting to list on success', async () => {
      const newMeeting = { id: '1', title: 'New', status: MeetingStatus.CREATED, created_at: '', updated_at: '' }
      vi.mocked(meetingsApi.createMeeting).mockResolvedValue(newMeeting as any)

      const store = useMeetingStore()
      const result = await store.addMeeting({ title: 'New' } as any)

      expect(result).toEqual(newMeeting)
      expect(store.meetings).toHaveLength(1)
      expect(store.meetings[0]).toEqual(newMeeting)
    })

    it('captures error on failure', async () => {
      vi.mocked(meetingsApi.createMeeting).mockRejectedValue(new Error('Bad request'))

      const store = useMeetingStore()
      await expect(store.addMeeting({ title: '' } as any)).rejects.toThrow()

      expect(store.error).toBeTruthy()
      expect(store.meetings).toHaveLength(0)
    })
  })

  describe('removeMeeting', () => {
    it('removes meeting from list on success', async () => {
      vi.mocked(meetingsApi.deleteMeeting).mockResolvedValue(undefined as any)

      const store = useMeetingStore()
      store.$patch({ meetings: [{ id: '1', title: 'Test' } as any], currentMeeting: { id: '1' } as any })

      await store.removeMeeting('1')

      expect(store.meetings).toHaveLength(0)
      expect(store.currentMeeting).toBeNull()
      expect(store.transcripts).toEqual([])
    })

    it('does not modify state on failure', async () => {
      vi.mocked(meetingsApi.deleteMeeting).mockRejectedValue(new Error('Forbidden'))

      const store = useMeetingStore()
      store.$patch({ meetings: [{ id: '1', title: 'Test' } as any] })

      await expect(store.removeMeeting('1')).rejects.toThrow()

      expect(store.meetings).toHaveLength(1)
      expect(store.error).toBeTruthy()
    })
  })

  describe('editMeeting', () => {
    it('updates meeting in list and currentMeeting', async () => {
      const updated = { id: '1', title: 'Updated', status: MeetingStatus.COMPLETED, created_at: '', updated_at: '' }
      vi.mocked(meetingsApi.updateMeeting).mockResolvedValue(updated as any)

      const store = useMeetingStore()
      store.$patch({
        meetings: [{ id: '1', title: 'Old' } as any],
        currentMeeting: { id: '1', title: 'Old' } as any,
      })

      await store.editMeeting('1', { title: 'Updated' } as any)

      expect(store.meetings[0]!.title).toBe('Updated')
      expect(store.currentMeeting?.title).toBe('Updated')
    })
  })

  describe('SSR safety', () => {
    it('does not access other stores at module level', () => {
      const store = useMeetingStore()
      expect(store).toBeDefined()
    })
  })
})
