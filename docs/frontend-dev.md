# MeetingPilot 前端开发文档

> 基于 PRD、API 接口清单与后端 Pydantic Schema 编写，确保前后端契约一致。

---

## 1. 技术栈

| 类别 | 选型 | 说明 |
|------|------|------|
| 框架 | Vue 3 + TypeScript | 组合式 API + `<script setup>` |
| 构建工具 | Vite | 快速冷启动、HMR |
| UI 框架 | Element Plus | 中文生态完善，表单/表格组件丰富 |
| 状态管理 | Pinia | 轻量、TS 友好 |
| 路由 | Vue Router 4 | 支持路由守卫、懒加载 |
| HTTP 客户端 | Axios | 拦截器统一处理鉴权与错误 |
| 音频波形 | WaveSurfer.js | 波形可视化 + 时间跳转 |
| 图谱可视化 | ECharts Graph | 力导向图，知识图谱展示 |
| 代码规范 | ESLint + Prettier | 统一代码风格 |

---

## 2. 项目结构

```
frontend/
├── index.html
├── package.json
├── vite.config.ts
├── tsconfig.json
├── env.d.ts
├── .env                        # 环境变量
├── .env.development            # VITE_API_BASE_URL = http://localhost:8000
├── .env.production
│
├── public/
│   └── favicon.ico
│
└── src/
    ├── main.ts
    ├── App.vue
    │
    ├── api/                        # Axios 封装 + 按模块拆分
    │   ├── client.ts               # Axios 实例、拦截器、错误处理
    │   ├── meetings.ts             # 会议 CRUD + 音频上传
    │   ├── transcripts.ts          # 转录切片查询与修正
    │   ├── summaries.ts            # 结构化纪要
    │   ├── actions.ts              # 待办事项 CRUD
    │   ├── decisions.ts            # 决策记录 + 冲突检测
    │   ├── qa.ts                   # 单次问答
    │   ├── memory.ts               # 跨会议语义检索
    │   ├── graph.ts                # 知识图谱
    │   └── integrations.ts         # 飞书同步等第三方
    │
    ├── assets/
    │   ├── images/
    │   └── styles/
    │       └── main.css            # 全局样式 + Element Plus 主题变量
    │
    ├── components/
    │   ├── common/                 # 通用基础组件
    │   │   ├── AppLayout.vue       # 主布局 (侧边栏 + 顶栏 + 内容)
    │   │   ├── Sidebar.vue         # 侧边导航
    │   │   ├── AppHeader.vue       # 顶部栏
    │   │   ├── EmptyState.vue      # 空状态占位
    │   │   └── ConfirmDialog.vue   # 确认弹窗
    │   │
    │   ├── audio/                  # 音频组件
    │   │   ├── AudioPlayer.vue     # 播放器外壳 (控制按钮 + 速度 + 音量)
    │   │   └── Waveform.vue        # WaveSurfer.js 波形视图
    │   │
    │   ├── meeting/                # 会议公共组件
    │   │   ├── MeetingCard.vue     # 会议列表卡片
    │   │   ├── MeetingForm.vue     # 创建/编辑会议表单
    │   │   ├── AudioUpload.vue     # 音频拖拽上传
    │   │   └── StatusBadge.vue     # 会议状态徽章
    │   │
    │   ├── transcript/             # 转录组件
    │   │   ├── TranscriptList.vue  # 说话人切片列表 (联动波形)
    │   │   └── TranscriptChunk.vue # 单条转录 (说话人 + 时间戳 + 文本)
    │   │
    │   ├── summary/                # 纪要组件
    │   │   ├── SummaryPanel.vue    # 结构化纪要展示
    │   │   ├── TopicCard.vue       # 议题卡片 (含来源链接)
    │   │   └── RiskAlert.vue       # 风险提示
    │   │
    │   ├── qa/                     # 问答组件
    │   │   ├── AgentChat.vue       # 智能问答对话面板
    │   │   ├── ChatBubble.vue      # 问答气泡
    │   │   └── CitationLink.vue    # 引用片段 (可跳转音频)
    │   │
    │   ├── action/                 # 待办组件
    │   │   ├── TaskCard.vue        # 待办卡片
    │   │   └── TaskForm.vue        # 新建/编辑待办表单
    │   │
    │   ├── decision/               # 决策组件
    │   │   ├── DecisionCard.vue    # 决策卡片
    │   │   └── ConflictAlert.vue   # 冲突提示
    │   │
    │   └── graph/                  # 图谱组件
    │       └── KnowledgeGraph.vue  # ECharts 力导向图
    │
    ├── composables/                # 组合式函数
    │   ├── useWaveSurfer.ts        # 音轨初始化 + 精准时间跳转
    │   ├── useWebSocket.ts         # WebSocket 连接管理 (QA 流式 + 事件推送)
    │   ├── useAudioSync.ts         # 音文联动 (播放位置 ↔ 转录高亮)
    │   └── usePolling.ts           # 轮询任务状态 (转录/分析进度)
    │
    ├── router/
    │   └── index.ts                # 路由定义 + 守卫
    │
    ├── stores/                     # Pinia Store
    │   ├── meeting.ts              # 会议列表 + 当前会议
    │   ├── transcript.ts           # 转录切片 + 当前高亮
    │   ├── agent.ts                # Agent 任务状态 + 问答上下文
    │   └── app.ts                  # 全局 UI 状态 (侧边栏折叠等)
    │
    ├── types/                      # TypeScript 类型 (对齐后端 Schema)
    │   ├── meeting.ts
    │   ├── transcript.ts
    │   ├── summary.ts
    │   ├── action.ts
    │   ├── decision.ts
    │   ├── qa.ts
    │   ├── common.ts
    │   └── graph.ts
    │
    └── views/                      # 页面视图
        ├── Dashboard.vue           # 首页 / 会议列表工作台
        ├── MeetingDetail.vue       # 会议详情 (核心双栏布局)
        ├── TaskList.vue            # 全局待办列表
        ├── DecisionTimeline.vue    # 决策时间线
        ├── KnowledgeGraphPage.vue  # 知识图谱全屏页
        ├── Settings.vue            # 系统设置
        └── Login.vue               # 登录页
```

