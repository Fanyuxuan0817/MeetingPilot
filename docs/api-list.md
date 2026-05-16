# MeetingPilot API 接口清单文档

版本：v1.0  
前端：Vue 3 + Vite + Pinia  
后端：FastAPI  
Base URL：`/api/v1`  
默认数据格式：`application/json`  
文件上传格式：`multipart/form-data`

---

## 1. 通用约定

### 1.1 统一分页响应

```json
{
  "items": [],
  "total": 0,
  "page": 1,
  "size": 20
}
```

### 1.2 统一错误响应

```json
{
  "code": "MEETING_NOT_FOUND",
  "message": "会议不存在",
  "details": {}
}
```

### 1.3 状态枚举

会议状态：

```text
created | uploading | transcribing | analyzing | completed | failed
```

待办状态：

```text
todo | doing | done | canceled
```

优先级：

```text
low | medium | high | urgent
```

Agent 任务状态：

```text
pending | running | completed | failed
```

---

## 2. 会议管理接口

### 2.1 创建会议

`POST /meetings`

请求体：

```json
{
  "title": "产品迭代周会",
  "description": "讨论本周产品、研发和测试进度",
  "started_at": "2026-05-16T10:00:00+08:00",
  "tags": ["产品", "周会"]
}
```

响应：

```json
{
  "id": "meet_a7b2c9",
  "title": "产品迭代周会",
  "status": "created",
  "created_at": "2026-05-16T10:00:00+08:00"
}
```

### 2.2 上传会议音频并启动处理

`POST /meetings/upload`

请求格式：`multipart/form-data`

| 参数名 | 类型 | 必填 | 说明 |
| :--- | :--- | :--- | :--- |
| `file` | File | 是 | 音频文件，支持 mp3、wav、m4a |
| `title` | string | 是 | 会议标题 |
| `description` | string | 否 | 会议描述 |
| `language` | string | 否 | 语言，例如 `zh`、`en`，默认自动识别 |
| `enable_speaker_diarization` | boolean | 否 | 是否启用说话人分离，默认 true |

响应：`202 Accepted`

```json
{
  "id": "meet_a7b2c9",
  "title": "产品迭代周会",
  "status": "transcribing",
  "audio_url": "/storage/audio/meet_a7b2c9.mp3",
  "job_id": "job_9x2k1m",
  "created_at": "2026-05-16T10:01:00+08:00"
}
```

### 2.3 获取会议列表

`GET /meetings`

Query 参数：

| 参数名 | 类型 | 必填 | 说明 |
| :--- | :--- | :--- | :--- |
| `page` | int | 否 | 页码，默认 1 |
| `size` | int | 否 | 每页条数，默认 20 |
| `keyword` | string | 否 | 按标题搜索 |
| `status` | string | 否 | 会议状态 |
| `tag` | string | 否 | 标签筛选 |

响应：

```json
{
  "items": [
    {
      "id": "meet_a7b2c9",
      "title": "产品迭代周会",
      "status": "completed",
      "duration": 3600.5,
      "tags": ["产品", "周会"],
      "created_at": "2026-05-16T10:01:00+08:00"
    }
  ],
  "total": 1,
  "page": 1,
  "size": 20
}
```

### 2.4 获取会议详情

`GET /meetings/{meeting_id}`

响应：

```json
{
  "id": "meet_a7b2c9",
  "title": "产品迭代周会",
  "description": "讨论本周产品、研发和测试进度",
  "status": "completed",
  "audio_url": "/storage/audio/meet_a7b2c9.mp3",
  "duration": 3600.5,
  "language": "zh",
  "tags": ["产品", "周会"],
  "created_at": "2026-05-16T10:01:00+08:00",
  "updated_at": "2026-05-16T10:50:00+08:00"
}
```

### 2.5 更新会议信息

`PATCH /meetings/{meeting_id}`

请求体：

```json
{
  "title": "产品迭代周会复盘",
  "description": "补充会议背景",
  "tags": ["产品", "复盘"]
}
```

响应：

```json
{
  "id": "meet_a7b2c9",
  "title": "产品迭代周会复盘",
  "description": "补充会议背景",
  "tags": ["产品", "复盘"],
  "updated_at": "2026-05-16T11:00:00+08:00"
}
```

### 2.6 删除会议

`DELETE /meetings/{meeting_id}`

