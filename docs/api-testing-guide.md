# MeetingPilot API 接口测试文档

## 前置准备

### 1. 启动后端服务

```bash
cd e:\workspace\MeetingPilot\MeetingPilot\backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 2. 验证服务状态

访问以下地址确认服务正常运行：
- 健康检查：http://localhost:8000/health
- API 文档：http://localhost:8000/docs
- OpenAPI JSON：http://localhost:8000/openapi.json

### 3. Apifox 环境配置

- **基础 URL**：`http://localhost:8000/api/v1`
- **Content-Type**：`application/json`

---

## 一、会议管理接口

### 1.1 创建会议

**接口信息**
- 方法：POST
- 路径：`/meetings`
- 功能：创建一个新的会议记录

**Apifox 操作步骤**
1. 新建接口，选择 **POST**
2. 路径填写：`/meetings`
3. 选择「Body」→ `JSON`，填写请求体

**请求体**
```json
{
  "title": "产品迭代周会",
  "description": "讨论本周产品、研发和测试进度",
  "started_at": "2026-05-16T10:00:00+08:00",
  "tags": ["产品", "周会"]
}
```

**字段说明**
| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| title | string | 是 | 会议标题，1-200字符 |
| description | string | 否 | 会议描述 |
| started_at | datetime | 是 | 会议开始时间，ISO 8601格式 |
| tags | array | 否 | 标签数组 |

**预期响应** (201 Created)
```json
{
  "id": "meet_a7b2c9",
  "title": "产品迭代周会",
  "description": "讨论本周产品、研发和测试进度",
  "status": "created",
  "tags": ["产品", "周会"],
  "duration": 0,
  "audio_url": null,
  "language": null,
  "created_at": "2026-05-16T10:00:00",
  "updated_at": null
}
```

**测试要点**
1. ✅ 正常创建：填写所有必填字段
2. ✅ 最小数据：只填写 title 和 started_at
3. ❌ 错误测试：title 为空字符串（应返回 422）
4. ❌ 错误测试：started_at 格式错误（应返回 422）

---

### 1.2 获取会议列表

**接口信息**
- 方法：GET
- 路径：`/meetings`
- 功能：分页获取会议列表，支持多种筛选条件

**Query 参数**
| 参数 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| page | int | 否 | 1 | 页码，从1开始 |
| size | int | 否 | 20 | 每页条数，建议10-50 |
| keyword | string | 否 | - | 按标题模糊搜索 |
| status | string | 否 | - | 会议状态筛选，可选值见下方 |
| tag | string | 否 | - | 按标签精确匹配 |

**status 可选值**
| 状态值 | 说明 |
|--------|------|
| created | 已创建 |
| uploading | 上传中 |
| transcribing | 转录中 |
| analyzing | 分析中 |
| completed | 已完成 |
| failed | 处理失败 |

---

**Apifox 操作步骤**

### 步骤 1：创建接口
1. 点击「新建接口」
2. 请求方式选择 **GET**
3. 接口路径填写：`/meetings`

### 步骤 2：配置 Query 参数
在「Query 参数」标签页添加参数：

| 参数名 | 参数值 | 必填 | 说明 |
|--------|--------|------|------|
| page | 1 | 否 | 页码 |
| size | 20 | 否 | 每页数量 |

### 步骤 3：发送请求
点击「发送」按钮，查看响应结果

---

**测试用例详解**

### 用例 1：基础查询（获取第一页数据）

**Apifox 配置**
- 方法：GET
- URL：`/meetings`
- Query 参数：
  - page = `1`
  - size = `20`

**完整 URL**
```
GET http://localhost:8000/api/v1/meetings?page=1&size=20
```

**预期响应** (200 OK)
```json
{
  "items": [
    {
      "id": "meet_a7b2c9",
      "title": "产品迭代周会",
      "status": "completed",
      "tags": ["产品", "周会"],
      "duration": 3600.5,
      "created_at": "2026-05-15T10:00:00",
      "updated_at": "2026-05-15T11:00:00"
    },
    {
      "id": "meet_b8c1d2",
      "title": "支付系统技术评审",
      "status": "completed",
      "tags": ["技术", "支付"],
      "duration": 2400.0,
      "created_at": "2026-05-12T14:00:00",
      "updated_at": "2026-05-12T15:30:00"
    },
    {
      "id": "meet_c3d4e5",
      "title": "Q3 产品规划会",
      "status": "transcribing",
      "tags": ["产品", "规划"],
      "duration": 0,
      "created_at": "2026-05-16T09:00:00",
      "updated_at": "2026-05-16T09:00:00"
    }
  ],
  "total": 3,
  "page": 1,
  "size": 20
}
```

**响应字段说明**
| 字段 | 类型 | 说明 |
|------|------|------|
| items | array | 会议列表数组 |
| items[].id | string | 会议唯一标识 |
| items[].title | string | 会议标题 |
| items[].status | string | 会议状态 |
| items[].tags | array | 标签数组 |
| items[].duration | float | 音频时长（秒） |
| items[].created_at | datetime | 创建时间 |
| items[].updated_at | datetime | 更新时间 |
| total | int | 总记录数 |
| page | int | 当前页码 |
| size | int | 每页条数 |

---

### 用例 2：关键词搜索（按标题搜索）

**场景**：搜索标题包含"支付"的会议

**Apifox 配置**
- 方法：GET
- URL：`/meetings`
- Query 参数：
  - keyword = `支付`
  - page = `1`
  - size = `20`

**完整 URL**
```
GET http://localhost:8000/api/v1/meetings?keyword=支付&page=1&size=20
```

**预期响应**
```json
{
  "items": [
    {
      "id": "meet_b8c1d2",
      "title": "支付系统技术评审",
      "status": "completed",
      "tags": ["技术", "支付"],
      "duration": 2400.0,
      "created_at": "2026-05-12T14:00:00",
      "updated_at": "2026-05-12T15:30:00"
    }
  ],
  "total": 1,
  "page": 1,
  "size": 20
}
```

---

### 用例 3：状态筛选（按会议状态过滤）

**场景**：只查看已完成的会议

**完整 URL**
```
GET http://localhost:8000/api/v1/meetings?status=completed
```

**预期响应**：返回 2 条 status 为 completed 的会议

---

### 用例 4：标签筛选（按标签过滤）

**场景**：查看所有"产品"相关的会议

**完整 URL**
```
GET http://localhost:8000/api/v1/meetings?tag=产品
```

**预期响应**：返回 2 条标签包含"产品"的会议（meet_a7b2c9、meet_c3d4e5）

---

### 用例 5：组合筛选（多条件联合查询）

**完整 URL**
```
GET http://localhost:8000/api/v1/meetings?keyword=产品&status=completed&tag=周会&page=1&size=10
```

**预期响应**：返回 1 条同时满足所有条件的会议

---

### 用例 6：分页测试（获取第二页）

**完整 URL**
```
GET http://localhost:8000/api/v1/meetings?page=2&size=2
```

**预期响应**：返回第 3 条会议，total=3，page=2，size=2

---

### 用例 7：无参数请求（使用默认值）

**完整 URL**
```
GET http://localhost:8000/api/v1/meetings
```