---

## 3. 路由设计

```typescript
const routes = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/Login.vue'),
    meta: { requiresAuth: false }
  },
  {
    path: '/',
    component: () => import('@/components/common/AppLayout.vue'),
    meta: { requiresAuth: true },
    children: [
      {
        path: '',
        name: 'Dashboard',
        component: () => import('@/views/Dashboard.vue')
      },
      {
        path: 'meetings/:id',
        name: 'MeetingDetail',
        component: () => import('@/views/MeetingDetail.vue'),
        props: true
      },
      {
        path: 'tasks',
        name: 'TaskList',
        component: () => import('@/views/TaskList.vue')
      },
      {
        path: 'decisions',
        name: 'DecisionTimeline',
        component: () => import('@/views/DecisionTimeline.vue')
      },
      {
        path: 'knowledge-graph',
        name: 'KnowledgeGraph',
        component: () => import('@/views/KnowledgeGraphPage.vue')
      },
      {
        path: 'settings',
        name: 'Settings',
        component: () => import('@/views/Settings.vue')
      }
    ]
  }
]
```

---

## 4. TypeScript 类型定义

> 与后端 Pydantic Schema 一一对应，作为前后端契约。

### 4.1 通用类型 `types/common.ts`

```typescript
export interface PaginatedResponse<T> {
  items: T[]
  total: number
  page: number
  size: number
}

export interface ErrorResponse {
  code: string
  message: string
  details?: Record<string, unknown>
}

export type JobStatus = 'pending' | 'running' | 'completed' | 'failed'

export interface JobResponse {
  meeting_id: string
  job_id: string
  status: JobStatus
}

export interface JobDetail {
  id: string
  type: string
  status: JobStatus
  progress: number
  message: string
}
```

