# MeetingPilot 前端状态管理与逻辑复用清单

> 本文档基于 `docs/Pinia.md` 的三层架构理念与 `docs/menu.md` 的目录规划，结合项目现有代码（types、api、router）梳理而出。
> 目的：为后续开发提供明确的 Store / Composable 实现路线图，避免遗漏或重复建设。

---

## 一、架构原则速览

| 层级 | 职责 | 文件位置 | 依赖方向 |
|------|------|----------|----------|
| **Pinia Store** | 持有跨组件/跨页面共享的响应式状态 | `src/stores/*.ts` | 调用 `api/` |
| **Composable** | 封装可复用的复杂交互逻辑（第三方库、轮询、WebSocket 等） | `src/composables/*.ts` | 调用 `stores/` 或 `api/` |
| **UI Component** | 纯展示 + 事件绑定，不包含业务逻辑 | `src/components/` + `src/views/` | 调用 `stores/` 和 `composables/` |

数据流向：**API → Store → Component**（单向）

---

## 二、Pinia Store 状态清单

### 2.1 `useMeetingStore` — 会议核心状态

| 类别 | 名称 | 类型 | 说明 | 数据来源 |
|------|------|------|------|----------|
| State | `meetings` | `MeetingRead[]` | 会议列表（Dashboard 页） | `listMeetings()` |
| State | `currentMeeting` | `MeetingRead \| null` | 当前查看的会议详情 | `getMeeting()` |
| State | `transcripts` | `TranscriptChunkRead[]` | 当前会议的转录切片 | `getMeetingTranscripts()` |
| State | `currentTime` | `number` | 全局同步的音频播放进度（秒） | 音频播放器回调 |
| State | `isLoading` | `boolean` | 数据加载中标记 | — |
| State | `pagination` | `{ total, page, size }` | 列表分页信息 | `listMeetings()` 响应 |
| State | `filters` | `ListMeetingsParams` | 列表筛选条件（关键词、状态、标签） | 用户交互 |
| Action | `loadMeetings()` | — | 加载会议列表（带分页/筛选） | `api/meetings` |
| Action | `loadMeetingData(id)` | — | 并发加载会议详情 + 转录内容 | `api/meetings` |
| Action | `uploadMeeting(params)` | — | 上传录音并返回 Job | `api/meetings` |
| Action | `deleteMeeting(id)` | — | 删除会议 | `api/meetings` |
| Action | `updateCurrentTime(t)` | — | 更新全局播放进度 | 音频播放器 |
| Action | `setFilters(f)` | — | 更新筛选条件并重新加载列表 | 用户交互 |
| Getter | `meetingCount` | `number` | 会议总数 | `pagination.total` |
| Getter | `activeFilters` | `boolean` | 是否有筛选条件激活 | `filters` |

**对应类型**：`MeetingRead`, `MeetingStatus`, `TranscriptChunkRead`, `PaginationResponse`, `ListMeetingsParams`（来自 `@/types`）

---

### 2.2 `useAgentStore` — AI Agent 状态

| 类别 | 名称 | 类型 | 说明 | 数据来源 |
|------|------|------|------|----------|
| State | `summary` | `SummaryRead \| null` | 当前会议的结构化纪要 | `getMeetingSummary()` |
| State | `actions` | `ActionItemRead[]` | 当前会议的待办事项 | `getMeetingActions()` |
| State | `decisions` | `DecisionRead[]` | 当前会议的决策记录 | `getMeetingDecisions()` |
| State | `conflicts` | `DecisionConflictRead[]` | 跨会议决策冲突 | `getMeetingConflicts()` |
| State | `chatMessages` | `ChatMessage[]` | 问答对话历史 | WebSocket / REST |
| State | `isStreaming` | `boolean` | AI 是否正在流式输出 | WebSocket 状态 |
| State | `agentJobs` | `MeetingJobItem[]` | 当前会议的 Agent 任务进度 | `getMeetingJobs()` |
| Action | `loadSummary(meetingId)` | — | 加载纪要 | `api/summaries` |
| Action | `generateSummary(meetingId)` | — | 触发纪要生成 | `api/summaries` |
| Action | `loadActions(meetingId)` | — | 加载待办 | `api/actions` |
| Action | `extractActions(meetingId)` | — | 触发待办提取 | `api/actions` |
| Action | `updateAction(id, data)` | — | 更新待办状态 | `api/actions` |
| Action | `syncToFeishu(actionId, params)` | — | 同步待办到飞书 | `api/actions` |
| Action | `loadDecisions(meetingId)` | — | 加载决策 | `api/decisions` |
| Action | `detectConflicts(meetingId)` | — | 触发冲突检测 | `api/decisions` |
| Action | `runAgents(meetingId, agents?)` | — | 触发指定 Agent 编排 | `api/meetings` |
| Action | `sendQuestion(question, meetingId?, scope?)` | — | 发送问答请求 | WebSocket |
| Action | `appendChatMessage(msg)` | — | 追加对话消息 | WebSocket 回调 |
| Getter | `hasConflicts` | `boolean` | 是否存在决策冲突 | `conflicts.length > 0` |
| Getter | `pendingActions` | `ActionItemRead[]` | 未完成的待办 | `actions.filter` |

