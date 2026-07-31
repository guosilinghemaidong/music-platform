import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

// 后端路由前缀列表（所有 FastAPI 路由的 prefix）
// 开发时，Vite 把这些前缀的请求代理到后端；Docker 时由 Nginx 代理
const apiPrefixes = [
  '/user', '/music', '/singer', '/album', '/category',
  '/collection', '/like', '/follow', '/comment', '/post',
  '/admin', '/upload', '/static', '/health', '/test-redis', '/search', '/playlist'
]

// 自动生成 proxy 配置（不用手写 14 个重复的配置）
const proxyConfig = {}
apiPrefixes.forEach(prefix => {
  proxyConfig[prefix] = {
    target: 'http://localhost:8000',
    changeOrigin: true
  }
})

// https://vite.dev/config/
export default defineConfig({
  plugins: [vue()],
  server: {
    proxy: proxyConfig
  }
})