**预期行为**：默认 page=1，size=20，返回所有会议

---

**Mock 数据说明**

| 会议ID | 标题 | 状态 | 标签 |
|--------|------|------|------|
| meet_a7b2c9 | 产品迭代周会 | completed | ["产品", "周会"] |
| meet_b8c1d2 | 支付系统技术评审 | completed | ["技术", "支付"] |
| meet_c3d4e5 | Q3 产品规划会 | transcribing | ["产品", "规划"] |

---

### 1.3 获取会议详情

**接口信息**
- 方法：GET
- 路径：`/meetings/{meeting_id}`
- 功能：获取单个会议的详细信息

**路径参数**
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| meeting_id | string | 是 | 会议ID，有效值：meet_a7b2c9, meet_b8c1d2, meet_c3d4e5 |

**Apifox 操作步骤**
1. 新建接口，选择 **GET**
2. 路径填写：`/meetings/meet_a7b2c9`
3. 点击「发送」

**测试用例**

### 用例 1：获取存在的会议

**完整 URL**
```
GET http://localhost:8000/api/v1/meetings/meet_a7b2c9
```

**预期响应** (200 OK)
```json
{
  "id": "meet_a7b2c9",
  "title": "产品迭代周会",
  "description": "讨论本周产品、研发和测试进度",
  "status": "completed",
  "tags": ["产品", "周会"],
  "duration": 3600.5,
  "audio_url": "/storage/audio/meet_a7b2c9.mp3",
  "language": "zh",
  "created_at": "2026-05-15T10:00:00",
  "updated_at": "2026-05-15T11:00:00"
}
```

---

### 用例 2：获取不存在的会议

**完整 URL**
```
GET http://localhost:8000/api/v1/meetings/meet_not_exist
```

**预期响应** (404 Not Found)
```json
{
  "detail": {
    "code": "MEETING_NOT_FOUND",
    "message": "会议不存在",
    "details": {
      "meeting_id": "meet_not_exist"
    }
  }
}
```

---

### 1.4 更新会议信息

**接口信息**
- 方法：PATCH
- 路径：`/meetings/{meeting_id}`
- 功能：部分更新会议信息（只更新传入的字段）

**路径参数**
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| meeting_id | string | 是 | 会议ID，有效值：meet_a7b2c9, meet_b8c1d2, meet_c3d4e5 |

**请求体字段**
| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| title | string | 否 | 会议标题，1-200字符 |
| description | string | 否 | 会议描述，传 null 清空 |
| tags | array | 否 | 标签数组，会完全替换原有标签 |

**重要说明**
- PATCH 是**部分更新**，只更新传入的字段
- 不传的字段保持原值不变
- `tags` 字段会**完全替换**原有标签，不是追加
- 传 `null` 可清空 description 字段

---

**Apifox 操作步骤**

### 步骤 1：创建接口
1. 点击「新建接口」
2. 请求方式选择 **PATCH**
3. 接口路径填写：`/meetings/meet_a7b2c9`

### 步骤 2：配置请求体
1. 选择「Body」标签页
2. 格式选择 `JSON`
3. 填写 JSON 请求体（见下方用例）

### 步骤 3：发送请求
点击「发送」按钮，查看响应结果

---

**测试用例详解**

### 用例 1：只更新标题

**Apifox 配置**
- 方法：PATCH
- URL：`/meetings/meet_a7b2c9`
- Body (JSON)：
```json
{
  "title": "产品迭代周会 - 5月版"
}
```

**完整请求**
```
PATCH http://localhost:8000/api/v1/meetings/meet_a7b2c9
Content-Type: application/json

{
  "title": "产品迭代周会 - 5月版"
}
```

**预期响应** (200 OK)
```json
{
  "id": "meet_a7b2c9",
  "title": "产品迭代周会 - 5月版",
  "description": "讨论本周产品、研发和测试进度",
  "status": "completed",
  "tags": ["产品", "周会"],
  "duration": 3600.5,
  "audio_url": "/storage/audio/meet_a7b2c9.mp3",
  "language": "zh",
  "created_at": "2026-05-15T10:00:00",
  "updated_at": "2026-05-16T14:30:00"
}
```

**验证要点**
- ✅ title 已更新为新值
- ✅ description 保持原值不变
- ✅ tags 保持原值不变
- ✅ updated_at 时间已更新

---

### 用例 2：只更新描述

**Body (JSON)**：
```json
{
  "description": "讨论本周产品、研发和测试进度，重点对齐支付模块延期问题"
}
```

**预期响应**：description 更新，其他字段保持原值

---

### 用例 3：更新标签（完全替换）

**Body (JSON)**：
```json
{
  "tags": ["产品", "复盘", "重要"]
}
```

**⚠️ 重要提示**
- 原标签 `["产品", "周会"]` 被完全替换为 `["产品", "复盘", "重要"]`
- 如果想保留原有标签，需要在请求中包含所有标签

---

### 用例 4：批量更新多个字段

**Body (JSON)**：
```json
{
  "title": "产品迭代周会复盘",
  "description": "本周产品迭代周会复盘，总结支付模块延期原因及后续计划",
  "tags": ["产品", "复盘", "支付模块"]
}
```

**预期响应**：三个字段同时更新

---

### 用例 5：清空描述

**Body (JSON)**：
```json
{
  "description": null
}
```

**预期响应**：description 变为 null

**说明**
- 传 `null` 会将 description 清空为 null
- 传空字符串 `""` 也会被转为 null（由 Schema 的 BeforeValidator 处理）
- 不传 description 字段则保留原值

---

### 用例 6：更新不存在的会议

**Body (JSON)**：
```json
{
  "title": "不存在的会议"
}
```

**URL**：`/meetings/meet_not_exist`

**预期响应** (404 Not Found)
```json
{
  "detail": {
    "code": "MEETING_NOT_FOUND",
    "message": "会议不存在",
    "details": {
      "meeting_id": "meet_not_exist"
    }
  }
}
```

---

### 用例 7：标题为空字符串（验证失败）

**Body (JSON)**：
```json
{
  "title": ""
}
```

**预期响应** (422 Unprocessable Entity)

---

### 用例 8：空请求体（不更新任何字段）

**Body (JSON)**：
```json
{}
```

**预期响应** (200 OK)：所有字段保持原值，updated_at 更新

---

**Mock 数据说明**

| 会议ID | 原始标题 | 原始描述 | 原始标签 |
|--------|----------|----------|----------|
| meet_a7b2c9 | 产品迭代周会 | 讨论本周产品、研发和测试进度 | ["产品", "周会"] |
| meet_b8c1d2 | 支付系统技术评审 | 支付回调问题排查 | ["技术", "支付"] |
| meet_c3d4e5 | Q3 产品规划会 | 讨论 Q3 产品路线图 | ["产品", "规划"] |

---

### 1.5 删除会议

**接口信息**
- 方法：DELETE
- 路径：`/meetings/{meeting_id}`
- 功能：删除会议

**Apifox 操作步骤**
1. 新建接口，选择 **DELETE**
2. 路径填写：`/meetings/meet_a7b2c9`
3. 点击「发送」

