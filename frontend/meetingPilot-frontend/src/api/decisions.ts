import apiClient from './client'
import type {
  DecisionListResponse,
  ConflictListResponse,
  JobResponse,
} from '@/types'

export function getMeetingDecisions(meetingId: string) {
  return apiClient.get<DecisionListResponse>(`/meetings/${meetingId}/decisions`).then((res: any) => res as DecisionListResponse)
}

export function getMeetingConflicts(meetingId: string) {
  return apiClient.get<ConflictListResponse>(`/meetings/${meetingId}/conflicts`).then((res: any) => res as ConflictListResponse)
}

export function detectConflicts(meetingId: string) {
  return apiClient.post<JobResponse>(`/meetings/${meetingId}/conflicts/detect`).then((res: any) => res as JobResponse)
}
