export enum MeetingStatus {
  CREATED = 'created',
  UPLOADING = 'uploading',
  TRANSCRIBING = 'transcribing',
  ANALYZING = 'analyzing',
  COMPLETED = 'completed',
  FAILED = 'failed',
}

export interface MeetingBase {
  title: string
  description: string | null
  tags: string[]
}

export interface MeetingCreate extends MeetingBase {
  started_at: string
}

export interface MeetingUpdate {
  title?: string | null
  description?: string | null
  tags?: string[] | null
}

export interface MeetingRead extends MeetingBase {
  id: string
  status: MeetingStatus
  duration: number | null
  audio_url: string | null
  language: string | null
  created_at: string
  updated_at: string | null
}