**完整 URL**
```
DELETE http://localhost:8000/api/v1/meetings/meet_a7b2c9
```

**预期响应** (204 No Content)
- 无响应体

---

### 1.6 上传会议音频

**接口信息**
- 方法：POST
- 路径：`/meetings/upload`
- 功能：上传音频文件并启动转录处理
- Content-Type: `multipart/form-data`

**请求参数**
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| file | File | 是 | 音频文件(mp3/wav/m4a) |
| title | string | 是 | 会议标题 |
| description | string | 否 | 会议描述 |
| language | string | 否 | 语言代码(zh/en) |
| enable_speaker_diarization | boolean | 否 | 是否启用说话人分离，默认true |

---

**Apifox 详细操作步骤**

### 步骤 1：创建接口
1. 点击「新建接口」
2. 请求方式选择 **POST**
3. 接口路径填写：`/meetings/upload`

### 步骤 2：配置 Body 为 form-data
1. 选择「Body」标签页
2. 点击格式选择，切换到 `form-data`
3. 确保 Content-Type 显示为 `multipart/form-data`

### 步骤 3：添加参数

在 form-data 中添加以下参数：

| 参数名 | 类型 | 值 | 说明 |
|--------|------|-----|------|
| file | File | [点击选择文件] | 上传音频文件 |
| title | Text | 产品迭代周会 | 会议标题 |
| description | Text | 讨论本周产品、研发和测试进度 | 会议描述（可选） |
| language | Text | zh | 语言代码（可选） |
| enable_speaker_diarization | Text | true | 启用说话人分离（可选） |

**file 参数配置**：
- 点击值列的「选择文件」按钮
- 选择一个音频文件（.mp3、.wav 或 .m4a 格式）
- 文件大小建议不超过 500MB

---

**测试用例详解**

### 用例 1：基础上传（必填字段）

**场景**：只上传必填字段

**Apifox 配置**
- 方法：POST
- URL：`/meetings/upload`
- Body (form-data)：
  - file = [选择一个 mp3 文件]
  - title = `产品迭代周会`

**完整请求**
```
POST http://localhost:8000/api/v1/meetings/upload
Content-Type: multipart/form-data; boundary=----WebKitFormBoundary

------WebKitFormBoundary
Content-Disposition: form-data; name="file"; filename="meeting.mp3"
Content-Type: audio/mpeg

[音频文件二进制内容]
------WebKitFormBoundary
Content-Disposition: form-data; name="title"

产品迭代周会
------WebKitFormBoundary--
```

**预期响应** (202 Accepted)
```json
{
  "meeting_id": "meet_a7b2c9",
  "job_id": "job_9x2k1m",
  "status": "running"
}
```

**说明**
- `meeting_id`: 新创建的会议ID
- `job_id`: 转录任务ID，用于查询处理进度
- `status`: 任务状态，running 表示正在处理

---

### 用例 2：完整上传（所有字段）

**场景**：上传音频并指定所有可选参数

**Apifox 配置**
- 方法：POST
- URL：`/meetings/upload`
- Body (form-data)：
  - file = [选择一个 wav 文件]
  - title = `支付系统技术评审`
  - description = `讨论支付回调问题及解决方案`
  - language = `zh`
  - enable_speaker_diarization = `true`

**完整请求**
```
POST http://localhost:8000/api/v1/meetings/upload
Content-Type: multipart/form-data; boundary=----WebKitFormBoundary

------WebKitFormBoundary
Content-Disposition: form-data; name="file"; filename="payment_review.wav"
Content-Type: audio/wav

[音频文件二进制内容]
------WebKitFormBoundary
Content-Disposition: form-data; name="title"

支付系统技术评审
------WebKitFormBoundary
Content-Disposition: form-data; name="description"

讨论支付回调问题及解决方案
------WebKitFormBoundary
Content-Disposition: form-data; name="language"

zh
------WebKitFormBoundary
Content-Disposition: form-data; name="enable_speaker_diarization"

true
------WebKitFormBoundary--
```

**预期响应** (202 Accepted)
```json
{
  "meeting_id": "meet_b8c1d2",
  "job_id": "job_9x2k1m",
  "status": "running"
}
```

---

### 用例 3：英文会议上传

**场景**：上传英文会议音频

**Apifox 配置**
- 方法：POST
- URL：`/meetings/upload`
- Body (form-data)：
  - file = [选择一个 m4a 文件]
  - title = `Weekly Product Review`
  - description = `Review product progress and plan for next sprint`
  - language = `en`
  - enable_speaker_diarization = `true`

**预期响应** (202 Accepted)
```json
{
  "meeting_id": "meet_c3d4e5",
  "job_id": "job_9x2k1m",
  "status": "running"
}
```

---

### 用例 4：禁用说话人分离

**场景**：上传音频但不区分说话人（加快处理速度）

**Apifox 配置**
- 方法：POST
- URL：`/meetings/upload`
- Body (form-data)：
  - file = [选择一个 mp3 文件]
  - title = `快速会议记录`
  - enable_speaker_diarization = `false`

**说明**
- 设置 `enable_speaker_diarization=false` 可以加快转录速度
- 适用于不需要区分说话人的场景
- 转录结果不会包含 speaker 字段

---

### 用例 5：缺少必填字段（验证失败）

**场景**：不上传文件，只传 title

**Apifox 配置**
- 方法：POST
- URL：`/meetings/upload`
- Body (form-data)：
  - title = `测试会议`
  - （不添加 file 参数，或 file 参数未选择文件）

**Apifox 控制台警告**
```
"Form param `file`, file load error: missing file source"
```

**说明**
- 如果 file 参数类型设置为 file 但没有选择具体文件，Apifox 会发送空文件
- 当前 Mock 实现会返回 202（实际生产环境应该返回 422）
- 要正确测试此用例，需要完全删除 file 参数（不是留空）

**正确测试方式**
1. 在 form-data 中完全删除 file 参数行
2. 只保留 title 参数
3. 发送请求

**预期响应** (422 Unprocessable Entity)
```json
{
  "detail": [
    {
      "loc": ["body", "file"],
      "msg": "field required",
      "type": "value_error.missing"
    }
  ]
}
```

---

### 用例 6：缺少 title（验证失败）

**场景**：只上传文件，不传 title

**Apifox 配置**
- 方法：POST
- URL：`/meetings/upload`
- Body (form-data)：
  - file = [选择一个 mp3 文件]
  - （不添加 title 参数）

**预期响应** (422 Unprocessable Entity)
```json
{
  "detail": [
    {
      "loc": ["body", "title"],
      "msg": "field required",
      "type": "value_error.missing"
    }
  ]
}
```

---

### 用例 7：文件格式不支持（验证失败）

**场景**：上传非音频文件（如 .txt、.pdf、.jpg 等）

**Apifox 配置**
- 方法：POST
- URL：`/meetings/upload`
- Body (form-data)：
  - file = [选择一个非音频文件，如 .txt 或 .pdf]
  - title = `测试会议`

**完整请求**
```
POST http://localhost:8000/api/v1/meetings/upload
Content-Type: multipart/form-data; boundary=----WebKitFormBoundary

------WebKitFormBoundary
Content-Disposition: form-data; name="file"; filename="test.txt"
Content-Type: text/plain

[文本文件内容]
------WebKitFormBoundary
Content-Disposition: form-data; name="title"

测试会议
------WebKitFormBoundary--
```