响应：`204 No Content`

---

## 3. 转录接口

### 3.1 获取转录切片

Vue 侧用于驱动 `TranscriptList.vue`、`Waveform.vue` 和音文联动跳转。

`GET /meetings/{meeting_id}/transcripts`

Query 参数：

| 参数名 | 类型 | 必填 | 说明 |
| :--- | :--- | :--- | :--- |
| `speaker` | string | 否 | 按说话人筛选 |
| `keyword` | string | 否 | 转录文本搜索 |

响应：

```json
{
  "meeting_id": "meet_a7b2c9",
  "chunks": [
    {
      "id": "chunk_1001",
      "speaker": "张三",
      "start": 0.0,
      "end": 4.25,
      "content": "大家好，今天主要对齐一下支付模块的延期问题。",
      "confidence": 0.96
    }
  ]
}
```

### 3.2 获取单个转录切片

`GET /transcripts/{chunk_id}`

响应：

```json
{
  "id": "chunk_1001",
  "meeting_id": "meet_a7b2c9",
  "speaker": "张三",
  "start": 0.0,
  "end": 4.25,
  "content": "大家好，今天主要对齐一下支付模块的延期问题。",
  "confidence": 0.96
}
```

### 3.3 更新转录切片

用于人工修正转录文本或说话人。

`PATCH /transcripts/{chunk_id}`

请求体：

```json
{
  "speaker": "李四",
  "content": "支付模块延期到周五。"
}
```

响应：

```json
{
  "id": "chunk_1001",
  "speaker": "李四",
  "content": "支付模块延期到周五。",
  "updated_at": "2026-05-16T11:10:00+08:00"
}
```

### 3.4 重新转录会议

`POST /meetings/{meeting_id}/transcribe`

请求体：

```json
{
  "language": "zh",
  "enable_speaker_diarization": true
}
```

响应：`202 Accepted`

```json
{
  "meeting_id": "meet_a7b2c9",
  "job_id": "job_8m3p2x",
  "status": "running"
}
```

---

## 4. 结构化纪要接口

### 4.1 获取会议纪要

`GET /meetings/{meeting_id}/summary`

响应：

```json
{
  "meeting_id": "meet_a7b2c9",
  "summary": {
    "overview": "本次会议主要讨论支付模块延期、接口联调和上线时间调整。",
    "topics": [
      {
        "title": "支付模块延期",
        "content": "支付模块由于第三方回调问题延期到周五完成。",
        "source_chunk_ids": ["chunk_1001", "chunk_1002"]
      }
    ],
    "decisions": [
      {
        "topic": "上线时间",
        "decision": "原定周三上线调整为周五上线",
        "source_chunk_ids": ["chunk_1003"]
      }
    ],
    "risks": [
      {
        "title": "第三方回调稳定性",
        "level": "high",
        "description": "若回调问题未解决，会影响支付闭环验证。"
      }
    ],
    "open_questions": [
      "测试环境是否能在周四前稳定复现回调问题？"
    ]
  },
  "generated_at": "2026-05-16T11:20:00+08:00"
}
```

### 4.2 重新生成会议纪要

`POST /meetings/{meeting_id}/summary/generate`

响应：`202 Accepted`

```json
{
  "meeting_id": "meet_a7b2c9",
  "job_id": "job_s7k20d",
  "status": "running"
}
```

---

## 5. 待办事项接口

### 5.1 获取会议待办

`GET /meetings/{meeting_id}/actions`

响应：

```json
{
  "meeting_id": "meet_a7b2c9",
  "items": [
    {
      "id": "act_501",
      "task": "修复支付回调失败问题",
      "owner": "王五",
      "deadline": "2026-05-18",
      "priority": "high",
      "status": "todo",
      "source_chunk_id": "chunk_1001"
    }
  ]
}
```

### 5.2 创建待办

`POST /meetings/{meeting_id}/actions`

请求体：

```json
{
  "task": "补充支付回调异常日志",
  "owner": "王五",
  "deadline": "2026-05-18",
  "priority": "medium",
  "source_chunk_id": "chunk_1001"
}
```

响应：

```json
{
  "id": "act_502",
  "meeting_id": "meet_a7b2c9",
  "task": "补充支付回调异常日志",
  "owner": "王五",
  "deadline": "2026-05-18",
  "priority": "medium",
  "status": "todo"
}
```

