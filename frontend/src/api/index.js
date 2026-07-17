import axios from 'axios'

// 创建 axios 实例，配置后端地址
const api = axios.create({
  baseURL: 'http://localhost:8000'  // 后端地址
})

export default api