**预期响应** (415 Unsupported Media Type)
```json
{
  "detail": "不支持的文件格式 'text/plain'，请上传 mp3、wav 或 m4a 格式的音频文件"
}
```

**说明**
- 后端会检查文件的 `Content-Type`
- 仅支持以下音频格式：
  - `audio/mpeg` (MP3)
  - `audio/wav` 或 `audio/x-wav` (WAV)
  - `audio/mp4` 或 `audio/x-m4a` (M4A)
- 上传其他类型文件会返回 415 错误

---

**测试流程建议**

上传音频后的完整测试流程：

1. **上传音频** - POST `/meetings/upload`
   - 记录返回的 `meeting_id` 和 `job_id`

2. **查询任务状态** - GET `/meetings/{meeting_id}/jobs`
   - 使用返回的 meeting_id 查询转录进度
   - 等待 status 变为 completed

3. **获取转录结果** - GET `/meetings/{meeting_id}/transcripts`
   - 转录完成后获取文本切片

4. **获取会议纪要** - GET `/meetings/{meeting_id}/summary`
   - 查看生成的结构化纪要

5. **获取待办事项** - GET `/meetings/{meeting_id}/actions`
   - 查看提取的待办任务

---

**常见问题排查**

### 问题 1：文件上传失败

**现象**：Apifox 提示上传失败或超时

**解决方案**：
1. 检查文件大小是否超过限制（建议 < 500MB）
2. 检查文件是否为有效的音频文件
3. 检查网络连接是否稳定
4. 尝试使用更小的文件测试

### 问题 2：Content-Type 错误

**现象**：返回 422 错误，提示无法解析请求

**解决方案**：
1. 确保 Body 格式选择为 `form-data`，不是 `json`
2. 确保 file 参数的类型选择为「文件」，不是「文本」
3. 不要手动设置 Content-Type 头部，Apifox 会自动处理

### 问题 3：转录任务一直 running

**现象**：任务状态长时间不变化

**说明**：
- 当前是 Mock 数据，任务状态不会自动变化
- 实际环境中，转录时间取决于音频长度（约 1:1 到 1:2 的时间比）
- 可以通过 WebSocket `/meetings/{meeting_id}/events` 接收实时进度推送

---

**支持的音频格式**

| 格式 | MIME 类型 | 说明 |
|------|-----------|------|
| MP3 | audio/mpeg | 最常用，压缩率高 |
| WAV | audio/wav | 无损格式，文件较大 |
| M4A | audio/mp4 | iPhone 录音默认格式 |

**建议**：
- 优先使用 MP3 格式，平衡音质和文件大小
- 采样率建议 16kHz 或以上
- 单声道即可满足转录需求

---

### 1.7 重新转录会议

**接口信息**
- 方法：POST
- 路径：`/meetings/{meeting_id}/transcribe`
- 功能：重新转录已上传的音频

**Apifox 操作步骤**
1. 选择 POST 方法
2. 路径填写：`/meetings/meet_a7b2c9/transcribe`
3. 不需要 Body，参数通过 Query 传递

**Query 参数**
| 参数 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| language | string | 否 | None | 语言代码 |
| enable_speaker_diarization | boolean | 否 | true | 是否启用说话人分离 |

**完整 URL**
```
POST http://localhost:8000/api/v1/meetings/meet_a7b2c9/transcribe?language=zh&enable_speaker_diarization=true
```

**预期响应** (202 Accepted)
```json
{
  "meeting_id": "meet_a7b2c9",
  "job_id": "job_8m3p2x",
  "status": "running"
}
```

---

### 1.8 获取会议任务状态

**接口信息**
- 方法：GET
- 路径：`/meetings/{meeting_id}/jobs`
- 功能：获取会议处理任务列表和状态

**Apifox 操作步骤**
1. 选择 GET 方法
2. 路径填写：`/meetings/meet_a7b2c9/jobs`
3. 点击「发送」

**完整 URL**
```
GET http://localhost:8000/api/v1/meetings/meet_a7b2c9/jobs
```

**预期响应** (200 OK)
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

---

### 1.9 手动触发 Agent 分析

**接口信息**
- 方法：POST
- 路径：`/meetings/{meeting_id}/agents/run`
- 功能：手动触发指定 Agent 进行分析

**Apifox 操作步骤**
1. 选择 POST 方法
2. 路径填写：`/meetings/meet_a7b2c9/agents/run`
3. 选择「Body」→ `JSON`

**请求体**
```json
{
  "agents": ["summary", "action", "memory", "graph", "conflict"]
}
```

**agents 可选值**
| 值 | 说明 |
|----|------|
| summary | 生成会议纪要 |
| action | 提取待办事项 |
| memory | 长期记忆检索 |
| graph | 知识图谱构建 |
| conflict | 决策冲突检测 |

**预期响应** (202 Accepted)
```json
{
  "meeting_id": "meet_a7b2c9",
  "job_id": "job_agent_001",
  "status": "running"
}
```

---

## 二、转录接口

### 2.1 获取转录切片

**接口信息**
- 方法：GET
- 路径：`/meetings/{meeting_id}/transcripts`
- 功能：获取会议的转录文本切片，支持按说话人和关键词筛选

**路径参数**
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| meeting_id | string | 是 | 会议ID |

**Query 参数**
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| speaker | string | 否 | 按说话人筛选 |
| keyword | string | 否 | 转录文本搜索 |

**Apifox 操作步骤**
1. 新建接口，选择 **GET**
2. 路径填写：`/meetings/meet_a7b2c9/transcripts`
3. 在「Query 参数」中添加筛选条件（可选）

**测试用例**

### 用例 1：获取全部转录

**完整 URL**
```
GET http://localhost:8000/api/v1/meetings/meet_a7b2c9/transcripts
```

**预期响应** (200 OK)
```json
{
  "meeting_id": "meet_a7b2c9",
  "chunks": [
    {
      "id": "chunk_1001",
      "meeting_id": "meet_a7b2c9",
      "speaker": "张三",
      "start": 0.0,
      "end": 4.25,
      "content": "大家好，今天主要对齐一下支付模块的延期问题。",
      "confidence": 0.96,
      "updated_at": null
    },
    {
      "id": "chunk_1002",
      "meeting_id": "meet_a7b2c9",
      "speaker": "李四",
      "start": 4.5,
      "end": 12.8,
      "content": "支付模块由于第三方回调问题，需要延期到周五完成。目前测试环境已经复现了这个问题。",
      "confidence": 0.94,
      "updated_at": null
    },
    {
      "id": "chunk_1003",
      "meeting_id": "meet_a7b2c9",
      "speaker": "王五",
      "start": 13.0,
      "end": 20.5,
      "content": "那原定周三上线的计划需要调整了，建议推迟到周五一起上线。",
      "confidence": 0.95,
      "updated_at": null
    },
    {
      "id": "chunk_1004",
      "meeting_id": "meet_a7b2c9",
      "speaker": "张三",
      "start": 21.0,
      "end": 28.3,
      "content": "同意，王五你负责跟进支付回调的修复，周四前给我反馈。",
      "confidence": 0.97,
      "updated_at": null
    },
    {
      "id": "chunk_1005",
      "meeting_id": "meet_a7b2c9",
      "speaker": "王五",
      "start": 28.5,
      "end": 32.0,
      "content": "好的，我会尽快处理。",
      "confidence": 0.98,
      "updated_at": null
    }
  ]
}
```

