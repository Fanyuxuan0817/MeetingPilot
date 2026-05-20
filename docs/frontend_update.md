# 🛠 MeetingPilot 前端基础设施修改文档

## 1. 环境变量配置 (`.env.development`)

为了让 `client.ts` 能够动态识别后端地址，并为后续接入 Apifox Mock 或正式后端做好准备，请在前端项目的**根目录**（与 `package.json` 同级）检查或创建该文件。

* **文件路径**：`frontend/meetingPilot-frontend/.env.development`
* **文件内容**：

```env
# 本地开发环境：后端 FastAPI 的基础 API 地址
VITE_API_BASE_URL=http://localhost:8000/api/v1

```

---

## 2. 网络网络封装升级 (`src/api/client.ts`)

请使用以下完整代码**直接覆盖**你原有的 `src/api/client.ts` 文件。该版本保留了你的结构，升级了双向拦截器。

* **文件路径**：`frontend/meetingPilot-frontend/src/api/client.ts`
* **完整代码**：

```typescript
import axios from 'axios'
import { ElMessage } from 'element-plus' // 引入 Element Plus 的轻提示用于统一报错

// 创建 axios 实例
const apiClient = axios.create({
  // 优先读取环境变量，若无则使用你原有的 '/api/v1' 兜底
  baseURL: import.meta.env.VITE_API_BASE_URL ?? '/api/v1',
  timeout: 30_000, // 保持你原本的 30 秒长超时，非常适合 AI 流式响应与音频转录
  headers: {
    'Content-Type': 'application/json',
  },
})

/**
 * 1. 请求拦截器 (Request Interceptor)
 * 作用：每次向后端发起请求前，自动从本地缓存提取 Token 并注入到 Header 中
 */
apiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token')
    if (token) {
      // 遵循 Bearer Token 规范
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

/**
 * 2. 响应拦截器 (Response Interceptor)
 * 作用：集中过滤后端返回的数据与网络状态码，实现防御性开发
 */
apiClient.interceptors.response.use(
  (response) => {
    // 【无损解包】直接返回解包后的业务数据，后续在业务组件中无需再写 res.data.data
    return response.data
  },
  (error) => {
    // 统一错误处理边界
    if (error.response) {
      const status = error.response.status
      const errorData = error.response.data
      
      // 兼容 FastAPI 的标准错误响应格式：{ detail: "错误信息" }
      const message = errorData?.detail || errorData?.message || '系统开小差了，请稍后再试'

      // 核心契约：处理 401 登录失效或 Token 过期
      if (status === 401) {
        localStorage.removeItem('token') // 清理残留脏数据
        ElMessage.error('登录已过期，请重新登录')
        
        // 延迟 1.2 秒跳转，留出足够时间让用户看清提示弹窗
        setTimeout(() => {
          window.location.href = '/login'
        }, 1200)
      } else {
        // 其他非 401 错误（如 400 参数错误、500 服务器崩溃），自动弹出后端返回的错误内容
        ElMessage.error(message)
      }

      return Promise.reject(errorData || error)
    }

    // 处理网络断开、跨域、或请求超时的极端边界情况
    ElMessage.error('网络连接失败，请检查网络或后端服务')
    return Promise.reject(error)
  },
)

// 保持原本的默认导出，确保其他写好的业务 API 文件无需修改 import 语句
export default apiClient

```

---

## 3. 升级带来的改动与对齐说明

完成上述修改后，你原有的代码资产将获得以下质的飞跃：

1. **向后兼容性**：因为导出的依然是 `apiClient`，你之前在 `meeting.ts` 里写的 `import apiClient from './client'` **完全不需要做任何改动**。
2. **数据层级精简**：
* *以前*：你在业务组件中拿到数据可能需要写 `const data = res.data.data`。
* *现在*：由于响应拦截器内部执行了 `return response.data`，你在组件中直接 `const data = await getMeetings()` 即可直接拿到后端返回的 JSON 数据主体。


3. **零负担异常处理**：你原有的业务 API 文件（如 `meeting.ts`）中，可以放心**删掉**所有的 `try {} catch {}`。因为任何一个接口报错（不管是 400 还是 500），`client.ts` 都会自动在页面顶部弹出一个漂亮的 Element Plus 错误提示。

。