### 5.3 更新待办

`PATCH /actions/{action_id}`

请求体：

```json
{
  "task": "补充支付回调异常日志并同步测试",
  "owner": "王五",
  "deadline": "2026-05-19",
  "priority": "high",
  "status": "doing"
}
```

响应：

```json
{
  "id": "act_502",
  "status": "doing",
  "updated_at": "2026-05-16T11:30:00+08:00"
}
```

### 5.4 删除待办

`DELETE /actions/{action_id}`

响应：`204 No Content`

### 5.5 重新提取待办

`POST /meetings/{meeting_id}/actions/extract`

响应：`202 Accepted`

```json
{
  "meeting_id": "meet_a7b2c9",
  "job_id": "job_a2m9p0",
  "status": "running"
}
```

---

## 6. 决策记录接口

### 6.1 获取会议决策

`GET /meetings/{meeting_id}/decisions`

响应：

```json
{
  "meeting_id": "meet_a7b2c9",
  "items": [
    {
      "id": "dec_301",
      "topic": "上线时间",
      "decision": "支付模块延期到周五上线",
      "version": 2,
      "source_chunk_id": "chunk_1003",
      "created_at": "2026-05-16T11:20:00+08:00"
    }
  ]
}
```

### 6.2 获取决策冲突检测结果

`GET /meetings/{meeting_id}/conflicts`

响应：

```json
{
  "meeting_id": "meet_a7b2c9",
  "items": [
    {
      "id": "conf_901",
      "topic": "上线时间",
      "current_decision": "周五上线",
      "previous_decision": "周三上线",
      "level": "medium",
      "description": "本次会议更新了历史上线时间决策。",
      "current_source_chunk_id": "chunk_1003",
      "previous_meeting_id": "meet_b8c1d2"
    }
  ]
}
```

### 6.3 重新检测决策冲突

`POST /meetings/{meeting_id}/conflicts/detect`

响应：`202 Accepted`

```json
{
  "meeting_id": "meet_a7b2c9",
  "job_id": "job_f8q1v6",
  "status": "running"
}
```

---

## 7. 智能问答接口

### 7.1 单次问答

适合普通 HTTP 请求，不需要流式输出时使用。

`POST /qa`

请求体：

```json
{
  "meeting_id": "meet_a7b2c9",
  "question": "支付模块延期是谁提出的？",
  "scope": "current_meeting"
}
```

`scope` 可选值：

```text
current_meeting | all_meetings
```

响应：

```json
{
  "answer": "支付模块延期由张三提出，原因是第三方回调问题尚未解决。",
  "citations": [
    {
      "meeting_id": "meet_a7b2c9",
      "chunk_id": "chunk_1001",
      "speaker": "张三",
      "start": 121.0,
      "end": 136.0,
      "text": "支付模块延期到周五。"
    }
  ]
}
```

### 7.2 流式问答 WebSocket

适合 Vue 聊天窗口逐字输出，连接后由前端发送问题。

`WS /chat`

前端发送：

```json
{
  "type": "question",
  "meeting_id": "meet_a7b2c9",
  "question": "支付模块延期是谁提出的？",
  "scope": "current_meeting"
}
```

后端推送：

```json
{ "type": "start", "message": "" }
```

```json
{ "type": "chunk", "message": "支付模块延期" }
```

```json
{
  "type": "end",
  "message": "",
  "citations": [
    {
      "meeting_id": "meet_a7b2c9",
      "chunk_id": "chunk_1001",
      "speaker": "张三",
      "start": 121.0,
      "end": 136.0,
      "text": "支付模块延期到周五。"
    }
  ]
}
```

错误推送：

```json
{
  "type": "error",
  "code": "QA_FAILED",
  "message": "问答生成失败"
}
```

---

## 8. Agent 任务接口

### 8.1 获取会议分析任务状态

Vue 可用该接口轮询处理进度，也可以配合 WebSocket 状态推送。

`GET /meetings/{meeting_id}/jobs`

响应：

```json
{
  "meeting_id": "meet_a7b2c9",
  "jobs": [
    {
      "id": "job_9x2k1m",
      "type": "transcription",
      "status": "completed",
      "progress": 100,
      "message": "转录完成"
    },
    {
      "id": "job_s7k20d",
      "type": "summary",
      "status": "running",
      "progress": 60,
      "message": "正在生成结构化纪要"
    }
  ]
}
```