---

### 用例 2：按说话人筛选

**完整 URL**
```
GET http://localhost:8000/api/v1/meetings/meet_a7b2c9/transcripts?speaker=张三
```

**预期响应**：返回 chunk_1001 和 chunk_1004（张三的发言）

---

### 用例 3：按关键词搜索

**完整 URL**
```
GET http://localhost:8000/api/v1/meetings/meet_a7b2c9/transcripts?keyword=支付
```

**预期响应**：返回包含"支付"关键词的切片（chunk_1001、chunk_1002、chunk_1004）

---

**Mock 数据说明**

| 切片ID | 说话人 | 时间段 | 内容摘要 |
|--------|--------|--------|----------|
| chunk_1001 | 张三 | 0.0-4.25 | 对齐支付模块延期问题 |
| chunk_1002 | 李四 | 4.5-12.8 | 第三方回调问题需延期 |
| chunk_1003 | 王五 | 13.0-20.5 | 建议推迟到周五上线 |
| chunk_1004 | 张三 | 21.0-28.3 | 安排王五跟进修复 |
| chunk_1005 | 王五 | 28.5-32.0 | 确认处理 |

---

### 2.2 获取单个转录切片

**接口信息**
- 方法：GET
- 路径：`/transcripts/{chunk_id}`

**Apifox 操作步骤**
1. 选择 GET 方法
2. 路径填写：`/transcripts/chunk_1001`
3. 点击「发送」

**完整 URL**
```
GET http://localhost:8000/api/v1/transcripts/chunk_1001
```

**预期响应** (200 OK)
```json
{
  "id": "chunk_1001",
  "meeting_id": "meet_a7b2c9",
  "speaker": "张三",
  "start": 0.0,
  "end": 4.25,
  "content": "大家好，今天主要对齐一下支付模块的延期问题。",
  "confidence": 0.96,
  "updated_at": null
}
```

---

### 2.3 更新转录切片

**接口信息**
- 方法：PATCH
- 路径：`/transcripts/{chunk_id}`
- 功能：人工修正转录文本或说话人

**路径参数**
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| chunk_id | string | 是 | 转录切片ID |

**请求体字段**
| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| speaker | string | 否 | 说话人名称 |
| content | string | 否 | 转录文本内容 |

**Apifox 操作步骤**
1. 选择 PATCH 方法
2. 路径填写：`/transcripts/chunk_1001`
3. 选择「Body」→ `JSON`

**测试用例**

### 用例 1：只更新说话人

**Body (JSON)**：
```json
{
  "speaker": "王五"
}
```

**完整 URL**
```
PATCH http://localhost:8000/api/v1/transcripts/chunk_1001
```

---

### 用例 2：只更新内容

**Body (JSON)**：
```json
{
  "content": "修正后的转录文本"
}
```

---

### 用例 3：同时更新

**Body (JSON)**：
```json
{
  "speaker": "李四",
  "content": "支付模块延期到周五完成。"
}
```

**预期响应** (200 OK)
```json
{
  "id": "chunk_1001",
  "meeting_id": "meet_a7b2c9",
  "speaker": "李四",
  "start": 0.0,
  "end": 4.25,
  "content": "支付模块延期到周五完成。",
  "confidence": 0.96,
  "updated_at": "2026-05-16T11:10:00"
}
```

---

## 三、结构化纪要接口

### 3.1 获取会议纪要

**接口信息**
- 方法：GET
- 路径：`/meetings/{meeting_id}/summary`
- 功能：获取会议的结构化纪要，包含概览、议题、决策、风险和待确认问题

**Apifox 操作步骤**
1. 选择 GET 方法
2. 路径填写：`/meetings/meet_a7b2c9/summary`
3. 点击「发送」

**完整 URL**
```
GET http://localhost:8000/api/v1/meetings/meet_a7b2c9/summary
```

**预期响应** (200 OK)
```json
{
  "meeting_id": "meet_a7b2c9",
  "summary": {
    "overview": "本次会议主要讨论支付模块延期、接口联调和上线时间调整。",
    "topics": [
      {
        "title": "支付模块延期",
        "content": "支付模块由于第三方回调问题延期到周五完成。测试环境已复现问题，王五负责跟进修复。",
        "source_chunk_ids": ["chunk_1001", "chunk_1002"]
      },
      {
        "title": "上线时间调整",
        "content": "原定周三上线计划推迟到周五，等待支付模块修复后一起上线。",
        "source_chunk_ids": ["chunk_1003"]
      },
      {
        "title": "任务分配",
        "content": "王五负责支付回调修复，需在周四前反馈进度。",
        "source_chunk_ids": ["chunk_1004"]
      }
    ],
    "decisions": [
      {
        "topic": "上线时间",
        "decision": "原定周三上线调整为周五上线",
        "source_chunk_ids": ["chunk_1003"]
      },
      {
        "topic": "任务负责人",
        "decision": "王五负责支付回调修复",
        "source_chunk_ids": ["chunk_1004"]
      }
    ],
    "risks": [
      {
        "title": "第三方回调稳定性",
        "level": "high",
        "description": "若回调问题未解决，会影响支付闭环验证。"
      },
      {
        "title": "延期影响范围",
        "level": "medium",
        "description": "周五上线可能影响周末用户高峰期体验。"
      }
    ],
    "open_questions": [
      "测试环境是否能在周四前稳定复现回调问题？",
      "周五上线是否需要申请紧急发布流程？"
    ]
  },
  "generated_at": "2026-05-16T11:20:00"
}
```

**响应字段说明**
| 字段 | 类型 | 说明 |
|------|------|------|
| summary.overview | string | 会议概览 |
| summary.topics | array | 讨论议题列表 |
| summary.topics[].source_chunk_ids | array | 关联的转录切片ID |
| summary.decisions | array | 决策列表 |
| summary.risks | array | 风险列表，level 可选值：low/medium/high |
| summary.open_questions | array | 待确认问题列表 |
| generated_at | datetime | 纪要生成时间 |

---

### 3.2 重新生成会议纪要

**接口信息**
- 方法：POST
- 路径：`/meetings/{meeting_id}/summary/generate`

**Apifox 操作步骤**
1. 选择 POST 方法
2. 路径填写：`/meetings/meet_a7b2c9/summary/generate`
3. 不需要 Body
4. 点击「发送」

**完整 URL**
```
POST http://localhost:8000/api/v1/meetings/meet_a7b2c9/summary/generate
```

**预期响应** (202 Accepted)
```json
{
  "meeting_id": "meet_a7b2c9",
  "job_id": "job_s7k20d",
  "status": "running"
}
```

---

## 四、待办事项接口

### 4.1 获取会议待办

