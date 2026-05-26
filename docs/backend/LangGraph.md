# LangGraph 智能编排详细开发手册

本阶段的目标是将 `Whisper` 输出的原始文本，通过多 Agent 协作，转化为具有**长期记忆**和**冲突检测**能力的智能数据。

## 步骤 1：环境搭建与状态定义 (The State)

在 LangGraph 中，状态（State）是所有 Agent 共享的“黑板”。

1. **定义数据模型：** 在 `agents/state.py` 中，使用 `TypedDict` 定义整个图的生命周期变量。
* `transcript`: 存储 `Transcript Agent` 产生的原始文本段落。
* `summary`: 存储 `Summary Agent` 生成的结构化摘要（Markdown 格式）。
* `action_items`: 存储 `Action Agent` 提取的任务列表对象。
* `decisions`: 存储本次会议的核心决策。
* `conflicts`: 存储 `Conflict Agent` 发现的与历史记录不符的矛盾点。
* `next_step`: 用于条件路由，决定下一个执行节点。


2. **实现状态持久化：** 配置 `Checkpointer`，确保会议分析过程中如果发生中断，可以从最后一个状态恢复。

---

## 步骤 2：核心 Agent 节点实现 (The Nodes)

每个节点都是一个异步函数，通过 LLM（如 GPT-4o 或 Claude 3.5）处理特定任务。

### 2.1 结构化摘要节点 (Summary Node)

* **输入：** `state["transcript"]`。
* **Prompt 策略：** 要求 LLM 按照 PRD 定义的结构（主题、议题、结论、未决问题）输出。
* **处理逻辑：** 如果文本过长，采用 Map-Reduce 模式，先对 Chunk 进行摘要，最后进行汇总。

### 2.2 待办提取节点 (Action Node)

* **输入：** `state["transcript"]`。
* **提取逻辑：** 使用 **Instructor** 或 **Pydantic** 强制 LLM 输出 JSON 格式，包含：`task` (任务内容), `owner` (负责人), `deadline` (截止日期)。
* **亮点：** 结合 `speaker` 字段，精准定位任务指派者。

### 2.3 冲突检测节点 (Conflict Node)

* **检索历史：** 根据本次会议的主题，调用 `pgvector` 搜索过去 30 天内相关的 `decision_record` 表。
* **对比逻辑：** 提示词：“这是今天的决策 A，这是历史记录 B。请检查两者在截止日期、负责人或执行方案上是否有冲突？”。
* **输出：** 如果有冲突，生成 `ConflictWarning` 对象存入状态。

---

## 3. 构建多 Agent 图拓扑 (The Graph)

使用 LangGraph 定义 Agent 之间的流转逻辑。我们将采用 PRD 建议的 **Pipeline + Fan-out** 模式。

1. **初始化图：** `workflow = StateGraph(AgentState)`。
2. **添加节点：** 将上述定义的 Node 函数注册到图中。
3. **连接逻辑边 (Edges)：**
* **并行触发 (Fan-out)：** `Router Agent` 处理完文本后，同时指向 `Summary Node`、`Action Node` 和 `Memory Node`。
* **汇总 (Fan-in)：** 使用 `Join` 逻辑，确保所有并行节点返回结果后，再进入 `Graph Agent` 构建关系网络。


4. **设置入口点：** `workflow.set_entry_point("transcript_processor")`。

---

## 4. 数据库与向量存储集成

Agent 产生的结果需要最终落地到 PostgreSQL 和向量库中。

1. **关系型入库：** 在图的最后一个节点（Execution Agent），调用 SQLAlchemy 将 `action_items` 批量插入 `action_item` 表。
2. **向量化：** 使用 `text-embedding-3-small` 将摘要和决策记录转化为向量，存入 `Qdrant` 或 PostgreSQL 的 `vector` 字段，供以后会议的 `Conflict Agent` 检索。
3. **图谱同步：** 将人物与任务的关系（谁负责什么）推送到 `Neo4j`，实现“最近三次会议张三负责了哪些任务”的图查询。

---

## 5. FastAPI 接口联调

将 LangGraph 封装为 API 供前端调用。

1. **异步流式输出：** 使用 `FastAPI` 的 `StreamingResponse`，配合 `graph.astream`，让前端能够实时看到“摘要生成中...”、“待办提取中...”的进度。
2. **WebSocket 状态更新：** 对于耗时较长的会议，通过 Redis 订阅发布机制，在分析完成后向客户端推送通知。

---

## 6. 测试与调优

1. **长文本压力测试：** 测试 2 小时会议（约 3 万字）的转录文本是否会导致 LLM 上下文溢出，必要时引入长文本分段处理策略。
2. **提示词调优：** 针对“待办事项”容易漏掉口头承诺的问题，优化 Prompt 中的少样本学习（Few-shot）示例。

这个阶段完成后，你的 **MeetingPilot** 将不再是一个简单的转录工具，而是一个能够自动追踪任务、预警决策冲突的智能助手。
