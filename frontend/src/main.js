import { createApp } from 'vue'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import { createPinia } from 'pinia'   // 导入 Pinia（全局状态管理）
import App from './App.vue'
import router from './router'  // 导入路由（下一步创建）

const app = createApp(App)
const pinia = createPinia()  // 创建 Pinia 实例

app.use(ElementPlus)  // 注册 Element Plus
app.use(router)       // 注册路由
app.use(pinia)        // 注册 Pinia（全局状态管理）

app.mount('#app')
