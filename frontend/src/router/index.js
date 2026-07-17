import { createRouter, createWebHistory } from 'vue-router'
import Login from '../views/Login.vue'
import Register from '../views/Register.vue'

// 定义路由规则
const routes = [
  {
    path: '/',           // 访问根路径
    redirect: '/login'   // 自动跳转到登录页
  },
  {
    path: '/login',      // 登录页
    component: Login
  },
  {
    path: '/register',   // 注册页
    component: Register
  }
]

// 创建路由实例
const router = createRouter({
  history: createWebHistory(),  // 使用 HTML5 历史模式
  routes
})

export default router