### 4.2 会议类型 `types/meeting.ts`

```typescript
export type MeetingStatus =
  | 'created'
  | 'uploading'
  | 'transcribing'
  | 'analyzing'
  | 'completed'
  | 'failed'

export interface Meeting {
  id: string
  title: string
  description: string | null
  status: MeetingStatus
  duration: number | null
  audio_url: string | null
  language: string | null
  tags: string[]
  created_at: string
  updated_at: string | null
}

export interface MeetingCreate {
  title: string
  description?: string | null
  started_at: string
  tags?: string[]
}

export interface MeetingUpdate {
  title?: string | null
  description?: string | null
  tags?: string[]
}

export interface MeetingUploadResponse {
  id: string
  title: string
  status: MeetingStatus
  audio_url: string
  job_id: string
  created_at: string
}
```

### 4.3 转录类型 `types/transcript.ts`

```typescript
export interface TranscriptChunk {
  id: string
  meeting_id: string
  speaker: string
  start: number
  end: number
  content: string
  confidence: number | null
  updated_at: string | null
}

export interface TranscriptChunkUpdate {
  speaker?: string | null
  content?: string | null
}

export interface TranscriptListResponse {
  meeting_id: string
  chunks: TranscriptChunk[]
}
```

### 4.4 纪要类型 `types/summary.ts`

```typescript
export type RiskLevel = 'low' | 'medium' | 'high'

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
```

### 4.5 待办类型 `types/action.ts`

```typescript
export type ActionStatus = 'todo' | 'doing' | 'done' | 'canceled'
export type Priority = 'low' | 'medium' | 'high' | 'urgent'

export interface ActionItem {
  id: string
  meeting_id: string
  task: string
  owner: string
  deadline: string | null
  priority: Priority
  status: ActionStatus
  source_chunk_id: string | null
  updated_at: string | null
}

export interface ActionItemCreate {
  task: string
  owner: string
  deadline?: string | null
  priority?: Priority
  source_chunk_id?: string | null
}

export interface ActionItemUpdate {
  task?: string | null
  owner?: string | null
  deadline?: string | null
  priority?: Priority | null
  status?: ActionStatus | null
}
```

### 4.6 决策类型 `types/decision.ts`

```typescript
export type ConflictLevel = 'low' | 'medium' | 'high'

export interface Decision {
  id: string
  topic: string
  decision: string
  version: number
  source_chunk_id: string
  created_at: string
}

export interface DecisionConflict {
  id: string
  topic: string
  current_decision: string
  previous_decision: string
  level: ConflictLevel
  description: string
  current_source_chunk_id: string
  previous_meeting_id: string
}
```

### 4.7 问答类型 `types/qa.ts`

```typescript
export type QAScope = 'current_meeting' | 'all_meetings'

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
  scope?: QAScope
}

export interface QAResponse {
  answer: string
  citations: Citation[]
}

export type WSMessageType = 'start' | 'chunk' | 'end' | 'error' | 'job_progress'

export interface WSMessage {
  type: WSMessageType
  message?: string
  job_id?: string | null
  progress?: number | null
  citations?: Citation[] | null
}
```

### 4.8 图谱类型 `types/graph.ts`

```typescript
export interface GraphNode {
  id: string
  label: string
  type: 'person' | 'task' | 'project' | 'decision' | 'risk'
}

export interface GraphEdge {
  source: string
  target: string
  type: string
}

export interface GraphData {
  nodes: GraphNode[]
  edges: GraphEdge[]
}

export interface GraphQueryRequest {
  question: string
}

export interface GraphQueryResponse {
  answer: string
  nodes: GraphNode[]
  edges: GraphEdge[]
}
```

---

## 5. API 封装

### 5.1 Axios 实例 `api/client.ts`