**接口信息**
- 方法：GET
- 路径：`/meetings/{meeting_id}/actions`
- 功能：获取会议关联的所有待办事项

**Apifox 操作步骤**
1. 选择 GET 方法
2. 路径填写：`/meetings/meet_a7b2c9/actions`
3. 点击「发送」

**完整 URL**
```
GET http://localhost:8000/api/v1/meetings/meet_a7b2c9/actions
```

**预期响应** (200 OK)
```json
{
  "meeting_id": "meet_a7b2c9",
  "items": [
    {
      "id": "act_501",
      "meeting_id": "meet_a7b2c9",
      "task": "修复支付回调失败问题",
      "owner": "王五",
      "deadline": "2026-05-18",
      "priority": "high",
      "status": "todo",
      "source_chunk_id": "chunk_1001",
      "updated_at": null
    },
    {
      "id": "act_502",
      "meeting_id": "meet_a7b2c9",
      "task": "补充支付回调异常日志",
      "owner": "王五",
      "deadline": "2026-05-17",
      "priority": "medium",
      "status": "doing",
      "source_chunk_id": "chunk_1002",
      "updated_at": "2026-05-16T09:00:00"
    },
    {
      "id": "act_503",
      "meeting_id": "meet_a7b2c9",
      "task": "更新上线计划文档",
      "owner": "张三",
      "deadline": "2026-05-17",
      "priority": "low",
      "status": "done",
      "source_chunk_id": "chunk_1003",
      "updated_at": "2026-05-16T07:00:00"
    }
  ]
}
```

**Mock 数据说明**

| 待办ID | 任务 | 负责人 | 优先级 | 状态 |
|--------|------|--------|--------|------|
| act_501 | 修复支付回调失败问题 | 王五 | high | todo |
| act_502 | 补充支付回调异常日志 | 王五 | medium | doing |
| act_503 | 更新上线计划文档 | 张三 | low | done |

---

### 4.2 创建待办

**接口信息**
- 方法：POST
- 路径：`/meetings/{meeting_id}/actions`
- 功能：为会议创建新的待办事项

**Apifox 操作步骤**
1. 选择 POST 方法
2. 路径填写：`/meetings/meet_a7b2c9/actions`
3. 选择「Body」→ `JSON`

**请求体**
```json
{
  "task": "补充支付回调异常日志",
  "owner": "王五",
  "deadline": "2026-05-18",
  "priority": "medium",
  "source_chunk_id": "chunk_1001"
}
```

**字段说明**
| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| task | string | 是 | 待办任务描述 |
| owner | string | 是 | 负责人 |
| deadline | date | 是 | 截止日期，格式 YYYY-MM-DD |
| priority | string | 是 | 优先级：low/medium/high/urgent |
| source_chunk_id | string | 否 | 关联的转录切片ID |

**priority 可选值**
| 值 | 说明 |
|----|------|
| low | 低优先级 |
| medium | 中优先级 |
| high | 高优先级 |
| urgent | 紧急 |

**预期响应** (201 Created)
```json
{
  "id": "act_504",
  "meeting_id": "meet_a7b2c9",
  "task": "补充支付回调异常日志",
  "owner": "王五",
  "deadline": "2026-05-18",
  "priority": "medium",
  "status": "todo",
  "source_chunk_id": "chunk_1001",
  "updated_at": null
}
```

---

### 4.3 更新待办

**接口信息**
- 方法：PATCH
- 路径：`/actions/{action_id}`
- 功能：更新待办事项的状态、优先级等信息

**Apifox 操作步骤**
1. 选择 PATCH 方法
2. 路径填写：`/actions/act_501`
3. 选择「Body」→ `JSON`

**请求体**
```json
{
  "task": "补充支付回调异常日志并同步测试",
  "owner": "王五",
  "deadline": "2026-05-19",
  "priority": "high",
  "status": "doing"
}
```

**字段说明**
- 所有字段都是可选的
- 只传需要更新的字段

**status 可选值**
| 值 | 说明 |
|----|------|
| todo | 待办 |
| doing | 进行中 |
| done | 已完成 |
| canceled | 已取消 |

**预期响应** (200 OK)
```json
{
  "id": "act_501",
  "meeting_id": "meet_a7b2c9",
  "task": "补充支付回调异常日志并同步测试",
  "owner": "王五",
  "deadline": "2026-05-19",
  "priority": "high",
  "status": "doing",
  "source_chunk_id": "chunk_1001",
  "updated_at": "2026-05-16T11:30:00"
}
```

---

### 4.4 删除待办

**接口信息**
- 方法：DELETE
- 路径：`/actions/{action_id}`

**Apifox 操作步骤**
1. 选择 DELETE 方法
2. 路径填写：`/actions/act_501`
3. 点击「发送」

**完整 URL**
```
DELETE http://localhost:8000/api/v1/actions/act_501
```

**预期响应** (204 No Content)

---

### 4.5 重新提取待办

**接口信息**
- 方法：POST
- 路径：`/meetings/{meeting_id}/actions/extract`

**Apifox 操作步骤**
1. 选择 POST 方法
2. 路径填写：`/meetings/meet_a7b2c9/actions/extract`
3. 不需要 Body
4. 点击「发送」

**完整 URL**
```
POST http://localhost:8000/api/v1/meetings/meet_a7b2c9/actions/extract
```

**预期响应** (202 Accepted)
```json
{
  "meeting_id": "meet_a7b2c9",
  "job_id": "job_a2m9p0",
  "status": "running"
}
```

---

### 4.6 同步待办到飞书

**接口信息**
- 方法：POST
- 路径：`/actions/{action_id}/sync/feishu`
- 功能：将待办事项同步到飞书任务

**Apifox 操作步骤**
1. 选择 POST 方法
2. 路径填写：`/actions/act_501/sync/feishu`
3. 参数通过 Query 传递（不需要 Body）

**Query 参数**
| 参数 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| target | string | 否 | task | 同步目标类型 |
| notify_owner | boolean | 否 | true | 是否通知负责人 |

**完整 URL**
```
POST http://localhost:8000/api/v1/actions/act_501/sync/feishu?target=task&notify_owner=true
```

**预期响应** (200 OK)
```json
{
  "action_id": "act_501",
  "provider": "feishu",
  "external_id": "feishu_task_123",
  "status": "synced",
  "synced_at": "2026-05-16T11:40:00"
}
```

---

## 五、决策记录接口

### 5.1 获取会议决策

**接口信息**
- 方法：GET
- 路径：`/meetings/{meeting_id}/decisions`
- 功能：获取会议中产生的所有决策记录

**Apifox 操作步骤**
1. 选择 GET 方法
2. 路径填写：`/meetings/meet_a7b2c9/decisions`
3. 点击「发送」

**完整 URL**
```
GET http://localhost:8000/api/v1/meetings/meet_a7b2c9/decisions
```

