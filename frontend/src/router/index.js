import { createRouter, createWebHistory } from 'vue-router'
import Login from '../views/Login.vue'
import Register from '../views/Register.vue'
import UserLayout from '../layouts/UserLayout.vue'
import AdminLayout from '../layouts/AdminLayout.vue'
import Home from '../views/Home.vue'
import Discover from '../views/Discover.vue'
import MyCollection from '../views/MyCollection.vue'
import Profile from '../views/Profile.vue'
import About from '../views/About.vue'
import AdminHome from '../views/admin/AdminHome.vue'
import AdminMusic from '../views/admin/AdminMusic.vue'
import AdminAddMusic from '../views/admin/AdminAddMusic.vue'

const routes = [
  { path: '/', redirect: '/login' },
  { path: '/login', component: Login },
  { path: '/register', component: Register },
  // 用户端路由
  {
    path: '/',
    component: UserLayout,
    children: [
      { path: 'home', component: Home },
      { path: 'discover', component: Discover },
      { path: 'collection', component: MyCollection },
      { path: 'profile', component: Profile },
      { path: 'about', component: About }
    ]
  },
  // 管理员路由
  {
    path: '/admin',
    component: AdminLayout,
    children: [
      { path: '', component: AdminHome },
      { path: 'music', component: AdminMusic },
      { path: 'add-music', component: AdminAddMusic }
    ]
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router
