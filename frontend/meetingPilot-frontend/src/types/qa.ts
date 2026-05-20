export interface Citation {
  meeting_id: string
  chunk_id: string
  speaker: string
  start: number
  end: number
  text: string
}

export interface QARequest {
  meeting_id?: string | null
  question: string
  scope: 'current_meeting' | 'all_meetings'
}

export interface QAResponse {
  answer: string
  citations: Citation[]
}

export type WSMessageType = 'start' | 'chunk' | 'end' | 'error' | 'job_progress'

export interface WSMessage {
  type: WSMessageType
  message?: string | null
  job_id?: string | null
  progress?: number | null
  citations?: Citation[] | null
}

export interface MemorySearchResultItem {
  meeting_id: string
  meeting_title: string
  chunk_id: string
  speaker: string
  start: number
  end: number
  text: string
  score: number
}

export interface MemorySearchResponse {
  items: MemorySearchResultItem[]
}

export interface GraphNode {
  id: string
  label: string
  type: string
}

export interface GraphEdge {
  source: string
  target: string
  type: string
}

export interface MeetingGraphResponse {
  nodes: GraphNode[]
  edges: GraphEdge[]
}

export interface GraphQueryResponse {
  answer: string
  nodes: GraphNode[]
  edges: GraphEdge[]
}

export interface ChatMessage {
  id: string
  role: 'user' | 'assistant'
  content: string
  citations?: Citation[]
  timestamp: number
}

export interface MeetingJobItem {
  id: string
  type: string
  status: string
  progress: number
  message: string
}

export interface MeetingJobsResponse {
  meeting_id: string
  jobs: MeetingJobItem[]
}