```typescript
import axios from 'axios'
import type { ErrorResponse } from '@/types/common'
import { ElMessage } from 'element-plus'

const client = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL + '/api/v1',
  timeout: 30000,
})

client.interceptors.request.use((config) => {
  const token = localStorage.getItem('token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

client.interceptors.response.use(
  (res) => res,
  (error) => {
    const data: ErrorResponse = error.response?.data
    if (data?.message) {
      ElMessage.error(data.message)
    }
    if (error.response?.status === 401) {
      localStorage.removeItem('token')
      window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)

export default client
```

### 5.2 会议 API `api/meetings.ts`

```typescript
import client from './client'
import type { Meeting, MeetingCreate, MeetingUpdate, MeetingUploadResponse } from '@/types/meeting'
import type { PaginatedResponse } from '@/types/common'

export function getMeetings(params?: {
  page?: number
  size?: number
  keyword?: string
  status?: string
  tag?: string
}) {
  return client.get<PaginatedResponse<Meeting>>('/meetings', { params })
}

export function getMeeting(id: string) {
  return client.get<Meeting>(`/meetings/${id}`)
}

export function createMeeting(data: MeetingCreate) {
  return client.post<Meeting>('/meetings', data)
}

export function updateMeeting(id: string, data: MeetingUpdate) {
  return client.patch<Meeting>(`/meetings/${id}`, data)
}

export function deleteMeeting(id: string) {
  return client.delete(`/meetings/${id}`)
}

export function uploadAudio(formData: FormData) {
  return client.post<MeetingUploadResponse>('/meetings/upload', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
    timeout: 120000,
  })
}
```

### 5.3 转录 API `api/transcripts.ts`

```typescript
import client from './client'
import type { TranscriptListResponse, TranscriptChunk, TranscriptChunkUpdate } from '@/types/transcript'
import type { JobResponse } from '@/types/common'

export function getTranscripts(meetingId: string, params?: { speaker?: string; keyword?: string }) {
  return client.get<TranscriptListResponse>(`/meetings/${meetingId}/transcripts`, { params })
}

export function getChunk(chunkId: string) {
  return client.get<TranscriptChunk>(`/transcripts/${chunkId}`)
}

export function updateChunk(chunkId: string, data: TranscriptChunkUpdate) {
  return client.patch<TranscriptChunk>(`/transcripts/${chunkId}`, data)
}

export function retranscribe(meetingId: string, data?: { language?: string; enable_speaker_diarization?: boolean }) {
  return client.post<JobResponse>(`/meetings/${meetingId}/transcribe`, data)
}
```

### 5.4 纪要 API `api/summaries.ts`

```typescript
import client from './client'
import type { SummaryRead } from '@/types/summary'
import type { JobResponse } from '@/types/common'

export function getSummary(meetingId: string) {
  return client.get<SummaryRead>(`/meetings/${meetingId}/summary`)
}

export function generateSummary(meetingId: string) {
  return client.post<JobResponse>(`/meetings/${meetingId}/summary/generate`)
}
```

### 5.5 待办 API `api/actions.ts`

```typescript
import client from './client'
import type { ActionItem, ActionItemCreate, ActionItemUpdate } from '@/types/action'
import type { JobResponse } from '@/types/common'

export function getActions(meetingId: string) {
  return client.get<{ meeting_id: string; items: ActionItem[] }>(`/meetings/${meetingId}/actions`)
}

export function createAction(meetingId: string, data: ActionItemCreate) {
  return client.post<ActionItem>(`/meetings/${meetingId}/actions`, data)
}

export function updateAction(actionId: string, data: ActionItemUpdate) {
  return client.patch<ActionItem>(`/actions/${actionId}`, data)
}

export function deleteAction(actionId: string) {
  return client.delete(`/actions/${actionId}`)
}

export function extractActions(meetingId: string) {
  return client.post<JobResponse>(`/meetings/${meetingId}/actions/extract`)
}
```

### 5.6 决策 API `api/decisions.ts`