**自定义类型补充**（需在 `types/` 中新增）：

```typescript
interface ChatMessage {
  id: string
  role: 'user' | 'assistant'
  content: string
  citations?: Citation[]
  timestamp: number
}
```

---

### 2.3 `useUserStore` — 用户与认证状态

| 类别 | 名称 | 类型 | 说明 | 数据来源 |
|------|------|------|------|----------|
| State | `token` | `string \| null` | JWT Token | localStorage / 登录接口 |
| State | `user` | `UserInfo \| null` | 当前用户信息 | 登录接口 |
| State | `isLoggedIn` | `boolean` | 登录状态 | `!!token` |
| Action | `login(credentials)` | — | 登录并存储 Token | 登录 API |
| Action | `logout()` | — | 清除 Token 并跳转 | — |
| Action | `loadProfile()` | — | 加载用户信息 | 用户 API |
| Getter | `displayName` | `string` | 用户显示名 | `user?.name` |

> 注：当前后端 API 暂未提供用户模块，此 Store 为预留设计，待后端 auth 接口就绪后实现。

---

### 2.4 Store 依赖关系图

```
useUserStore (独立，仅被路由守卫和 Navbar 消费)
     │
useMeetingStore (核心，被 Dashboard / MeetingDetail 消费)
     │
useAgentStore (依赖 MeetingStore.currentMeeting.id 加载数据)
```

---

## 三、Composable 逻辑复用清单

### 3.1 `useAudioPlayer` — 音频播放控制

| 导出 | 类型 | 说明 |
|------|------|------|
| `initPlayer(container, audioUrl)` | `function` | 初始化 WaveSurfer.js 波形图并绑定容器 |
| `playPause()` | `function` | 播放/暂停切换 |
| `seekTo(time)` | `function` | 跳转到指定时间（秒） |
| `currentTime` | `Ref<number>` | 当前播放时间（响应式） |
| `duration` | `Ref<number>` | 音频总时长 |
| `isPlaying` | `Ref<boolean>` | 是否正在播放 |
| `destroy()` | `function` | 销毁实例，释放资源 |

**核心逻辑**：
- 初始化 WaveSurfer 实例，配置波形颜色（可爱风配色）
- 监听 `timeupdate` 事件，同步到 `useMeetingStore.updateCurrentTime()`
- 组件卸载时自动调用 `destroy()` 防止内存泄漏

**依赖**：`wavesurfer.js`、`useMeetingStore`

---

### 3.2 `useWebSocket` — WebSocket 流式通信

| 导出 | 类型 | 说明 |
|------|------|------|
| `connect(type, meetingId?)` | `function` | 建立连接（`'chat'` 或 `'events'`） |
| `send(data)` | `function` | 发送消息 |
| `disconnect()` | `function` | 主动断开连接 |
| `isConnected` | `Ref<boolean>` | 连接状态 |
| `lastMessage` | `Ref<WSMessage \| null>` | 最近收到的消息 |

**核心逻辑**：
- 封装 `api/chat.ts` 中的 `createChatWebSocket` 和 `createMeetingEventsWebSocket`
- 自动重连机制（指数退避，最多 3 次）
- 心跳保活（`MeetingEvents` 类型的 WebSocket 需定期 `sendPing`）
- 组件卸载时自动 `disconnect()`

**依赖**：`api/chat.ts`、`useAgentStore`（将收到的消息追加到 `chatMessages`）

---

### 3.3 `useTaskPolling` — 任务状态轮询

| 导出 | 类型 | 说明 |
|------|------|------|
| `startPolling(callback, interval?)` | `function` | 启动轮询，callback 返回 `true` 时自动停止 |
| `stopPolling()` | `function` | 手动停止轮询 |
| `isPolling` | `Ref<boolean>` | 是否正在轮询 |

**核心逻辑**：
- 使用 `setInterval` 定期调用回调
- 回调返回 `true` 表示任务完成，自动停止
- `onUnmounted` 自动清理，防止内存泄漏
- 默认间隔 3000ms

**依赖**：无外部依赖，纯逻辑封装

**使用场景**：
- 会议上传后轮询转录进度 → `getMeetingJobs()`
- Agent 编排后轮询任务状态 → `getMeetingJobs()`

