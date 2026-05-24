# MeetingPilot 数据库表设计文档

基于 `backend/app/schemas/` 数据契约与 `docs/PRD.md` 业务需求设计

---

# 目录

1. [设计原则](#1-设计原则)
2. [存储架构总览](#2-存储架构总览)
3. [PostgreSQL 关系型表](#3-postgresql-关系型表)
4. [pgvector 向量存储](#4-pgvector-向量存储)
5. [Neo4j 图数据库](#5-neo4j-图数据库)
6. [ER 关系图](#6-er-关系图)
7. [索引策略](#7-索引策略)
8. [数据契约映射](#8-数据契约映射)

---

# 1. 设计原则

| 原则 | 说明 |
|------|------|
| 契约驱动 | 所有字段来源于 Pydantic Schema 定义，确保 API 与存储一致 |
| 双库协同 | PostgreSQL + pgvector 存结构化数据与语义向量，Neo4j 存关系图谱 |
| 主键统一 | 全部使用 UUID v4，便于分布式生成与跨系统关联 |
| 向量内聚 | 使用 pgvector 将向量嵌入与业务数据同库存储，避免跨库数据同步，支持向量-标量联合查询 |
| 软删除优先 | 核心业务表预留 `deleted_at` 字段，避免物理删除导致关联断裂 |
| 枚举约束 | 使用 PostgreSQL ENUM TYPE 确保状态字段取值合法 |

---

# 2. 存储架构总览

```text
┌──────────────────────────────────────────────────────────────┐
│                        应用层                                 │
└──────────┬───────────────────────┬───────────────────────────┘
           │                       │
           ▼                       ▼
┌─────────────────────────────────┐  ┌─────────────────────┐
│   PostgreSQL + pgvector         │  │     Neo4j           │
│                                 │  │                     │
│  · meeting                      │  │  · Person 节点      │
│  · meeting_tag                  │  │  · Project 节点     │
│  · transcript_chunk + embedding │  │  · Task 节点        │
│  · action_item                  │  │  · Decision 节点    │
│  · decision_record              │  │  · Risk 节点        │
│  · decision_conflict            │  │  · 关系边           │
│  · summary + embedding          │  └─────────────────────┘
│  · summary_topic                │
│  · summary_decision             │
│  · summary_risk                 │
│  · summary_open_question        │
│  · job                          │
│  · qa_history + embedding       │
│  · qa_citation                  │
└─────────────────────────────────┘
```

---

# 3. PostgreSQL 关系型表

## 3.1 ENUM 类型定义

```sql
CREATE TYPE meeting_status AS ENUM (
    'created', 'uploading', 'transcribing', 'analyzing', 'completed', 'failed'
);

CREATE TYPE action_status AS ENUM (
    'todo', 'doing', 'done', 'canceled'
);

CREATE TYPE priority_level AS ENUM (
    'low', 'medium', 'high', 'urgent'
);

CREATE TYPE conflict_level AS ENUM (
    'low', 'medium', 'high'
);

CREATE TYPE risk_level AS ENUM (
    'low', 'medium', 'high'
);

CREATE TYPE job_status AS ENUM (
    'pending', 'running', 'completed', 'failed'
);

CREATE TYPE qa_scope AS ENUM (
    'current_meeting', 'all_meetings'
);
```

> **来源映射**：`meeting_status` ← [meeting.py](../backend/app/schemas/meeting.py) `MeetingStatus`；`action_status` / `priority_level` ← [action_item.py](../backend/app/schemas/action_item.py) `ActionStatus` / `Priority`；`conflict_level` ← [decision.py](../backend/app/schemas/decision.py) `ConflictLevel`；`risk_level` ← [summary.py](../backend/app/schemas/summary.py) `RiskLevel`；`job_status` ← [common.py](../backend/app/schemas/common.py) `JobStatus`；`qa_scope` ← [qa.py](../backend/app/schemas/qa.py) `QARequest.scope`

---

## 3.2 meeting — 会议主表

> **来源**：[meeting.py](../backend/app/schemas/meeting.py) `MeetingRead`

```sql
CREATE TABLE meeting (
    id          UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    title       VARCHAR(200) NOT NULL,
    description TEXT,
    status      meeting_status NOT NULL DEFAULT 'created',
    duration    DOUBLE PRECISION DEFAULT 0.0,
    audio_url   VARCHAR(500),
    language    VARCHAR(10),
    started_at  TIMESTAMPTZ NOT NULL,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at  TIMESTAMPTZ,
    deleted_at  TIMESTAMPTZ
);
```

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | UUID | PK | 会议唯一标识 |
| title | VARCHAR(200) | NOT NULL | 会议标题，对应 `MeetingBase.title` |
| description | TEXT | | 会议描述，对应 `MeetingBase.description` |
| status | meeting_status | NOT NULL DEFAULT 'created' | 会议生命周期状态 |
| duration | DOUBLE PRECISION | DEFAULT 0.0 | 音频时长（秒），对应 `MeetingRead.duration` |
| audio_url | VARCHAR(500) | | 音频文件存储路径，对应 `MeetingRead.audio_url` |
| language | VARCHAR(10) | | 音频语言代码，对应 `MeetingRead.language` |
| started_at | TIMESTAMPTZ | NOT NULL | 会议开始时间，对应 `MeetingCreate.started_at` |
| created_at | TIMESTAMPTZ | NOT NULL DEFAULT NOW() | 记录创建时间 |
| updated_at | TIMESTAMPTZ | | 记录更新时间，对应 `MeetingRead.updated_at` |
| deleted_at | TIMESTAMPTZ | | 软删除标记 |

---

## 3.3 meeting_tag — 会议标签

> **来源**：[meeting.py](../backend/app/schemas/meeting.py) `MeetingBase.tags`

```sql
CREATE TABLE meeting_tag (
    id          UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    meeting_id  UUID        NOT NULL REFERENCES meeting(id) ON DELETE CASCADE,
    tag         VARCHAR(50) NOT NULL,
    UNIQUE(meeting_id, tag)
);
```

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | UUID | PK | 标签记录 ID |
| meeting_id | UUID | FK → meeting(id) CASCADE | 所属会议 |
| tag | VARCHAR(50) | NOT NULL | 标签内容 |

> **设计说明**：Schema 中 `tags: list[str]` 为数组类型，此处拆分为独立表实现多值存储，联合唯一约束 `(meeting_id, tag)` 防止重复标签。

---

## 3.4 transcript_chunk — 转录切片

> **来源**：[transcript.py](../backend/app/schemas/transcript.py) `TranscriptChunkRead`

```sql
CREATE TABLE transcript_chunk (
    id          UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    meeting_id  UUID        NOT NULL REFERENCES meeting(id) ON DELETE CASCADE,
    speaker     VARCHAR(100) NOT NULL,
    content     TEXT        NOT NULL,
    start       DOUBLE PRECISION NOT NULL CHECK (start >= 0),
    end         DOUBLE PRECISION NOT NULL CHECK (end >= 0),
    confidence  DOUBLE PRECISION CHECK (confidence >= 0 AND confidence <= 1),
    embedding   vector(1536),
    created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at  TIMESTAMPTZ,
    deleted_at  TIMESTAMPTZ
);
```

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | UUID | PK | 切片唯一标识 |
| meeting_id | UUID | FK → meeting(id) CASCADE | 所属会议 |
| speaker | VARCHAR(100) | NOT NULL | 说话人名称，对应 `TranscriptChunkBase.speaker` |
| content | TEXT | NOT NULL | 转录文本内容 |
| start | DOUBLE PRECISION | NOT NULL, ≥ 0 | 片段起始时间（秒） |
| end | DOUBLE PRECISION | NOT NULL, ≥ 0 | 片段结束时间（秒） |
| confidence | DOUBLE PRECISION | 0~1 | 转录置信度，对应 `TranscriptChunkRead.confidence` |
| embedding | vector(1536) | | 文本语义向量，由 Embedding 模型生成 |
| created_at | TIMESTAMPTZ | NOT NULL DEFAULT NOW() | 记录创建时间 |
| updated_at | TIMESTAMPTZ | | 记录更新时间 |
| deleted_at | TIMESTAMPTZ | | 软删除标记 |

> **PRD 对应**：§4.2 转录模块 — 支持时间戳、说话人分离、多语言输出。

---

## 3.5 action_item — 待办事项

> **来源**：[action_item.py](../backend/app/schemas/action_item.py) `ActionItemRead`

```sql
CREATE TABLE action_item (
    id              UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    meeting_id      UUID        NOT NULL REFERENCES meeting(id) ON DELETE CASCADE,
    task            TEXT        NOT NULL,
    owner           VARCHAR(100) NOT NULL,
    deadline        DATE,
    priority        priority_level NOT NULL DEFAULT 'medium',
    status          action_status NOT NULL DEFAULT 'todo',
    source_chunk_id UUID        REFERENCES transcript_chunk(id) ON DELETE SET NULL,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ,
    deleted_at      TIMESTAMPTZ
);
```

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | UUID | PK | 待办唯一标识 |
| meeting_id | UUID | FK → meeting(id) CASCADE | 所属会议 |
| task | TEXT | NOT NULL | 任务描述 |
| owner | VARCHAR(100) | NOT NULL | 负责人 |
| deadline | DATE | | 截止日期 |
| priority | priority_level | NOT NULL DEFAULT 'medium' | 优先级 |
| status | action_status | NOT NULL DEFAULT 'todo' | 执行状态 |
| source_chunk_id | UUID | FK → transcript_chunk(id) SET NULL | 来源转录片段 |
| created_at | TIMESTAMPTZ | NOT NULL DEFAULT NOW() | 记录创建时间 |
| updated_at | TIMESTAMPTZ | | 记录更新时间 |
| deleted_at | TIMESTAMPTZ | | 软删除标记 |

> **PRD 对应**：§4.5 待办提取模块 — 自动抽取任务、负责人、截止时间、优先级、来源片段。

---

## 3.6 decision_record — 决策记录

> **来源**：[decision.py](../backend/app/schemas/decision.py) `DecisionRead`

```sql
CREATE TABLE decision_record (
    id              UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    meeting_id      UUID        NOT NULL REFERENCES meeting(id) ON DELETE CASCADE,
    topic           TEXT        NOT NULL,
    decision        TEXT        NOT NULL,
    version         INTEGER     NOT NULL DEFAULT 1,
    source_chunk_id UUID        NOT NULL REFERENCES transcript_chunk(id) ON DELETE RESTRICT,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
```

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | UUID | PK | 决策唯一标识 |
| meeting_id | UUID | FK → meeting(id) CASCADE | 所属会议 |
| topic | TEXT | NOT NULL | 决策主题 |
| decision | TEXT | NOT NULL | 决策内容 |
| version | INTEGER | NOT NULL DEFAULT 1 | 决策版本号，用于追踪变更 |
| source_chunk_id | UUID | FK → transcript_chunk(id) RESTRICT | 来源转录片段，RESTRICT 防止误删 |
| created_at | TIMESTAMPTZ | NOT NULL DEFAULT NOW() | 记录创建时间 |

> **PRD 对应**：§4.7 决策冲突检测模块 — 通过 `version` 字段实现决策版本追踪，支持跨会议决策变更检测。

---

## 3.7 decision_conflict — 决策冲突

> **来源**：[decision.py](../backend/app/schemas/decision.py) `DecisionConflictRead`

```sql
CREATE TABLE decision_conflict (
    id                      UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    topic                   TEXT        NOT NULL,
    current_decision        TEXT        NOT NULL,
    previous_decision       TEXT        NOT NULL,
    level                   conflict_level NOT NULL,
    description             TEXT        NOT NULL,
    current_source_chunk_id UUID        NOT NULL REFERENCES transcript_chunk(id) ON DELETE RESTRICT,
    previous_meeting_id     UUID        NOT NULL REFERENCES meeting(id) ON DELETE CASCADE,
    created_at              TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
```

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | UUID | PK | 冲突记录 ID |
| topic | TEXT | NOT NULL | 冲突主题 |
| current_decision | TEXT | NOT NULL | 当前决策内容 |
| previous_decision | TEXT | NOT NULL | 之前决策内容 |
| level | conflict_level | NOT NULL | 冲突等级 |
| description | TEXT | NOT NULL | 冲突描述 |
| current_source_chunk_id | UUID | FK → transcript_chunk(id) RESTRICT | 当前决策来源片段 |
| previous_meeting_id | UUID | FK → meeting(id) CASCADE | 之前决策所在会议 |
| created_at | TIMESTAMPTZ | NOT NULL DEFAULT NOW() | 记录创建时间 |

> **PRD 对应**：§4.7 — 识别历史决策变化，如"上次周三上线 → 本次周五上线"。

---

## 3.8 summary — 会议纪要

> **来源**：[summary.py](../backend/app/schemas/summary.py) `SummaryRead`

```sql
CREATE TABLE summary (
    id              UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    meeting_id      UUID        NOT NULL UNIQUE REFERENCES meeting(id) ON DELETE CASCADE,
    overview        TEXT        NOT NULL,
    embedding       vector(1536),
    generated_at    TIMESTAMPTZ NOT NULL
);
```

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | UUID | PK | 纪要唯一标识 |
| meeting_id | UUID | FK → meeting(id) CASCADE, UNIQUE | 一对一关联会议 |
| overview | TEXT | NOT NULL | 会议概览，对应 `SummaryDetail.overview` |
| embedding | vector(1536) | | 纪要概览语义向量，用于跨会议摘要检索 |
| generated_at | TIMESTAMPTZ | NOT NULL | 纪要生成时间 |

---

## 3.9 summary_topic — 纪要议题

> **来源**：[summary.py](../backend/app/schemas/summary.py) `Topic`

```sql
CREATE TABLE summary_topic (
    id          UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    summary_id  UUID        NOT NULL REFERENCES summary(id) ON DELETE CASCADE,
    title       VARCHAR(200) NOT NULL,
    content     TEXT        NOT NULL,
    sort_order  INTEGER     NOT NULL DEFAULT 0
);
```

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | UUID | PK | 议题 ID |
| summary_id | UUID | FK → summary(id) CASCADE | 所属纪要 |
| title | VARCHAR(200) | NOT NULL | 议题标题 |
| content | TEXT | NOT NULL | 议题内容 |
| sort_order | INTEGER | NOT NULL DEFAULT 0 | 排序序号，保持议题顺序 |

---

## 3.10 summary_topic_source — 议题来源关联

> **来源**：[summary.py](../backend/app/schemas/summary.py) `Topic.source_chunk_ids`

```sql
CREATE TABLE summary_topic_source (
    summary_topic_id UUID NOT NULL REFERENCES summary_topic(id) ON DELETE CASCADE,
    chunk_id         UUID NOT NULL REFERENCES transcript_chunk(id) ON DELETE CASCADE,
    PRIMARY KEY (summary_topic_id, chunk_id)
);
```

> **设计说明**：Schema 中 `source_chunk_ids: list[str]` 为数组类型，此处拆分为 M:N 关联表。

---

## 3.11 summary_decision — 纪要决策

> **来源**：[summary.py](../backend/app/schemas/summary.py) `DecisionShort`

```sql
CREATE TABLE summary_decision (
    id          UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    summary_id  UUID        NOT NULL REFERENCES summary(id) ON DELETE CASCADE,
    topic       VARCHAR(200) NOT NULL,
    decision    TEXT        NOT NULL,
    sort_order  INTEGER     NOT NULL DEFAULT 0
);
```

---

## 3.12 summary_decision_source — 纪要决策来源关联

> **来源**：[summary.py](../backend/app/schemas/summary.py) `DecisionShort.source_chunk_ids`

```sql
CREATE TABLE summary_decision_source (
    summary_decision_id UUID NOT NULL REFERENCES summary_decision(id) ON DELETE CASCADE,
    chunk_id            UUID NOT NULL REFERENCES transcript_chunk(id) ON DELETE CASCADE,
    PRIMARY KEY (summary_decision_id, chunk_id)
);
```

---

## 3.13 summary_risk — 纪要风险

> **来源**：[summary.py](../backend/app/schemas/summary.py) `Risk`

```sql
CREATE TABLE summary_risk (
    id          UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    summary_id  UUID        NOT NULL REFERENCES summary(id) ON DELETE CASCADE,
    title       VARCHAR(200) NOT NULL,
    level       risk_level  NOT NULL,
    description TEXT        NOT NULL,
    sort_order  INTEGER     NOT NULL DEFAULT 0
);
```

---

## 3.14 summary_open_question — 纪要未决问题

> **来源**：[summary.py](../backend/app/schemas/summary.py) `SummaryDetail.open_questions`

```sql
CREATE TABLE summary_open_question (
    id          UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    summary_id  UUID        NOT NULL REFERENCES summary(id) ON DELETE CASCADE,
    question    TEXT        NOT NULL,
    sort_order  INTEGER     NOT NULL DEFAULT 0
);
```

---

## 3.15 job — 异步任务

> **来源**：[common.py](../backend/app/schemas/common.py) `JobResponse`

```sql
CREATE TABLE job (
    id          UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    meeting_id  UUID        NOT NULL REFERENCES meeting(id) ON DELETE CASCADE,
    status      job_status  NOT NULL DEFAULT 'pending',
    created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at  TIMESTAMPTZ
);
```

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | UUID | PK | 任务 ID，对应 `JobResponse.job_id` |
| meeting_id | UUID | FK → meeting(id) CASCADE | 关联会议 |
| status | job_status | NOT NULL DEFAULT 'pending' | 任务状态 |
| created_at | TIMESTAMPTZ | NOT NULL DEFAULT NOW() | 创建时间 |
| updated_at | TIMESTAMPTZ | | 更新时间 |

---

## 3.16 qa_history — 问答历史

> **来源**：[qa.py](../backend/app/schemas/qa.py) `QARequest` / `QAResponse`

```sql
CREATE TABLE qa_history (
    id              UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    meeting_id      UUID        REFERENCES meeting(id) ON DELETE SET NULL,
    question        TEXT        NOT NULL,
    answer          TEXT        NOT NULL,
    scope           qa_scope    NOT NULL DEFAULT 'current_meeting',
    question_embedding vector(1536),
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
```

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | UUID | PK | 问答记录 ID |
| meeting_id | UUID | FK → meeting(id) SET NULL | 关联会议，跨会议查询时为 NULL |
| question | TEXT | NOT NULL | 用户提问 |
| answer | TEXT | NOT NULL | 系统回答 |
| scope | qa_scope | NOT NULL DEFAULT 'current_meeting' | 查询范围 |
| question_embedding | vector(1536) | | 问题语义向量，用于历史问答语义检索 |
| created_at | TIMESTAMPTZ | NOT NULL DEFAULT NOW() | 提问时间 |

---

## 3.17 qa_citation — 问答引用

> **来源**：[qa.py](../backend/app/schemas/qa.py) `Citation`

```sql
CREATE TABLE qa_citation (
    id              UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    qa_history_id   UUID        NOT NULL REFERENCES qa_history(id) ON DELETE CASCADE,
    meeting_id      UUID        NOT NULL REFERENCES meeting(id) ON DELETE CASCADE,
    chunk_id        UUID        NOT NULL REFERENCES transcript_chunk(id) ON DELETE CASCADE,
    speaker         VARCHAR(100) NOT NULL,
    start           DOUBLE PRECISION NOT NULL CHECK (start >= 0),
    end             DOUBLE PRECISION NOT NULL CHECK (end >= 0),
    text            TEXT        NOT NULL
);
```

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | UUID | PK | 引用 ID |
| qa_history_id | UUID | FK → qa_history(id) CASCADE | 所属问答记录 |
| meeting_id | UUID | FK → meeting(id) CASCADE | 引用片段所在会议 |
| chunk_id | UUID | FK → transcript_chunk(id) CASCADE | 引用的转录片段 |
| speaker | VARCHAR(100) | NOT NULL | 说话人 |
| start | DOUBLE PRECISION | NOT NULL, ≥ 0 | 音频起始时间 |
| end | DOUBLE PRECISION | NOT NULL, ≥ 0 | 音频结束时间 |
| text | TEXT | NOT NULL | 引用原文 |

> **PRD 对应**：§4.4 智能问答模块 — 回答附原文、时间点、音频跳转定位。

---

# 4. pgvector 向量存储

使用 [pgvector](https://github.com/pgvector/pgvector) 扩展将向量嵌入直接存储在 PostgreSQL 中，实现结构化数据与语义向量的统一存储与联合查询。

---

## 4.1 扩展启用

```sql
CREATE EXTENSION IF NOT EXISTS vector;
```

---

## 4.2 向量维度说明

| 配置项 | 值 |
|--------|-----|
| 向量维度 | 1536 |
| 距离度量 | Cosine（余弦相似度） |
| 推荐模型 | OpenAI `text-embedding-3-small`（1536 维） |

> **注意**：若使用其他 Embedding 模型（如 `bge-large-zh` 1024 维），需调整 `vector()` 维度参数及对应 HNSW 索引。所有 `vector(1536)` 需统一修改为实际维度。

---

## 4.3 向量字段分布

| 表 | 向量字段 | 用途 | PRD 对应 |
|----|----------|------|----------|
| transcript_chunk | embedding | 转录切片语义向量，支持 chunk 级语义检索 | §4.4 智能问答、§4.6 历史记忆 |
| summary | embedding | 纪要概览语义向量，支持跨会议摘要检索 | §4.6 历史记忆 |
| qa_history | question_embedding | 问题语义向量，支持历史问答语义匹配 | §4.4 智能问答 |

---

## 4.4 向量-标量联合查询示例

**场景：在会议内检索与问题最相关的转录片段**

```sql
SELECT
    tc.id,
    tc.speaker,
    tc.content,
    tc.start,
    tc.end,
    1 - (tc.embedding <=> $1) AS similarity
FROM transcript_chunk tc
WHERE tc.meeting_id = $2
  AND tc.deleted_at IS NULL
ORDER BY tc.embedding <=> $1
LIMIT 5;
```

**场景：跨会议检索与问题相关的摘要**

```sql
SELECT
    s.id,
    s.meeting_id,
    s.overview,
    m.title AS meeting_title,
    1 - (s.embedding <=> $1) AS similarity
FROM summary s
JOIN meeting m ON m.id = s.meeting_id
WHERE m.deleted_at IS NULL
ORDER BY s.embedding <=> $1
LIMIT 5;
```

> **优势**：pgvector 支持在 `WHERE` 子句中同时使用向量距离和标量过滤（如 `meeting_id`、`deleted_at`），无需跨库协调。

---

## 4.5 与独立向量数据库的对比

| 对比项 | pgvector | Qdrant / Milvus |
|--------|----------|-----------------|
| 部署复杂度 | 低（PG 扩展，无额外服务） | 高（独立服务 + 运维） |
| 数据一致性 | 强（同库事务保证） | 弱（需双写同步） |
| 向量-标量联合查询 | 原生 SQL 支持 | 需 payload 过滤 |
| 向量检索性能 | 中小规模优秀（< 1M 向量） | 大规模更优 |
| 运维成本 | 低 | 高 |
| 适用阶段 | MVP → 中期 | 大规模生产 |

> **选型结论**：项目 MVP 阶段与中期（向量数据 < 100 万条），pgvector 完全满足需求，且避免了跨库数据同步的复杂性。后期若向量规模增长，可平滑迁移至专用向量库。

---

# 5. Neo4j 图数据库

用于构建会议知识网络，支持图谱推理与复杂查询。

> **PRD 对应**：§4.8 知识图谱模块

---

## 5.1 节点定义

### Person 节点

```cypher
(:Person {
    name: STRING,       -- 说话人名称，与 transcript_chunk.speaker 对应
    role: STRING        -- 角色（可选）
})
```

### Meeting 节点

```cypher
(:Meeting {
    id: STRING,         -- 与 PostgreSQL meeting.id 对应
    title: STRING,
    started_at: DATETIME
})
```

### Project 节点

```cypher
(:Project {
    name: STRING,
    description: STRING
})
```

### Task 节点

```cypher
(:Task {
    id: STRING,         -- 与 PostgreSQL action_item.id 对应
    task: STRING,
    owner: STRING,
    deadline: DATE,
    priority: STRING,
    status: STRING
})
```

### Decision 节点

```cypher
(:Decision {
    id: STRING,         -- 与 PostgreSQL decision_record.id 对应
    topic: STRING,
    decision: STRING,
    version: INTEGER
})
```

### Risk 节点

```cypher
(:Risk {
    id: STRING,         -- 与 PostgreSQL summary_risk.id 对应
    title: STRING,
    level: STRING,
    description: STRING
})
```

---

## 5.2 关系定义

| 关系 | 类型 | 说明 | PRD 对应 |
|------|------|------|----------|
| (Person)-[:ATTENDED]->(Meeting) | 参会 | 说话人参加会议 | — |
| (Person)-[:PROPOSED]->(Decision) | 提出 | 某人提出某决策 | §4.8 提出 |
| (Person)-[:RESPONSIBLE_FOR]->(Task) | 负责 | 某人负责某任务 | §4.8 负责 |
| (Decision)-[:MADE_IN]->(Meeting) | 产生于 | 决策产生于某会议 | — |
| (Task)-[:DEPENDS_ON]->(Task) | 依赖 | 任务间依赖关系 | §4.8 依赖 |
| (Task)-[:DELAYED_FROM]->(Task) | 延期 | 任务延期关系 | §4.8 延期 |
| (Decision)-[:CONFLICTS_WITH]->(Decision) | 冲突 | 决策冲突关系 | §4.7 |
| (Task)-[:BELONGS_TO]->(Project) | 属于 | 任务归属项目 | — |
| (Risk)-[:RELATED_TO]->(Project) | 关联 | 风险关联项目 | — |

---

## 5.3 图谱查询示例

**查询：最近三次会议张三负责了哪些任务？**

```cypher
MATCH (p:Person {name: '张三'})-[:RESPONSIBLE_FOR]->(t:Task)<-[:HAS_TASK]-(m:Meeting)
WHERE m.started_at >= datetime() - duration({days: 90})
RETURN m.title AS meeting, t.task AS task, t.status AS status, t.deadline AS deadline
ORDER BY m.started_at DESC
LIMIT 10
```

---

# 6. ER 关系图

```text
┌──────────────┐       ┌──────────────┐
│   meeting    │1     N│ meeting_tag  │
│──────────────│───────│──────────────│
│ id (PK)      │       │ id (PK)      │
│ title        │       │ meeting_id(FK)│
│ description  │       │ tag          │
│ status       │       └──────────────┘
│ duration     │
│ audio_url    │1     N┌──────────────────────┐
│ language     │───────│   transcript_chunk   │
│ started_at   │       │──────────────────────│
│ created_at   │       │ id (PK)              │
│ updated_at   │       │ meeting_id (FK)      │
│ deleted_at   │       │ speaker              │
└──────┬───────┘       │ content              │
       │               │ start / end          │
       │               │ confidence           │
       │1            N │ embedding (vector)   │
       │───────────────│ created_at           │
       │               │ updated_at           │
       │               │ deleted_at           │
       │               └────────┬─────────────┘
       │                        │
       │1            N          │
       │───────────────         │
       │               │       │
┌──────────────┐       │       │
│ action_item  │       │       │
│──────────────│       │       │
│ id (PK)      │       │       │
│ meeting_id(FK)│      │       │
│ task         │       │       │
│ owner        │       │       │
│ deadline     │       │       │
│ priority     │       │       │
│ status       │       │       │
│source_chunk_id│──FK──┘       │
│ created_at   │               │
│ updated_at   │               │
│ deleted_at   │               │
└──────────────┘               │
                               │
┌──────────────────┐           │
│ decision_record  │           │
│──────────────────│           │
│ id (PK)          │           │
│ meeting_id (FK)  │           │
│ topic            │           │
│ decision         │           │
│ version          │           │
│source_chunk_id(FK)│──FK──────┘
│ created_at       │
└──────────────────┘

┌──────────────────────┐
│ decision_conflict    │
│──────────────────────│
│ id (PK)              │
│ topic                │
│ current_decision     │
│ previous_decision    │
│ level                │
│ description          │
│current_source_chunk_id│──FK→ transcript_chunk
│ previous_meeting_id  │──FK→ meeting
│ created_at           │
└──────────────────────┘

┌──────────────────────┐
│       summary        │1
│──────────────────────│──────────────────────────────────────┐
│ id (PK)              │1     N            1     N            1     N
│ meeting_id(FK,UNIQUE)│──────┐      ┌──────────────┐  ┌──────────────┐
│ overview             │      │      │summary_topic │  │summary_risk  │
│ embedding (vector)   │      │      │──────────────│  │──────────────│
│ generated_at         │      │      │ id (PK)      │  │ id (PK)      │
└──────────────────────┘      │      │ summary_id(FK)│  │ summary_id(FK)│
                              │      │ title        │  │ title        │
                              │      │ content      │  │ level        │
                              │      │ sort_order   │  │ description  │
                              │      └──────┬───────┘  │ sort_order   │
                              │             │          └──────────────┘
                              │             │N
                              │    ┌────────────────────────┐
                              │    │summary_topic_source    │
                              │    │────────────────────────│
                              │    │summary_topic_id (PK,FK)│
                              │    │chunk_id (PK,FK)        │──FK→ transcript_chunk
                              │    └────────────────────────┘
                              │
                              │1     N
                              │┌───────────────────┐    ┌────────────────────────────┐
                              ││summary_decision   │    │summary_decision_source     │
                              ││───────────────────│    │────────────────────────────│
                              ││ id (PK)           │    │summary_decision_id(PK,FK)  │
                              ││ summary_id (FK)   │    │chunk_id (PK,FK)            │──FK→ transcript_chunk
                              ││ topic             │    └────────────────────────────┘
                              ││ decision          │
                              ││ sort_order        │
                              │└───────────────────┘
                              │
                              │1     N
                              │┌─────────────────────┐
                              ││summary_open_question│
                              ││─────────────────────│
                              ││ id (PK)             │
                              ││ summary_id (FK)     │
                              ││ question            │
                              ││ sort_order          │
                              └─────────────────────┘

┌──────────────┐       ┌────────────────────────┐
│     job      │       │      qa_history        │
│──────────────│       │────────────────────────│
│ id (PK)      │       │ id (PK)                │
│ meeting_id(FK)│      │ meeting_id(FK)         │
│ status       │       │ question               │
│ created_at   │       │ answer                 │
│ updated_at   │       │ scope                  │
└──────────────┘       │ question_embedding(vec)│
                       │ created_at             │
                       └──────────┬─────────────┘
                                  │1
                                  │     N
                       ┌──────────────┐
                       │  qa_citation │
                       │──────────────│
                       │ id (PK)      │
                       │qa_history_id(FK)│
                       │ meeting_id(FK)│
                       │ chunk_id (FK) │
                       │ speaker      │
                       │ start / end  │
                       │ text         │
                       └──────────────┘
```

---

# 7. 索引策略

## 7.1 PostgreSQL 索引

```sql
-- meeting 表
CREATE INDEX idx_meeting_status      ON meeting(status) WHERE deleted_at IS NULL;
CREATE INDEX idx_meeting_started_at  ON meeting(started_at DESC) WHERE deleted_at IS NULL;
CREATE INDEX idx_meeting_created_at  ON meeting(created_at DESC) WHERE deleted_at IS NULL;

-- meeting_tag 表
CREATE INDEX idx_meeting_tag_meeting_id ON meeting_tag(meeting_id);
CREATE INDEX idx_meeting_tag_tag        ON meeting_tag(tag);

-- transcript_chunk 表
CREATE INDEX idx_chunk_meeting_id   ON transcript_chunk(meeting_id) WHERE deleted_at IS NULL;
CREATE INDEX idx_chunk_speaker      ON transcript_chunk(speaker) WHERE deleted_at IS NULL;
CREATE INDEX idx_chunk_start_time   ON transcript_chunk(meeting_id, start) WHERE deleted_at IS NULL;

-- action_item 表
CREATE INDEX idx_action_meeting_id  ON action_item(meeting_id) WHERE deleted_at IS NULL;
CREATE INDEX idx_action_owner       ON action_item(owner) WHERE deleted_at IS NULL;
CREATE INDEX idx_action_status      ON action_item(status) WHERE deleted_at IS NULL;
CREATE INDEX idx_action_deadline    ON action_item(deadline) WHERE deleted_at IS NULL;
CREATE INDEX idx_action_source_chunk ON action_item(source_chunk_id) WHERE deleted_at IS NULL;

-- decision_record 表
CREATE INDEX idx_decision_meeting_id ON decision_record(meeting_id);
CREATE INDEX idx_decision_topic      ON decision_record(topic);
CREATE INDEX idx_decision_source     ON decision_record(source_chunk_id);

-- decision_conflict 表
CREATE INDEX idx_conflict_previous_meeting ON decision_conflict(previous_meeting_id);
CREATE INDEX idx_conflict_level            ON decision_conflict(level);
CREATE INDEX idx_conflict_current_chunk    ON decision_conflict(current_source_chunk_id);

-- summary 表
CREATE INDEX idx_summary_meeting_id ON summary(meeting_id);

-- summary 子表
CREATE INDEX idx_summary_topic_summary_id    ON summary_topic(summary_id);
CREATE INDEX idx_summary_decision_summary_id ON summary_decision(summary_id);
CREATE INDEX idx_summary_risk_summary_id     ON summary_risk(summary_id);
CREATE INDEX idx_summary_question_summary_id ON summary_open_question(summary_id);

-- job 表
CREATE INDEX idx_job_meeting_id ON job(meeting_id);
CREATE INDEX idx_job_status    ON job(status);

-- qa_history 表
CREATE INDEX idx_qa_meeting_id ON qa_history(meeting_id);
CREATE INDEX idx_qa_created_at ON qa_history(created_at DESC);

-- qa_citation 表
CREATE INDEX idx_citation_qa_history_id ON qa_citation(qa_history_id);
CREATE INDEX idx_citation_chunk_id      ON qa_citation(chunk_id);
```

## 7.2 pgvector 向量索引

```sql
-- transcript_chunk.embedding: 转录切片语义检索
CREATE INDEX idx_chunk_embedding ON transcript_chunk
    USING hnsw (embedding vector_cosine_ops)
    WITH (m = 16, ef_construction = 64);

-- summary.embedding: 跨会议摘要检索
CREATE INDEX idx_summary_embedding ON summary
    USING hnsw (embedding vector_cosine_ops)
    WITH (m = 16, ef_construction = 64);

-- qa_history.question_embedding: 历史问答语义匹配
CREATE INDEX idx_qa_question_embedding ON qa_history
    USING hnsw (question_embedding vector_cosine_ops)
    WITH (m = 16, ef_construction = 64);
```

**HNSW 参数说明**：

| 参数 | 值 | 说明 |
|------|-----|------|
| m | 16 | 每个节点的最大连接数，增大可提高召回率但增加索引大小 |
| ef_construction | 64 | 构建索引时的搜索宽度，增大可提高索引质量但增加构建时间 |
| vector_cosine_ops | — | 余弦距离操作符，对应 `<=>` 运算符 |

**运行时参数**：

```sql
-- 查询时调整搜索宽度（越大召回率越高，速度越慢）
SET hnsw.ef_search = 100;
```

> **性能参考**：在 10 万条 1536 维向量数据集上，HNSW 索引 Top-10 查询延迟约 5~15ms。当向量数据超过 100 万条时，建议评估是否需要迁移至专用向量数据库。

## 7.3 Neo4j 索引

```cypher
CREATE CONSTRAINT FOR (p:Person)   REQUIRE p.name IS UNIQUE;
CREATE CONSTRAINT FOR (m:Meeting)  REQUIRE m.id   IS UNIQUE;
CREATE CONSTRAINT FOR (t:Task)     REQUIRE t.id    IS UNIQUE;
CREATE CONSTRAINT FOR (d:Decision) REQUIRE d.id    IS UNIQUE;
CREATE CONSTRAINT FOR (r:Risk)     REQUIRE r.id    IS UNIQUE;
CREATE CONSTRAINT FOR (pj:Project) REQUIRE pj.name IS UNIQUE;
```

---

# 8. 数据契约映射

以下表格展示每个 Pydantic Schema 字段到数据库字段的完整映射关系。

## 8.1 MeetingRead → meeting + meeting_tag

| Schema 字段 | 数据库表.字段 | 说明 |
|-------------|---------------|------|
| id | meeting.id | 直接映射 |
| title | meeting.title | 直接映射 |
| description | meeting.description | 直接映射 |
| tags | meeting_tag.tag (多行) | list → 子表多行 |
| status | meeting.status | ENUM 映射 |
| duration | meeting.duration | 直接映射 |
| audio_url | meeting.audio_url | 直接映射 |
| language | meeting.language | 直接映射 |
| created_at | meeting.created_at | 直接映射 |
| updated_at | meeting.updated_at | 直接映射 |

## 8.2 TranscriptChunkRead → transcript_chunk

| Schema 字段 | 数据库表.字段 | 说明 |
|-------------|---------------|------|
| id | transcript_chunk.id | 直接映射 |
| meeting_id | transcript_chunk.meeting_id | 直接映射 |
| speaker | transcript_chunk.speaker | 直接映射 |
| content | transcript_chunk.content | 直接映射 |
| start | transcript_chunk.start | 直接映射 |
| end | transcript_chunk.end | 直接映射 |
| confidence | transcript_chunk.confidence | 直接映射 |
| updated_at | transcript_chunk.updated_at | 直接映射 |
| — | transcript_chunk.embedding | Schema 未定义，由后端 Embedding 模型生成后写入 |

## 8.3 ActionItemRead → action_item

| Schema 字段 | 数据库表.字段 | 说明 |
|-------------|---------------|------|
| id | action_item.id | 直接映射 |
| meeting_id | action_item.meeting_id | 直接映射 |
| task | action_item.task | 直接映射 |
| owner | action_item.owner | 直接映射 |
| deadline | action_item.deadline | 直接映射 |
| priority | action_item.priority | ENUM 映射 |
| source_chunk_id | action_item.source_chunk_id | 直接映射 |
| status | action_item.status | ENUM 映射 |
| updated_at | action_item.updated_at | 直接映射 |

## 8.4 DecisionRead → decision_record

| Schema 字段 | 数据库表.字段 | 说明 |
|-------------|---------------|------|
| id | decision_record.id | 直接映射 |
| topic | decision_record.topic | 直接映射 |
| decision | decision_record.decision | 直接映射 |
| version | decision_record.version | 直接映射 |
| source_chunk_id | decision_record.source_chunk_id | 直接映射 |
| created_at | decision_record.created_at | 直接映射 |

> **注意**：Schema 中 `DecisionRead` 无 `meeting_id` 字段，但数据库表需要 `meeting_id` 以建立与会议的关联，通过 `source_chunk_id → transcript_chunk.meeting_id` 可间接获取，但直接存储更利于查询。

## 8.5 DecisionConflictRead → decision_conflict

| Schema 字段 | 数据库表.字段 | 说明 |
|-------------|---------------|------|
| id | decision_conflict.id | 直接映射 |
| topic | decision_conflict.topic | 直接映射 |
| current_decision | decision_conflict.current_decision | 直接映射 |
| previous_decision | decision_conflict.previous_decision | 直接映射 |
| level | decision_conflict.level | ENUM 映射 |
| description | decision_conflict.description | 直接映射 |
| current_source_chunk_id | decision_conflict.current_source_chunk_id | 直接映射 |
| previous_meeting_id | decision_conflict.previous_meeting_id | 直接映射 |

## 8.6 SummaryRead → summary + 子表

| Schema 字段 | 数据库表.字段 | 说明 |
|-------------|---------------|------|
| meeting_id | summary.meeting_id | 直接映射 |
| summary.overview | summary.overview | 直接映射 |
| — | summary.embedding | Schema 未定义，由后端 Embedding 模型生成后写入 |
| summary.topics | summary_topic + summary_topic_source | list → 子表 |
| summary.decisions | summary_decision + summary_decision_source | list → 子表 |
| summary.risks | summary_risk | list → 子表 |
| summary.open_questions | summary_open_question | list → 子表 |
| generated_at | summary.generated_at | 直接映射 |

## 8.7 Citation → qa_citation

| Schema 字段 | 数据库表.字段 | 说明 |
|-------------|---------------|------|
| meeting_id | qa_citation.meeting_id | 直接映射 |
| chunk_id | qa_citation.chunk_id | 直接映射 |
| speaker | qa_citation.speaker | 直接映射 |
| start | qa_citation.start | 直接映射 |
| end | qa_citation.end | 直接映射 |
| text | qa_citation.text | 直接映射 |

## 8.8 QARequest / QAResponse → qa_history

| Schema 字段 | 数据库表.字段 | 说明 |
|-------------|---------------|------|
| QARequest.meeting_id | qa_history.meeting_id | 直接映射 |
| QARequest.question | qa_history.question | 直接映射 |
| QARequest.scope | qa_history.scope | ENUM 映射 |
| QAResponse.answer | qa_history.answer | 直接映射 |
| — | qa_history.question_embedding | Schema 未定义，由后端 Embedding 模型生成后写入 |

## 8.9 JobResponse → job + meeting

| Schema 字段 | 数据库表.字段 | 说明 |
|-------------|---------------|------|
| meeting_id | job.meeting_id | 直接映射 |
| job_id | job.id | 直接映射 |
| status | job.status | ENUM 映射 |
