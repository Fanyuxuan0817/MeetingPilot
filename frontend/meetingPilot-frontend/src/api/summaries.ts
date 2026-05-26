import apiClient from './client'
import type { SummaryRead, JobResponse } from '@/types'

export function getMeetingSummary(meetingId: string) {
  return apiClient.get<SummaryRead>(`/meetings/${meetingId}/summary`).then((res: any) => res as SummaryRead)
}

export function generateMeetingSummary(meetingId: string) {
  return apiClient.post<JobResponse>(`/meetings/${meetingId}/summary/generate`).then((res: any) => res as JobResponse)
}