### 8.2 手动触发完整 Agent 分析

`POST /meetings/{meeting_id}/agents/run`

请求体：

```json
{
  "agents": ["summary", "action", "memory", "graph", "conflict"]
}
```

响应：`202 Accepted`

```json
{
  "meeting_id": "meet_a7b2c9",
  "job_id": "job_agent_001",
  "status": "running"
}
```

### 8.3 WebSocket 会议处理状态推送

`WS /meetings/{meeting_id}/events`

后端推送：

```json
{
  "type": "job_progress",
  "job_id": "job_s7k20d",
  "job_type": "summary",
  "status": "running",
  "progress": 60,
  "message": "正在生成结构化纪要"
}
```

---

## 9. 历史记忆与检索接口

### 9.1 跨会议语义检索

`POST /memory/search`

请求体：

```json
{
  "query": "支付模块延期之前讨论过吗？",
  "limit": 5,
  "filters": {
    "project": "支付系统"
  }
}
```

响应：

```json
{
  "items": [
    {
      "meeting_id": "meet_b8c1d2",
      "meeting_title": "支付系统技术评审",
      "chunk_id": "chunk_8801",
      "speaker": "李四",
      "start": 230.0,
      "end": 245.0,
      "text": "支付回调存在偶发失败，需要延期排查。",
      "score": 0.89
    }
  ]
}
```

---

## 10. 知识图谱接口

### 10.1 获取会议知识图谱

`GET /meetings/{meeting_id}/graph`

响应：

```json
{
  "nodes": [
    {
      "id": "person_zhangsan",
      "label": "张三",
      "type": "person"
    },
    {
      "id": "task_payment_callback",
      "label": "修复支付回调",
      "type": "task"
    }
  ],
  "edges": [
    {
      "source": "person_zhangsan",
      "target": "task_payment_callback",
      "type": "负责"
    }
  ]
}
```

### 10.2 图谱查询

`POST /graph/query`

请求体：

```json
{
  "question": "最近三次会议张三负责了哪些任务？"
}
```

响应：

```json
{
  "answer": "最近三次会议中，张三负责支付回调修复、接口联调和上线风险确认。",
  "nodes": [],
  "edges": []
}
```

---

## 11. 第三方执行接口

### 11.1 同步待办到飞书

`POST /actions/{action_id}/sync/feishu`

请求体：

```json
{
  "target": "task",
  "notify_owner": true
}
```

响应：

```json
{
  "action_id": "act_501",
  "provider": "feishu",
  "external_id": "feishu_task_123",
  "status": "synced",
  "synced_at": "2026-05-16T11:40:00+08:00"
}
```

### 11.2 获取第三方同步状态

`GET /integrations/sync-records`

Query 参数：

| 参数名 | 类型 | 必填 | 说明 |
| :--- | :--- | :--- | :--- |
| `provider` | string | 否 | 例如 `feishu` |
| `meeting_id` | string | 否 | 会议 ID |

响应：

```json
{
  "items": [
    {
      "id": "sync_001",
      "provider": "feishu",
      "resource_type": "action",
      "resource_id": "act_501",
      "external_id": "feishu_task_123",
      "status": "synced",
      "created_at": "2026-05-16T11:40:00+08:00"
    }
  ]
}
```

---

## 12. MVP 优先级

第一阶段必须实现：

| 优先级 | 接口 |
| --- | --- |
| P0 | `POST /meetings/upload` |
| P0 | `GET /meetings` |
| P0 | `GET /meetings/{meeting_id}` |
| P0 | `GET /meetings/{meeting_id}/transcripts` |
| P0 | `GET /meetings/{meeting_id}/summary` |
| P0 | `GET /meetings/{meeting_id}/actions` |
| P1 | `PATCH /actions/{action_id}` |
| P1 | `POST /qa` |
| P1 | `WS /chat` |
| P1 | `GET /meetings/{meeting_id}/jobs` |

第二阶段再实现：

| 优先级 | 接口 |
| --- | --- |
| P2 | `POST /memory/search` |
| P2 | `GET /meetings/{meeting_id}/conflicts` |
| P2 | `GET /meetings/{meeting_id}/graph` |
| P2 | `POST /actions/{action_id}/sync/feishu` |