```typescript
import client from './client'
import type { Decision, DecisionConflict } from '@/types/decision'
import type { JobResponse } from '@/types/common'

export function getDecisions(meetingId: string) {
  return client.get<{ meeting_id: string; items: Decision[] }>(`/meetings/${meetingId}/decisions`)
}

export function getConflicts(meetingId: string) {
  return client.get<{ meeting_id: string; items: DecisionConflict[] }>(`/meetings/${meetingId}/conflicts`)
}

export function detectConflicts(meetingId: string) {
  return client.post<JobResponse>(`/meetings/${meetingId}/conflicts/detect`)
}
```

### 5.7 问答 API `api/qa.ts`

```typescript
import client from './client'
import type { QARequest, QAResponse } from '@/types/qa'

export function askQuestion(data: QARequest) {
  return client.post<QAResponse>('/qa', data)
}
```

### 5.8 记忆检索 API `api/memory.ts`

```typescript
import client from './client'

export interface MemorySearchRequest {
  query: string
  limit?: number
  filters?: Record<string, string>
}

export interface MemorySearchItem {
  meeting_id: string
  meeting_title: string
  chunk_id: string
  speaker: string
  start: number
  end: number
  text: string
  score: number
}

export function searchMemory(data: MemorySearchRequest) {
  return client.post<{ items: MemorySearchItem[] }>('/memory/search', data)
}
```

### 5.9 知识图谱 API `api/graph.ts`

```typescript
import client from './client'
import type { GraphData, GraphQueryRequest, GraphQueryResponse } from '@/types/graph'

export function getMeetingGraph(meetingId: string) {
  return client.get<GraphData>(`/meetings/${meetingId}/graph`)
}

export function queryGraph(data: GraphQueryRequest) {
  return client.post<GraphQueryResponse>('/graph/query', data)
}
```

### 5.10 集成 API `api/integrations.ts`

```typescript
import client from './client'

export function syncActionToFeishu(actionId: string, data: { target: string; notify_owner: boolean }) {
  return client.post(`/actions/${actionId}/sync/feishu`, data)
}

export function getSyncRecords(params?: { provider?: string; meeting_id?: string }) {
  return client.get('/integrations/sync-records', { params })
}
```

---

## 6. WebSocket 封装

### 6.1 `composables/useWebSocket.ts`

```typescript
import { ref, onUnmounted } from 'vue'
import type { WSMessage, Citation } from '@/types/qa'

export function useWebSocket(path: string) {
  const baseUrl = import.meta.env.VITE_WS_BASE_URL || 'ws://localhost:8000'
  const ws = ref<WebSocket | null>(null)
  const isConnected = ref(false)
  const messages = ref<WSMessage[]>([])

  function connect() {
    const url = `${baseUrl}${path}`
    ws.value = new WebSocket(url)

    ws.value.onopen = () => { isConnected.value = true }
    ws.value.onclose = () => { isConnected.value = false }
    ws.value.onerror = () => { isConnected.value = false }
    ws.value.onmessage = (event) => {
      const msg: WSMessage = JSON.parse(event.data)
      messages.value.push(msg)
    }
  }

  function send(data: Record<string, unknown>) {
    ws.value?.send(JSON.stringify(data))
  }

  function close() {
    ws.value?.close()
  }

  onUnmounted(() => close())

  return { isConnected, messages, connect, send, close }
}
```

### 6.2 QA 流式对话用法

```typescript
const { isConnected, messages, connect, send, close } = useWebSocket('/api/v1/chat')

function askQuestion(meetingId: string, question: string, scope = 'current_meeting') {
  send({
    type: 'question',
    meeting_id: meetingId,
    question,
    scope,
  })
}
```

### 6.3 会议事件推送用法

```typescript
const { messages, connect } = useWebSocket(`/api/v1/meetings/${meetingId}/events`)

connect()
// 监听 messages 变化，更新 Agent 任务进度
```

---

## 7. 核心页面设计

### 7.1 Dashboard 首页 `/`

