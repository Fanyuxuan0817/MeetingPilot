import apiClient from './client'
import type {
  ActionItemCreate,
  ActionItemRead,
  ActionItemUpdate,
  ActionListResponse,
  JobResponse,
  FeishuSyncResponse,
} from '@/types'

export function getMeetingActions(meetingId: string) {
  return apiClient.get<ActionListResponse>(`/meetings/${meetingId}/actions`).then((res: any) => res as ActionListResponse)
}

export function createAction(meetingId: string, data: ActionItemCreate) {
  return apiClient.post<ActionItemRead>(`/meetings/${meetingId}/actions`, data).then((res: any) => res as ActionItemRead)
}

export function updateAction(actionId: string, data: ActionItemUpdate) {
  return apiClient.patch<ActionItemRead>(`/actions/${actionId}`, data).then((res: any) => res as ActionItemRead)
}

export function deleteAction(actionId: string) {
  return apiClient.delete(`/actions/${actionId}`)
}

export function extractActions(meetingId: string) {
  return apiClient.post<JobResponse>(`/meetings/${meetingId}/actions/extract`).then((res: any) => res as JobResponse)
}

export interface SyncActionToFeishuParams {
  target?: string
  notify_owner?: boolean
}

export function syncActionToFeishu(actionId: string, params?: SyncActionToFeishuParams) {
  return apiClient.post<FeishuSyncResponse>(`/actions/${actionId}/sync/feishu`, null, { params }).then((res: any) => res as FeishuSyncResponse)
}
