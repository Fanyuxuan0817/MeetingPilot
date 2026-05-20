export enum JobStatus {
  PENDING = 'pending',
  RUNNING = 'running',
  COMPLETED = 'completed',
  FAILED = 'failed',
}

export interface PaginationResponse<T> {
  items: T[]
  total: number
  page: number
  size: number
}

export interface ErrorResponse {
  code: string
  message: string
  details?: Record<string, unknown> | null
}

export interface JobResponse {
  meeting_id: string
  job_id: string
  status: JobStatus
}