**功能**：会议列表工作台

| 区域 | 组件 | 说明 |
|------|------|------|
| 顶部搜索栏 | `ElInput` + `ElSelect` | 按标题搜索、状态筛选、标签筛选 |
| 操作区 | `ElButton` | 新建会议、上传音频 |
| 会议列表 | `MeetingCard` | 卡片网格，展示标题/状态/时长/标签/时间 |
| 分页 | `ElPagination` | 对接 `page` / `size` 参数 |

**数据流**：
- 调用 `GET /api/v1/meetings` 获取分页列表
- 点击"上传音频"弹出 `AudioUpload` 对话框，调用 `POST /api/v1/meetings/upload`
- 点击卡片跳转 `/meetings/:id`

### 7.2 MeetingDetail 会议详情 `/meetings/:id`

**核心双栏布局**：

```
┌──────────────────────────────────────────────────────┐
│  会议标题  状态徽章  标签  编辑按钮                      │
├────────────────────────────┬─────────────────────────┤
│                            │                         │
│  音频播放器 (Waveform)      │   Tab: 纪要 | 待办 |    │
│                            │        决策 | 问答       │
│  转录列表 (TranscriptList)  │                         │
│  - 说话人 + 时间戳 + 文本   │   [对应 Tab 内容]        │
│  - 点击跳转音频位置         │                         │
│  - 当前播放高亮             │                         │
│                            │                         │
└────────────────────────────┴─────────────────────────┘
```

**左侧面板**：
- `AudioPlayer.vue` + `Waveform.vue`：音频播放与波形
- `TranscriptList.vue`：转录切片列表，点击跳转音频，当前播放段落高亮

**右侧 Tab 面板**：
| Tab | 组件 | 数据源 |
|-----|------|--------|
| 纪要 | `SummaryPanel` | `GET /meetings/:id/summary` |
| 待办 | `TaskCard` 列表 | `GET /meetings/:id/actions` |
| 决策 | `DecisionCard` + `ConflictAlert` | `GET /meetings/:id/decisions` + `GET /meetings/:id/conflicts` |
| 问答 | `AgentChat` | `POST /qa` 或 `WS /chat` |

**音文联动**：
- 播放器 `timeupdate` 事件 → 高亮对应 `TranscriptChunk`
- 点击 `TranscriptChunk` → 跳转播放器到 `start` 时间点
- 点击 `CitationLink` (问答中的引用) → 同时跳转播放器 + 高亮转录

### 7.3 TaskList 全局待办 `/tasks`

| 功能 | 说明 |
|------|------|
| 待办列表 | 按状态/负责人/截止日期分组 |
| 筛选 | 状态、负责人、优先级、日期范围 |
| 状态更新 | 勾选切换 todo/doing/done |
| 新建待办 | 弹窗表单 |
| 来源跳转 | 点击来源会议跳转 MeetingDetail |

### 7.4 DecisionTimeline 决策时间线 `/decisions`

| 功能 | 说明 |
|------|------|
| 时间线 | 按时间展示决策演变 |
| 冲突提示 | 高亮显示决策变化 (ConflictAlert) |
| 来源追溯 | 点击查看原始讨论片段 |

### 7.5 KnowledgeGraphPage 知识图谱 `/knowledge-graph`

| 功能 | 说明 |
|------|------|
| 图谱可视化 | ECharts 力导向图 |
| 节点筛选 | 按类型 (人物/项目/任务/决策/风险) |
| 搜索 | 搜索节点并高亮 |
| 点击详情 | 弹窗展示节点信息与关联 |

---

## 8. 组合式函数设计

### 8.1 `composables/useWaveSurfer.ts`

```typescript
// 职责:
// - 初始化 WaveSurfer 实例
// - 加载音频 URL
// - 暴露 play / pause / seekTo 方法
// - 监听 timeupdate 事件，emit 当前时间
```

### 8.2 `composables/useAudioSync.ts`

