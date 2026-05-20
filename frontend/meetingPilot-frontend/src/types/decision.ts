export enum ConflictLevel {
  LOW = 'low',
  MEDIUM = 'medium',
  HIGH = 'high',
}

export interface DecisionRead {
  id: string
  topic: string
  decision: string
  version: number
  source_chunk_id: string
  created_at: string
}

export interface DecisionConflictRead {
  id: string
  topic: string
  current_decision: string
  previous_decision: string
  level: ConflictLevel
  description: string
  current_source_chunk_id: string
  previous_meeting_id: string
}

export interface DecisionListResponse {
  meeting_id: string
  items: DecisionRead[]
}

export interface ConflictListResponse {
  meeting_id: string
  items: DecisionConflictRead[]
}
