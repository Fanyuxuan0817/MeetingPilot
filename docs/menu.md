MeetingPilot/
├── README.md                           # 项目说明文档
├── PRD.md                              # 需求文档
├── frontend-dev.md                     # 前端开发规范指南
├── docker-compose.yml                  # 本地开发环境编排 (DBs, Redis)
├── .env.example                        # 全局环境变量示例
├── docs/                               # 架构设计与文档说明
│   ├── architecture.md
│   ├── api.md
│   ├── database.md
│   └── agent-flow.md
│
├── frontend/                           # Vue 3 前端工程 (Vite + Tailwind) 🚀 
│   ├── package.json
│   ├── vite.config.ts                  # Vite 配置文件
│   ├── tailwind.config.js              # Tailwind 配置文件
│   ├── tsconfig.json                   # TypeScript 配置 (推荐使用 TS)
│   ├── index.html                      # 单页面应用入口
│   │
│   ├── src/
│   │   ├── main.ts                     # Vue 入口文件
│   │   ├── App.vue                     # 根组件
│   │   │
│   │   ├── api/                        # 接口请求模块 (Axios 封装)
│   │   │   ├── client.ts               # Axios 实例及拦截器
│   │   │   ├── meetings.ts             # 会议、录音、转录核心 API
│   │   │   ├── agents.ts               # 纪要、待办、高级 Agent 相关 API
│   │   │   └── qa.ts                   # 问答服务 API
│   │   │
│   │   ├── assets/                     # 静态资源 (图片、卡通猫 Coach 素材)
│   │   │   ├── images/
│   │   │   └── styles/
│   │   │       └── tailwind.css        # 全局样式引入
│   │   │
│   │   ├── components/                 # 组件层 (解耦复用)
│   │   │   ├── common/                 # 通用基础组件 (如 Navbar, Sidebar)
│   │   │   ├── audio/                  # 音频组件
│   │   │   │   ├── AudioPlayer.vue     # 音频播放器外壳
│   │   │   │   └── Waveform.vue        # 音频播放器的波形视图
│   │   │   ├── meeting/                # 会议公共组件
│   │   │   ├── transcript/             # 转录文本展示与高亮组件
│   │   │   │   └── TranscriptList.vue  # 说话人切片列表 (联动波形)
│   │   │   ├── summary/                # 纪要展示组件
│   │   │   ├── qa/                     # 智能问答组件
│   │   │   │   ├── ChatBubble.vue      # 问答气泡
│   │   │   │   └── AgentChat.vue       # 智能问答对话面板
│   │   │   └── ui/                     # 简约/可爱风格的原子 UI 组件 (如 Button, Card)
│   │   │
│   │   ├── composables/                # Vue 3 组合式 API (核心逻辑封装)
│   │   │   ├── useWaveSurfer.ts        # 统管音轨初始化与精准时间跳转
│   │   │   └── useWebSocket.ts         # 统管与 QA Agent 的流式对话通信
│   │   │
│   │   ├── router/                     # Vue Router 路由配置
│   │   │   └── index.ts                # 定义 Dashboard, MeetingDetail 等路由
│   │   │
│   │   ├── stores/                     # Pinia 状态管理
│   │   │   ├── meeting.ts              # 存储当前会议、转录 Text Chunks 状态
│   │   │   └── agent.ts                # 存储 Agent 状态、问答上下文
│   │   │
│   │   ├── types/                      # TypeScript 类型声明
│   │   │   └── index.ts                # 对应后端 Pydantic Schema 的前端类型
│   │   │
│   │   └── views/                      # 页面级组件 (视图)
│   │       ├── Dashboard.vue           # 首页 / 会议列表工作台
│   │       ├── MeetingDetail.vue       # 会议详情页 (核心双栏：左看文本/右调 Agent)
│   │       └── Settings.vue            # 系统设置
│   │
│   └── public/                         # 纯静态资源 (不参与 Vite 编译)
│
├── backend/                            # FastAPI 后端核心 🐍 【对齐优化】
│   ├── pyproject.toml
│   ├── alembic.ini                     # 数据库迁移配置
│   │
│   ├── app/
│   │   ├── main.py                     # FastAPI 应用程序入口
│   │   │
│   │   ├── core/                       # 全局核心配置
│   │   │   ├── config.py
│   │   │   ├── logging.py
│   │   │   ├── security.py
│   │   │   └── exceptions.py
│   │   │
│   │   ├── api/                        # 路由控制层 (对接前端 api/)
│   │   │   ├── router.py               # 根路由聚合
│   │   │   └── v1/                     # V1 版本 API
│   │   │       ├── meetings.py         # 会议生命周期管理
│   │   │       ├── transcripts.py      # 转录文本查询
│   │   │       ├── summaries.py        # 结构化纪要
│   │   │       ├── actions.py          # 待办事项
│   │   │       ├── decisions.py        # 决策冲突检测
│   │   │       └── chat.py             # 统一问答 (含 REST 与 WebSocket) 🧩
│   │   │
│   │   ├── models/                     # 关系型数据库模型 (SQLAlchemy)
│   │   │   ├── base.py                 # Base 基类定义
│   │   │   ├── meeting.py              # meeting 主表
│   │   │   ├── transcript.py           # transcript_chunk 表
│   │   │   ├── action_item.py          # action_item 表
│   │   │   ├── decision.py             # decision_record 表
│   │   │   └── user.py                 # 用户表
│   │   │
│   │   ├── schemas/                    # Pydantic 模型 (前后端契约)
│   │   │   ├── meeting.py              # 会议出入参验证
│   │   │   ├── transcript.py           # 转录文本切片定义
│   │   │   ├── action_item.py          # 待办项字段定义
│   │   │   ├── decision.py             # 决策字段定义
│   │   │   ├── summary.py              # 结构化纪要定义
│   │   │   ├── qa.py                   # 问答请求/响应格式
│   │   │   └── common.py               # 通用响应模型 (分页、任务状态等)
│   │   │
│   │   ├── repositories/               # 数据库原子操作层 (DAO)
│   │   │   ├── meeting_repo.py         # 专职对 meeting 表的 CRUD
│   │   │   ├── transcript_repo.py
│   │   │   ├── action_repo.py
│   │   │   └── decision_repo.py
│   │   │
│   │   ├── services/                   # 传统业务逻辑层 (上承 API，下接 Repo)
│   │   │   ├── meeting_service.py      # 会议创建与流转
│   │   │   ├── audio_service.py        # 音频管理、分块、转码
│   │   │   └── transcription_service.py# 封装 Faster-Whisper/pyannote 调度
│   │   │
│   │   ├── agents/                     # 智能编排层 (LangGraph 中心)
│   │   │   ├── graph.py                # LangGraph 状态机定义与编译
│   │   │   ├── state.py                # AgentState 状态定义
│   │   │   ├── router_agent.py         # 路由分发决策
│   │   │   └── nodes/                  # 拆分为具体 Node，对应 PRD 各大 Agent 🛠️
│   │   │       ├── summary_node.py     # 摘要提取节点
│   │   │       ├── action_node.py      # 待办提取节点
│   │   │       ├── memory_node.py      # 长期记忆检索节点
│   │   │       ├── graph_node.py       # 知识图谱构建节点
│   │   │       ├── conflict_node.py    # 冲突检测节点
│   │   │       ├── qa_node.py          # 问答推理节点
│   │   │       └── execution_node.py   # 工具执行节点 (飞书同步)
│   │   │
│   │   ├── clients/                    # 三方基础设施客户端 (取代原 integrations) 🌐
│   │   │   ├── whisper_client.py       # WhisperX 远程或本地调用
│   │   │   ├── qdrant_client.py        # Qdrant 向量存储
│   │   │   ├── neo4j_client.py         # Neo4j 图数据库
│   │   │   ├── redis_client.py         # Redis 缓存与队列客户端
│   │   │   └── feishu_client.py        # 飞书开放平台 SDK 封装
│   │   │
│   │   ├── workers/                    # 异步任务处理 (结合 Redis/Celery)
│   │   │   ├── queue.py                # 队列初始化
│   │   │   ├── audio_jobs.py           # 异步音频转录任务
│   │   │   └── agent_jobs.py           # 异步 Agent 编排任务
│   │   │
│   │   └── utils/                      # 通用工具类
│   │       ├── time.py
│   │       ├── text.py
│   │       └── file.py
│   │
│   ├── migrations/                     # Alembic 数据库迁移文件
│   ├── tests/                          # 自动化测试
│   └── storage/                        # 本地持久化数据暂存 (生产环境映射到卷)
│       ├── audio/
│       ├── transcripts/
│       └── exports/
│
├── infra/                              # 容器化基础设施配置文件
│   ├── postgres/                       # pgvector 插件初始化配置
│   ├── redis/
│   ├── qdrant/
│   ├── neo4j/
│   └── nginx/
│
└── scripts/                            # 自动化脚本
    ├── dev.sh                          # 一键启动后端 + 基础设施
    ├── migrate.sh                      # 执行数据库迁移
    └── seed.py                         # 填充测试会议数据