```typescript
// 职责:
// - 接收当前播放时间
// - 计算当前高亮的 TranscriptChunk
// - 提供跳转方法 (chunk → 音频时间点)
// - 接收 Citation 的 start 时间，跳转播放器
```

### 8.3 `composables/usePolling.ts`

```typescript
// 职责:
// - 轮询 GET /meetings/:id/jobs 获取任务进度
// - 或监听 WS /meetings/:id/events 推送
// - 任务完成时停止轮询并刷新数据
```

---

## 9. Pinia Store 设计

### 9.1 `stores/meeting.ts`

```typescript
import { defineStore } from 'pinia'
import { ref } from 'vue'
import type { Meeting } from '@/types/meeting'
import type { PaginatedResponse } from '@/types/common'
import * as meetingApi from '@/api/meetings'

export const useMeetingStore = defineStore('meeting', () => {
  const meetings = ref<Meeting[]>([])
  const currentMeeting = ref<Meeting | null>(null)
  const total = ref(0)
  const loading = ref(false)

  async function fetchMeetings(params?: { page?: number; size?: number; keyword?: string; status?: string; tag?: string }) {
    loading.value = true
    try {
      const { data } = await meetingApi.getMeetings(params)
      meetings.value = data.items
      total.value = data.total
    } finally {
      loading.value = false
    }
  }

  async function fetchMeeting(id: string) {
    const { data } = await meetingApi.getMeeting(id)
    currentMeeting.value = data
  }

  return { meetings, currentMeeting, total, loading, fetchMeetings, fetchMeeting }
})
```

### 9.2 `stores/transcript.ts`

```typescript
import { defineStore } from 'pinia'
import { ref } from 'vue'
import type { TranscriptChunk } from '@/types/transcript'
import * as transcriptApi from '@/api/transcripts'

export const useTranscriptStore = defineStore('transcript', () => {
  const chunks = ref<TranscriptChunk[]>([])
  const activeChunkId = ref<string | null>(null)
  const loading = ref(false)

  async function fetchChunks(meetingId: string, params?: { speaker?: string; keyword?: string }) {
    loading.value = true
    try {
      const { data } = await transcriptApi.getTranscripts(meetingId, params)
      chunks.value = data.chunks
    } finally {
      loading.value = false
    }
  }

  function setActiveChunk(chunkId: string) {
    activeChunkId.value = chunkId
  }

  return { chunks, activeChunkId, loading, fetchChunks, setActiveChunk }
})
```

### 9.3 `stores/agent.ts`

```typescript
import { defineStore } from 'pinia'
import { ref } from 'vue'
import type { JobDetail } from '@/types/common'
import type { QAResponse } from '@/types/qa'

export const useAgentStore = defineStore('agent', () => {
  const jobs = ref<JobDetail[]>([])
  const qaHistory = ref<Array<{ question: string; response: QAResponse }>>([])

  function updateJob(job: JobDetail) {
    const idx = jobs.value.findIndex((j) => j.id === job.id)
    if (idx >= 0) jobs.value[idx] = job
    else jobs.value.push(job)
  }

  return { jobs, qaHistory, updateJob }
})
```

---

## 10. Vite 配置要点

```typescript
// vite.config.ts
import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import { resolve } from 'path'

export default defineConfig({
  plugins: [vue()],
  resolve: {
    alias: {
      '@': resolve(__dirname, 'src'),
    },
  },
  server: {
    port: 5173,
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
      '/ws': {
        target: 'ws://localhost:8000',
        ws: true,
      },
    },
  },
})
```

---

## 11. 开发阶段与优先级

### 第一阶段 (MVP)

