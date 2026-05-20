export interface TranscriptChunkBase {
  speaker: string
  content: string
}

export interface TranscriptChunkUpdate {
  speaker?: string | null
  content?: string | null
}

export interface TranscriptChunkRead extends TranscriptChunkBase {
  id: string
  meeting_id: string
  start: number
  end: number
  confidence: number | null
  updated_at: string | null
}

export interface TranscriptListRead {
  meeting_id: string
  chunks: TranscriptChunkRead[]
}
