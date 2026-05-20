import apiClient from './client'
import type {
  QARequest,
  QAResponse,
  MemorySearchResponse,
  MeetingGraphResponse,
  GraphQueryResponse,
} from '@/types'

export function askQuestion(data: QARequest) {
  return apiClient.post<QAResponse>('/qa', data)
}

export interface SearchMemoryParams {
  query: string
  limit?: number
  filters?: Record<string, unknown>
}

export function searchMemory(params: SearchMemoryParams) {
  return apiClient.post<MemorySearchResponse>('/memory/search', params)
}

export function getMeetingGraph(meetingId: string) {
  return apiClient.get<MeetingGraphResponse>(`/meetings/${meetingId}/graph`)
}

export function queryGraph(question: string) {
  return apiClient.post<GraphQueryResponse>('/graph/query', null, { params: { question } })
}