| 优先级 | 页面/功能 | 涉及 API |
|--------|----------|----------|
| P0 | 会议列表 + 搜索筛选 | `GET /meetings` |
| P0 | 音频上传 + 创建会议 | `POST /meetings/upload` |
| P0 | 会议详情 - 音频播放器 | `GET /meetings/:id` |
| P0 | 会议详情 - 转录展示 | `GET /meetings/:id/transcripts` |
| P0 | 会议详情 - 纪要展示 | `GET /meetings/:id/summary` |
| P0 | 会议详情 - 待办展示 | `GET /meetings/:id/actions` |
| P1 | 待办状态更新 | `PATCH /actions/:id` |
| P1 | 智能问答 (单次) | `POST /qa` |
| P1 | 智能问答 (流式) | `WS /chat` |
| P1 | 任务进度轮询 | `GET /meetings/:id/jobs` |

### 第二阶段

| 优先级 | 页面/功能 | 涉及 API |
|--------|----------|----------|
| P2 | 跨会议语义检索 | `POST /memory/search` |
| P2 | 决策冲突检测 | `GET /meetings/:id/conflicts` |
| P2 | 知识图谱可视化 | `GET /meetings/:id/graph` |
| P2 | 飞书同步 | `POST /actions/:id/sync/feishu` |

### 第三阶段

| 优先级 | 页面/功能 | 说明 |
|--------|----------|------|
| P3 | 图谱查询 | `POST /graph/query` |
| P3 | 转录修正 | `PATCH /transcripts/:chunk_id` |
| P3 | 决策时间线 | 全局决策视图 |
| P3 | 设置页 | 主题/语言/集成配置 |

---

## 12. 关键交互细节

### 12.1 音频上传流程

```
用户拖拽/选择文件
  → 前端校验格式 (mp3/wav/m4a) 和大小
  → FormData { file, title, description?, language?, enable_speaker_diarization? }
  → POST /meetings/upload
  → 返回 202 + job_id
  → 跳转会议详情页
  → 轮询 GET /meetings/:id/jobs 或监听 WS 推送
  → 状态从 transcribing → analyzing → completed
  → 完成后自动加载转录和纪要
```

### 12.2 音文联动流程

```
播放器 timeupdate
  → useAudioSync 计算当前时间对应的 chunk
  → TranscriptList 高亮该 chunk, 滚动到可视区域

点击 TranscriptChunk
  → useAudioSync.seekTo(chunk.start)
  → Waveform 跳转到对应时间点

点击 CitationLink (问答引用)
  → useAudioSync.seekTo(citation.start)
  → TranscriptList 高亮对应 chunk
```

### 12.3 流式问答流程

```
用户输入问题
  → WS /chat 发送 { type: "question", meeting_id, question, scope }
  → 收到 { type: "start" } → 显示 loading
  → 收到 { type: "chunk", message: "..." } → 逐字追加到回答
  → 收到 { type: "end", citations: [...] } → 渲染引用链接
  → 收到 { type: "error" } → 显示错误提示
```

### 12.4 会议状态流转

```
created → uploading → transcribing → analyzing → completed
                                              → failed
```

前端根据 `status` 字段展示不同 UI：
- `created`：显示上传音频入口
- `uploading` / `transcribing` / `analyzing`：显示进度条 + 任务状态
- `completed`：显示完整内容 (转录/纪要/待办)
- `failed`：显示错误信息 + 重试按钮

---

## 13. 环境变量

```bash
# .env.development
VITE_API_BASE_URL=http://localhost:8000
VITE_WS_BASE_URL=ws://localhost:8000

# .env.production
VITE_API_BASE_URL=
VITE_WS_BASE_URL=
```

---

## 14. 代码规范

- 组件使用 `<script setup lang="ts">` + `<template>` + `<style scoped>`
- 文件命名：组件 `PascalCase.vue`，composable `useXxx.ts`，store `xxx.ts`，API `xxx.ts`
- API 返回类型必须显式声明泛型，如 `client.get<Meeting>(...)`
- 所有枚举值与后端保持一致，使用 union type 而非 TS enum
- 优先使用 composables 抽离逻辑，组件只做渲染和事件绑定
- Element Plus 组件按需导入 (配合 `unplugin-vue-components` + `unplugin-auto-import`)
