import apiClient from './client'
import type { SummaryRead, JobResponse } from '@/types'

export function getMeetingSummary(meetingId: string) {
  return apiClient.get<SummaryRead>(`/meetings/${meetingId}/summary`)
}

export function generateMeetingSummary(meetingId: string) {
  return apiClient.post<JobResponse>(`/meetings/${meetingId}/summary/generate`)
}
