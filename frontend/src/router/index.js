import { createRouter, createWebHistory } from 'vue-router'
import Login from '../views/Login.vue'
import Register from '../views/Register.vue'
import Home from '../views/Home.vue'
import AdminHome from '../views/admin/AdminHome.vue'

const routes = [
  {
    path: '/',
    redirect: '/login'
  },
  {
    path: '/login',
    component: Login
  },
  {
    path: '/register',
    component: Register
  },
  {
    path: '/home',        // 普通用户首页
    component: Home
  },
  {
    path: '/admin',       // 管理员首页
    component: AdminHome
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router
