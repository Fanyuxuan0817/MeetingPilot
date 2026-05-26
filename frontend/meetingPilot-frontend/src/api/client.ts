import axios, { type AxiosResponse } from 'axios'
import { ElMessage } from 'element-plus'

const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL ?? '/api/v1',
  timeout: 30_000,
  headers: {
    'Content-Type': 'application/json',
  },
})

apiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  },
)

apiClient.interceptors.response.use(
  (response: AxiosResponse) => {
    return response.data as any
  },
  (error) => {
    if (error.response) {
      const status = error.response.status
      const errorData = error.response.data

      const message = errorData?.detail || errorData?.message || '系统开小差了，请稍后再试'

      if (status === 401) {
        localStorage.removeItem('token')
        ElMessage.error('登录已过期，请重新登录')

        setTimeout(() => {
          window.location.href = '/login'
        }, 1200)
      } else {
        ElMessage.error(message)
      }

      return Promise.reject(errorData || error)
    }

    ElMessage.error('网络连接失败，请检查网络或后端服务')
    return Promise.reject(error)
  },
)

export default apiClient