**预期响应** (200 OK)
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
      "created_at": "2026-05-16T10:20:00"
    },
    {
      "id": "dec_302",
      "topic": "任务负责人",
      "decision": "王五负责支付回调修复",
      "version": 1,
      "source_chunk_id": "chunk_1004",
      "created_at": "2026-05-16T10:20:00"
    },
    {
      "id": "dec_303",
      "topic": "测试策略",
      "decision": "周四前完成支付回调回归测试",
      "version": 1,
      "source_chunk_id": "chunk_1005",
      "created_at": "2026-05-16T10:20:00"
    }
  ]
}
```

---

### 5.2 获取决策冲突

**接口信息**
- 方法：GET
- 路径：`/meetings/{meeting_id}/conflicts`
- 功能：获取本次会议与历史会议的决策冲突

**Apifox 操作步骤**
1. 选择 GET 方法
2. 路径填写：`/meetings/meet_a7b2c9/conflicts`
3. 点击「发送」

**完整 URL**
```
GET http://localhost:8000/api/v1/meetings/meet_a7b2c9/conflicts
```

**预期响应** (200 OK)
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

**level 可选值**：`low` | `medium` | `high`

---

### 5.3 重新检测决策冲突

**接口信息**
- 方法：POST
- 路径：`/meetings/{meeting_id}/conflicts/detect`

**Apifox 操作步骤**
1. 选择 POST 方法
2. 路径填写：`/meetings/meet_a7b2c9/conflicts/detect`
3. 不需要 Body
4. 点击「发送」

**完整 URL**
```
POST http://localhost:8000/api/v1/meetings/meet_a7b2c9/conflicts/detect
```

**预期响应** (202 Accepted)
```json
{
  "meeting_id": "meet_a7b2c9",
  "job_id": "job_f8q1v6",
  "status": "running"
}
```

---

## 六、智能问答接口

### 6.1 单次问答

**接口信息**
- 方法：POST
- 路径：`/qa`
- 功能：基于会议内容进行智能问答

**Apifox 操作步骤**
1. 选择 POST 方法
2. 路径填写：`/qa`
3. 选择「Body」→ `JSON`

**请求体字段**
| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| meeting_id | string | 否 | 会议ID，scope 为 all_meetings 时可不传 |
| question | string | 是 | 问题内容 |
| scope | string | 否 | 搜索范围，默认 current_meeting |

**scope 可选值**
| 值 | 说明 |
|----|------|
| current_meeting | 仅搜索当前会议 |
| all_meetings | 搜索所有会议 |

**测试用例**

### 用例 1：询问延期原因

**Body (JSON)**：
```json
{
  "meeting_id": "meet_a7b2c9",
  "question": "支付模块延期是谁提出的？",
  "scope": "current_meeting"
}
```

**预期响应** (200 OK)
```json
{
  "answer": "支付模块延期由张三提出，原因是第三方回调问题尚未解决。",
  "citations": [
    {
      "meeting_id": "meet_a7b2c9",
      "chunk_id": "chunk_1001",
      "speaker": "张三",
      "start": 0.0,
      "end": 4.25,
      "text": "大家好，今天主要对齐一下支付模块的延期问题。"
    },
    {
      "meeting_id": "meet_a7b2c9",
      "chunk_id": "chunk_1002",
      "speaker": "李四",
      "start": 4.5,
      "end": 12.8,
      "text": "支付模块由于第三方回调问题，需要延期到周五完成。"
    }
  ]
}
```

---

### 用例 2：询问责任人

**Body (JSON)**：
```json
{
  "meeting_id": "meet_a7b2c9",
  "question": "谁负责支付回调修复？",
  "scope": "current_meeting"
}
```

**预期响应**
```json
{
  "answer": "王五负责支付回调修复，需要在周四前反馈进度。",
  "citations": [
    {
      "meeting_id": "meet_a7b2c9",
      "chunk_id": "chunk_1004",
      "speaker": "张三",
      "start": 21.0,
      "end": 28.3,
      "text": "同意，王五你负责跟进支付回调的修复，周四前给我反馈。"
    }
  ]
}
```

---

### 用例 3：自定义问题

**Body (JSON)**：
```json
{
  "meeting_id": "meet_a7b2c9",
  "question": "本次会议讨论了哪些风险？",
  "scope": "current_meeting"
}
```

**预期响应**：返回模拟回答，citations 指向相关切片

---

### 6.2 跨会议语义检索

**接口信息**
- 方法：POST
- 路径：`/memory/search`
- 功能：跨会议进行语义搜索

**Apifox 操作步骤**
1. 选择 POST 方法
2. 路径填写：`/memory/search`
3. 参数通过 Query 传递（不需要 Body）

**Query 参数**
| 参数 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| query | string | 是 | - | 搜索内容 |
| limit | int | 否 | 5 | 返回条数上限 |

**完整 URL**
```
POST http://localhost:8000/api/v1/memory/search?query=支付模块延期之前讨论过吗？&limit=5
```

**预期响应** (200 OK)
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
    },
    {
      "meeting_id": "meet_a7b2c9",
      "meeting_title": "产品迭代周会",
      "chunk_id": "chunk_1002",
      "speaker": "李四",
      "start": 4.5,
      "end": 12.8,
      "text": "支付模块由于第三方回调问题，需要延期到周五完成。",
      "score": 0.85
    }
  ]
}
```

---

### 6.3 获取知识图谱

**接口信息**
- 方法：GET
- 路径：`/meetings/{meeting_id}/graph`
- 功能：获取会议的知识图谱，包含人物、任务、话题等节点及关系

**Apifox 操作步骤**
1. 选择 GET 方法
2. 路径填写：`/meetings/meet_a7b2c9/graph`
3. 点击「发送」

**完整 URL**
```
GET http://localhost:8000/api/v1/meetings/meet_a7b2c9/graph
```

**预期响应** (200 OK)
```json
{
  "nodes": [
    {"id": "person_zhangsan", "label": "张三", "type": "person"},
    {"id": "person_lisi", "label": "李四", "type": "person"},
    {"id": "person_wangwu", "label": "王五", "type": "person"},
    {"id": "task_payment_callback", "label": "修复支付回调", "type": "task"},
    {"id": "task_update_doc", "label": "更新上线计划文档", "type": "task"},
    {"id": "topic_payment_module", "label": "支付模块", "type": "topic"},
    {"id": "topic_launch_date", "label": "上线时间", "type": "topic"}
  ],
  "edges": [
    {"source": "person_zhangsan", "target": "task_update_doc", "type": "负责"},
    {"source": "person_wangwu", "target": "task_payment_callback", "type": "负责"},
    {"source": "person_zhangsan", "target": "topic_payment_module", "type": "提及"},
    {"source": "person_lisi", "target": "topic_payment_module", "type": "提及"},
    {"source": "person_wangwu", "target": "topic_launch_date", "type": "提议"}
  ]
}
```

**节点类型**：`person`（人物）、`task`（任务）、`topic`（话题）

---

### 6.4 图谱查询

**接口信息**
- 方法：POST
- 路径：`/graph/query`
- 功能：基于知识图谱进行自然语言查询

**Apifox 操作步骤**
1. 选择 POST 方法
2. 路径填写：`/graph/query`
3. 参数通过 Query 传递（不需要 Body）

**Query 参数**
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| question | string | 是 | 查询问题 |

**完整 URL**
```
POST http://localhost:8000/api/v1/graph/query?question=最近三次会议张三负责了哪些任务？
```

