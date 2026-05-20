import apiClient from './client'
import type {
  MeetingCreate,
  MeetingRead,
  MeetingUpdate,
  PaginationResponse,
  JobResponse,
  MeetingJobsResponse,
} from '@/types'
import { MeetingStatus } from '@/types'

export interface ListMeetingsParams {
  page?: number
  size?: number
  keyword?: string
  status?: MeetingStatus
  tag?: string
}

export interface UploadMeetingParams {
  file: File
  title: string
  description?: string
  language?: string
  enable_speaker_diarization?: boolean
}

export interface RetranscribeParams {
  language?: string
  enable_speaker_diarization?: boolean
}

export interface RunAgentsParams {
  agents?: string[]
}

export function createMeeting(data: MeetingCreate) {
  return apiClient.post<MeetingRead>('/meetings', data)
}

export function uploadMeeting(params: UploadMeetingParams) {
  const formData = new FormData()
  formData.append('file', params.file)
  formData.append('title', params.title)
  if (params.description != null) {
    formData.append('description', params.description)
  }
  if (params.language != null) {
    formData.append('language', params.language)
  }
  formData.append('enable_speaker_diarization', String(params.enable_speaker_diarization ?? true))

  return apiClient.post<JobResponse>('/meetings/upload', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  })
}

export function listMeetings(params?: ListMeetingsParams) {
  return apiClient.get<PaginationResponse<MeetingRead>>('/meetings', { params })
}

export function getMeeting(meetingId: string) {
  return apiClient.get<MeetingRead>(`/meetings/${meetingId}`)
}

export function updateMeeting(meetingId: string, data: MeetingUpdate) {
  return apiClient.patch<MeetingRead>(`/meetings/${meetingId}`, data)
}

export function deleteMeeting(meetingId: string) {
  return apiClient.delete(`/meetings/${meetingId}`)
}

export function retranscribeMeeting(meetingId: string, params?: RetranscribeParams) {
  return apiClient.post<JobResponse>(`/meetings/${meetingId}/transcribe`, null, { params })
}

export function getMeetingJobs(meetingId: string) {
  return apiClient.get<MeetingJobsResponse>(`/meetings/${meetingId}/jobs`)
}

export function runAgents(meetingId: string, params?: RunAgentsParams) {
  return apiClient.post<JobResponse>(`/meetings/${meetingId}/agents/run`, params ?? {})
}
