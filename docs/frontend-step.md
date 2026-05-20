# MeetingPilot 前端开发步骤文档

## 第一阶段：环境搭建与基础架构

在动手写业务代码前，必须先理顺基础架构，确保后续开发不乱。

1. **清理项目骨架**
* 删除 `src/components/HelloWorld.vue` 及所有初始化的 `assets` 图片。
* 在 `App.vue` 中清空默认样式，只保留 `<router-view />`。


2. **集成 Tailwind CSS (简约可爱风基础)**
* 配置 `tailwind.config.js`，建议加入一些浅粉、粉紫的自定义色调，以符合你偏好的 UI 风格。
* 在 `main.ts` 中引入 Tailwind 的基础指令。


3. **建立标准目录**
* 在 `src` 下手动创建以下文件夹：
* `api/`: 存放 Axios 接口定义。
* `types/`: 存放 TypeScript 接口定义。
* `composables/`: 存放组合式逻辑（如音频控制）。
* `stores/`: Pinia 状态库。





---

## 第二阶段：定义“数据契约” (TypeScript & API)

这是全栈开发的灵魂，确保前端数据结构与后端 PostgreSQL/Pydantic 完全对齐。

1. **定义核心类型 (`src/types/meeting.ts`)**
* 根据 PRD 定义 `Meeting`、`TranscriptChunk`（转录切片）和 `ActionItem`（待办事项）的接口。


2. **封装 Axios 客户端 (`src/api/client.ts`)**
* 创建一个指向 `http://localhost:8000/api/v1` 的 Axios 实例。


3. **编写 Mock 请求**
* 在 `src/api/meetings.ts` 中写好获取会议详情和转录列表的方法。



---

## 第三阶段：核心“音文联动”模块开发 (重点)

这是 PRD 中提到的项目最大亮点：**可追溯性**。

1. **开发音频逻辑 (`src/composables/useWaveSurfer.ts`)**
* 利用 `WaveSurfer.js` 初始化音频波形。
* **关键任务**：监听 `timeupdate` 事件，并将当前播放时间同步到 Pinia 的 `currentTime` 状态中。


2. **构建波形组件 (`src/components/audio/Waveform.vue`)**
* 渲染音频波形，支持点击波形跳转时间。


3. **构建转录列表 (`src/components/transcript/TranscriptList.vue`)**
* **逻辑实现**：
* 使用 `v-for` 渲染转录文本。
* **高亮**：判断 `currentTime` 是否在某段文本的 `start` 和 `end` 之间，若是则改变背景色。
* **跳转**：点击文字，调用 `wavesurfer.setTime()` 跳转音频。





---

## 第四阶段：AI Agent 交互与分析面板

实现多 Agent 协作层在前端的展示。

1. **设计侧边栏分析面板**
* **摘要模块**：展示 `Summary Agent` 生成的结构化会议主题和议题。
* **待办模块**：展示 `Action Agent` 提取的任务、负责人和截止日期。


2. **开发智能对话框 (`src/components/qa/AgentChat.vue`)**
* **WebSocket 通信**：连接后端的 `QA Agent` 实现实时流式回答。
* **引用回溯**：如果 AI 回答中附带了原文时间戳，点击该回答应能触发音频跳转。



---

## 第五阶段：布局组装与 UI 润色

1. **页面路由配置**
* `/`: 仪表盘（Dashboard），展示历史会议列表。
* `/meeting/:id`: 会议工作台（核心详情页）。


2. **加入“可爱风”元素**
* 在角落或加载动画中加入你的卡通猫 Coach 形象。
* 使用圆角和马卡龙色系的 UI 按钮。



---
