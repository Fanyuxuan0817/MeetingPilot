import apiClient from './client'
import type {
  TranscriptChunkRead,
  TranscriptChunkUpdate,
  TranscriptListRead,
} from '@/types'

export interface GetMeetingTranscriptsParams {
  speaker?: string
  keyword?: string
}

export function getMeetingTranscripts(meetingId: string, params?: GetMeetingTranscriptsParams) {
  return apiClient.get<TranscriptListRead>(`/meetings/${meetingId}/transcripts`, { params })
}

export function getTranscriptChunk(chunkId: string) {
  return apiClient.get<TranscriptChunkRead>(`/transcripts/${chunkId}`)
}

export function updateTranscriptChunk(chunkId: string, data: TranscriptChunkUpdate) {
  return apiClient.patch<TranscriptChunkRead>(`/transcripts/${chunkId}`, data)
}
