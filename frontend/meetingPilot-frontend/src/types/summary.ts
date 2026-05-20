export enum RiskLevel {
  LOW = 'low',
  MEDIUM = 'medium',
  HIGH = 'high',
}

export interface Topic {
  title: string
  content: string
  source_chunk_ids: string[]
}

export interface DecisionShort {
  topic: string
  decision: string
  source_chunk_ids: string[]
}

export interface Risk {
  title: string
  level: RiskLevel
  description: string
}

export interface SummaryDetail {
  overview: string
  topics: Topic[]
  decisions: DecisionShort[]
  risks: Risk[]
  open_questions: string[]
}

export interface SummaryRead {
  meeting_id: string
  summary: SummaryDetail
  generated_at: string
}
