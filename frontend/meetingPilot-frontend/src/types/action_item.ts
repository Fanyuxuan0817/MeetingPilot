export enum ActionStatus {
  TODO = 'todo',
  DOING = 'doing',
  DONE = 'done',
  CANCELED = 'canceled',
}

export enum Priority {
  LOW = 'low',
  MEDIUM = 'medium',
  HIGH = 'high',
  URGENT = 'urgent',
}

export interface ActionItemBase {
  task: string
  owner: string
  deadline: string | null
  priority: Priority
  source_chunk_id: string | null
}

export interface ActionItemCreate extends ActionItemBase {}

export interface ActionItemUpdate {
  task?: string | null
  owner?: string | null
  deadline?: string | null
  priority?: Priority | null
  status?: ActionStatus | null
}

export interface ActionItemRead extends ActionItemBase {
  id: string
  meeting_id: string
  status: ActionStatus
  updated_at: string | null
}

export interface ActionListResponse {
  meeting_id: string
  items: ActionItemRead[]
}

export interface FeishuSyncResponse {
  action_id: string
  provider: string
  external_id: string
  status: string
  synced_at: string
}