**预期响应** (200 OK)
```json
{
  "answer": "最近三次会议中，张三负责支付回调修复跟进、上线计划文档更新和接口联调协调。",
  "nodes": [
    {"id": "person_zhangsan", "label": "张三", "type": "person"},
    {"id": "task_payment_callback", "label": "修复支付回调", "type": "task"},
    {"id": "task_update_doc", "label": "更新上线计划文档", "type": "task"}
  ],
  "edges": [
    {"source": "person_zhangsan", "target": "task_payment_callback", "type": "跟进"},
    {"source": "person_zhangsan", "target": "task_update_doc", "type": "负责"}
  ]
}
```

---

## 七、WebSocket 流式问答

### 7.1 流式问答连接

**连接信息**
- WebSocket URL：`ws://localhost:8000/api/v1/chat`

**Apifox 配置步骤**
1. 新建接口，选择 **WebSocket** 类型
2. URL 填写：`ws://localhost:8000/api/v1/chat`
3. 点击「连接」

**连接成功后，发送消息**
```json
{
  "type": "question",
  "meeting_id": "meet_a7b2c9",
  "question": "支付模块延期是谁提出的？",
  "scope": "current_meeting"
}
```

**接收消息格式**

1. 开始消息：
```json
{
  "type": "start",
  "message": ""
}
```

2. 内容块（逐字推送，多个）：
```json
{
  "type": "chunk",
  "message": "支付模块延期"
}
```

3. 结束消息：
```json
{
  "type": "end",
  "message": "",
  "citations": [
    {
      "meeting_id": "meet_a7b2c9",
      "chunk_id": "chunk_1001",
      "speaker": "张三",
      "start": 0.0,
      "end": 4.25,
      "text": "大家好，今天主要对齐一下支付模块的延期问题。"
    }
  ]
}
```

4. 错误消息：
```json
{
  "type": "error",
  "code": "QA_FAILED",
  "message": "问答生成失败"
}
```

---

### 7.2 会议事件推送

**连接信息**
- WebSocket URL：`ws://localhost:8000/api/v1/meetings/{meeting_id}/events`
- 示例：`ws://localhost:8000/api/v1/meetings/meet_a7b2c9/events`

**Apifox 配置步骤**
1. 新建接口，选择 **WebSocket** 类型
2. URL 填写：`ws://localhost:8000/api/v1/meetings/meet_a7b2c9/events`
3. 点击「连接」

**连接成功后自动接收进度推送**
```json
{
  "type": "job_progress",
  "job_id": "job_transcription_meet_a7b2c9",
  "job_type": "transcription",
  "status": "running",
  "progress": 20,
  "message": "正在处理 transcription... 20%"
}
```

**推送的任务类型**：transcription → summary → action → memory → graph → conflict

**发送心跳**
```json
{
  "action": "ping"
}
```

**响应**
```json
{
  "type": "pong"
}
```

---

## 八、测试顺序建议

### 第一阶段：基础功能验证

按以下顺序测试：

1. **健康检查** - GET `/health`
2. **创建会议** - POST `/meetings`
3. **获取会议列表** - GET `/meetings`
4. **获取会议详情** - GET `/meetings/{meeting_id}`
5. **更新会议** - PATCH `/meetings/{meeting_id}`

### 第二阶段：转录相关

6. **获取转录** - GET `/meetings/{meeting_id}/transcripts`
7. **更新转录** - PATCH `/transcripts/{chunk_id}`

### 第三阶段：智能分析

8. **获取纪要** - GET `/meetings/{meeting_id}/summary`
9. **获取待办** - GET `/meetings/{meeting_id}/actions`
10. **创建待办** - POST `/meetings/{meeting_id}/actions`
11. **更新待办** - PATCH `/actions/{action_id}`
12. **获取决策** - GET `/meetings/{meeting_id}/decisions`

### 第四阶段：高级功能

13. **智能问答** - POST `/qa`
14. **WebSocket 问答** - WS `/chat`
15. **知识图谱** - GET `/meetings/{meeting_id}/graph`
16. **语义检索** - POST `/memory/search`

### 第五阶段：删除操作

17. **删除待办** - DELETE `/actions/{action_id}`
18. **删除会议** - DELETE `/meetings/{meeting_id}`

---

## 九、常见问题排查

### 问题 1：连接被拒绝

**现象**：`Connection refused`

**解决方案**：
1. 检查后端服务是否启动
2. 检查端口是否正确（默认 8000）
3. 检查防火墙设置

### 问题 2：404 Not Found

**现象**：接口返回 404

**解决方案**：
1. 检查 URL 路径是否正确
2. 检查是否添加了 `/api/v1` 前缀
3. 检查路径参数是否正确（如 meeting_id 是否有效）

### 问题 3：422 Validation Error

**现象**：请求参数验证失败

**解决方案**：
1. 检查请求体 JSON 格式是否正确
2. 检查必填字段是否填写
3. 检查字段类型是否匹配
4. 检查字符串长度限制
5. **注意**：PATCH 请求的参数要放在 Body（JSON）中，不是 Query 参数中

### 问题 4：PATCH 请求 Body 为空

**现象**：返回 422，提示 `Field required`，`input: null`

**解决方案**：
1. 不要把参数填在 Query 参数中
2. 切换到「Body」标签页
3. 选择 `JSON` 格式
4. 在 Body 中填写 JSON 数据

---

## 十、Mock 数据汇总

当前所有接口返回的都是 Mock 数据，主要用于前端联调测试。

### 会议数据
| 会议ID | 标题 | 状态 | 标签 |
|--------|------|------|------|
| meet_a7b2c9 | 产品迭代周会 | completed | ["产品", "周会"] |
| meet_b8c1d2 | 支付系统技术评审 | completed | ["技术", "支付"] |
| meet_c3d4e5 | Q3 产品规划会 | transcribing | ["产品", "规划"] |

### 转录切片数据
| 切片ID | 说话人 | 时间段 | 内容摘要 |
|--------|--------|--------|----------|
| chunk_1001 | 张三 | 0.0-4.25 | 对齐支付模块延期问题 |
| chunk_1002 | 李四 | 4.5-12.8 | 第三方回调问题需延期 |
| chunk_1003 | 王五 | 13.0-20.5 | 建议推迟到周五上线 |
| chunk_1004 | 张三 | 21.0-28.3 | 安排王五跟进修复 |
| chunk_1005 | 王五 | 28.5-32.0 | 确认处理 |

### 待办数据
| 待办ID | 任务 | 负责人 | 优先级 | 状态 |
|--------|------|--------|--------|------|
| act_501 | 修复支付回调失败问题 | 王五 | high | todo |
| act_502 | 补充支付回调异常日志 | 王五 | medium | doing |
| act_503 | 更新上线计划文档 | 张三 | low | done |

### 决策数据
| 决策ID | 主题 | 决策内容 | 版本 |
|--------|------|----------|------|
| dec_301 | 上线时间 | 支付模块延期到周五上线 | 2 |
| dec_302 | 任务负责人 | 王五负责支付回调修复 | 1 |
| dec_303 | 测试策略 | 周四前完成支付回调回归测试 | 1 |

实际开发中，这些数据会从数据库中读取。
