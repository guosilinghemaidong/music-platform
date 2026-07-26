import axios from 'axios'

// 创建 axios 实例，配置后端地址
const api = axios.create({
  baseURL: 'http://localhost:8000'  // 后端地址
})

// ========== 请求拦截器：自动带上 Token ==========
// 每次发请求前，自动从 localStorage 取出 token 加到请求头
// 这样就不用每个请求手动写 headers: { Authorization: 'Bearer ' + token }
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token')
  if (token) {
    config.headers.Authorization = 'Bearer ' + token
  }
  return config
})

// ========== 响应拦截器：统一处理 401 错误 ==========
// 后端返回 401（Token 过期或无效）时，自动清除本地 Token 并跳转到登录页
api.interceptors.response.use(
  (response) => response,   // 正常响应直接放行
  (error) => {
    if (error.response && error.response.status === 401) {
      localStorage.removeItem('token')
      localStorage.removeItem('username')
      localStorage.removeItem('role')
      // 避免在登录页重复跳转
      if (window.location.pathname !== '/login') {
        window.location.href = '/login'
      }
    }
    return Promise.reject(error)
  }
)

export default api