---

### 3.4 `useTranscriptHighlight` — 转录文本高亮联动

| 导出 | 类型 | 说明 |
|------|------|------|
| `activeChunkId` | `Ref<string \| null>` | 当前高亮的转录切片 ID |
| `highlightChunk(chunkId)` | `function` | 高亮指定切片并滚动到视口 |
| `syncWithAudio(currentTime)` | `function` | 根据播放时间自动切换高亮切片 |

**核心逻辑**：
- 监听 `useMeetingStore.currentTime`，根据时间匹配对应的 `TranscriptChunk`
- 高亮切换时自动滚动到可视区域（`scrollIntoView({ behavior: 'smooth' })`）
- 点击切片时反向控制音频跳转（调用 `useAudioPlayer.seekTo()`）

**依赖**：`useMeetingStore`（读取 `transcripts` 和 `currentTime`）

---

### 3.5 `useMeetingUpload` — 会议上传流程

| 导出 | 类型 | 说明 |
|------|------|------|
| `upload(file, metadata)` | `function` | 执行上传并启动轮询 |
| `uploadProgress` | `Ref<number>` | 上传进度百分比 |
| `isUploading` | `Ref<boolean>` | 是否正在上传 |
| `uploadError` | `Ref<string \| null>` | 上传错误信息 |

**核心逻辑**：
- 调用 `uploadMeeting()` API
- 上传成功后自动启动 `useTaskPolling` 轮询转录进度
- 轮询完成后更新 `useMeetingStore` 中的会议状态

**依赖**：`api/meetings`、`useMeetingStore`、`useTaskPolling`

---

## 四、Store ↔ Composable ↔ View 映射表

| 页面视图 | 消费的 Store | 消费的 Composable |
|----------|-------------|-------------------|
| `Dashboard.vue` | `useMeetingStore` | `useMeetingUpload` |
| `MeetingDetail.vue` | `useMeetingStore` + `useAgentStore` | `useAudioPlayer` + `useTranscriptHighlight` + `useTaskPolling` + `useWebSocket` |
| `Settings.vue` | `useUserStore` | — |

---

## 五、现有代码与清单对照

| 清单项 | 文件路径 | 当前状态 | 依赖的 Types | 依赖的 API |
|--------|----------|----------|-------------|-----------|
| `useMeetingStore` | `src/stores/meeting.ts` | ❌ 待建 | `MeetingRead`, `TranscriptChunkRead`, `PaginationResponse` | `meetings.ts`, `transcripts.ts` |
| `useAgentStore` | `src/stores/agent.ts` | ❌ 待建 | `SummaryRead`, `ActionItemRead`, `DecisionRead`, `DecisionConflictRead`, `ChatMessage`(新增) | `summaries.ts`, `actions.ts`, `decisions.ts`, `chat.ts` |
| `useUserStore` | `src/stores/user.ts` | ❌ 待建（后端未就绪） | `UserInfo`(新增) | 待定 |
| `useAudioPlayer` | `src/composables/useAudioPlayer.ts` | ❌ 待建 | — | — |
| `useWebSocket` | `src/composables/useWebSocket.ts` | ❌ 待建 | `WSMessage`, `Citation` | `chat.ts` |
| `useTaskPolling` | `src/composables/useTaskPolling.ts` | ❌ 待建 | — | — |
| `useTranscriptHighlight` | `src/composables/useTranscriptHighlight.ts` | ❌ 待建 | `TranscriptChunkRead` | — |
| `useMeetingUpload` | `src/composables/useMeetingUpload.ts` | ❌ 待建 | `UploadMeetingParams`, `JobResponse` | `meetings.ts` |

> ✅ 已就绪的基础设施：`types/`（7 个类型文件）、`api/`（7 个接口文件 + client 封装）、`chat.ts`（WebSocket 封装）

---

## 六、实现优先级建议

| 优先级 | Store / Composable | 理由 |
|--------|-------------------|------|
| P0 | `useMeetingStore` | 核心数据流，Dashboard 和 MeetingDetail 都依赖 |
| P0 | `useTaskPolling` | 独立纯逻辑，无外部依赖，可立即实现 |
| P0 | `useAudioPlayer` | MeetingDetail 核心交互，WaveSurfer.js 已在依赖中 |
| P1 | `useAgentStore` | MeetingDetail 右栏 AI 功能依赖 |
| P1 | `useWebSocket` | 问答流式对话依赖，需与 AgentStore 协同 |
| P1 | `useTranscriptHighlight` | 音频-转录联动核心体验 |
| P2 | `useMeetingUpload` | Dashboard 上传流程，可延后 |
| P2 | `useUserStore` | 后端 auth 接口未就绪，暂缓 |
