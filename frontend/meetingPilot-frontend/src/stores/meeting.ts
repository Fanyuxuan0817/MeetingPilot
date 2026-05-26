import { ref, computed } from 'vue'
import { defineStore } from 'pinia'
import type WaveSurfer from 'wavesurfer.js'
import type {
  MeetingRead,
  MeetingCreate,
  MeetingUpdate,
  TranscriptChunkRead,
  TranscriptListRead,
} from '@/types'
import {
  listMeetings,
  getMeeting,
  createMeeting,
  updateMeeting,
  deleteMeeting,
  uploadMeeting,
  getMeetingJobs,
  runAgents,
} from '@/api/meetings'
import { getMeetingTranscripts } from '@/api/transcripts'
import type { ListMeetingsParams, UploadMeetingParams, RunAgentsParams } from '@/api/meetings'

export const useMeetingStore = defineStore('meeting', () => {
  const meetings = ref<MeetingRead[]>([])
  const currentMeeting = ref<MeetingRead | null>(null)
  const transcripts = ref<TranscriptChunkRead[]>([])
  const currentTime = ref(0)
  const isPlaying = ref(false)
  const isLoading = ref(false)
  const error = ref<unknown>(null)
  const pagination = ref({ total: 0, page: 1, size: 20 })
  const filters = ref<ListMeetingsParams>({})
  const waveSurfer = ref<WaveSurfer | null>(null)

  const meetingCount = computed(() => pagination.value.total)

  const activeFilters = computed(() => {
    const f = filters.value
    return !!(f.keyword || f.status || f.tag)
  })

  function clearError() {
    error.value = null
  }

  async function loadMeetings(overrideParams?: ListMeetingsParams) {
    isLoading.value = true
    error.value = null
    try {
      const params = overrideParams ?? filters.value
      const res = await listMeetings(params)
      meetings.value = res.items
      pagination.value.total = res.total
      pagination.value.page = res.page
      pagination.value.size = res.size
    } catch (err) {
      error.value = err
      throw err
    } finally {
      isLoading.value = false
    }
  }

  async function loadMeetingData(id: string) {
    isLoading.value = true
    error.value = null
    try {
      const [meetingData, transcriptData] = await Promise.all([
        getMeeting(id),
        getMeetingTranscripts(id),
      ])
      currentMeeting.value = meetingData
      transcripts.value = transcriptData.chunks
    } catch (err) {
      error.value = err
      throw err
    } finally {
      isLoading.value = false
    }
  }

  async function addMeeting(data: MeetingCreate) {
    error.value = null
    try {
      const res = await createMeeting(data)
      meetings.value.unshift(res)
      return res
    } catch (err) {
      error.value = err
      throw err
    }
  }

  async function editMeeting(meetingId: string, data: MeetingUpdate) {
    error.value = null
    try {
      const res = await updateMeeting(meetingId, data)
      if (currentMeeting.value?.id === meetingId) {
        currentMeeting.value = res
      }
      const idx = meetings.value.findIndex((m) => m.id === meetingId)
      if (idx !== -1) meetings.value[idx] = res
      return res
    } catch (err) {
      error.value = err
      throw err
    }
  }

  async function removeMeeting(meetingId: string) {
    error.value = null
    try {
      await deleteMeeting(meetingId)
      meetings.value = meetings.value.filter((m) => m.id !== meetingId)
      if (currentMeeting.value?.id === meetingId) {
        currentMeeting.value = null
        transcripts.value = []
      }
    } catch (err) {
      error.value = err
      throw err
    }
  }

  async function uploadAudio(params: UploadMeetingParams) {
    error.value = null
    try {
      return await uploadMeeting(params)
    } catch (err) {
      error.value = err
      throw err
    }
  }

  async function fetchMeetingJobs(meetingId: string) {
    error.value = null
    try {
      return await getMeetingJobs(meetingId)
    } catch (err) {
      error.value = err
      throw err
    }
  }

  async function triggerAgents(meetingId: string, params?: RunAgentsParams) {
    error.value = null
    try {
      return await runAgents(meetingId, params)
    } catch (err) {
      error.value = err
      throw err
    }
  }

  function updateCurrentTime(time: number) {
    currentTime.value = time
  }

  function setPlaying(playing: boolean) {
    isPlaying.value = playing
  }

  function setWaveSurfer(ws: WaveSurfer | null) {
    waveSurfer.value = ws
  }

  function setFilters(newFilters: ListMeetingsParams) {
    filters.value = newFilters
    loadMeetings()
  }

  return {
    meetings,
    currentMeeting,
    transcripts,
    currentTime,
    isPlaying,
    isLoading,
    error,
    pagination,
    filters,
    waveSurfer,
    meetingCount,
    activeFilters,
    clearError,
    loadMeetings,
    loadMeetingData,
    addMeeting,
    editMeeting,
    removeMeeting,
    uploadAudio,
    fetchMeetingJobs,
    triggerAgents,
    updateCurrentTime,
    setPlaying,
    setWaveSurfer,
    setFilters,
  }
})
