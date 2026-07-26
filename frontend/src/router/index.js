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
import AdminSinger from '../views/admin/AdminSinger.vue'
import AdminAlbum from '../views/admin/AdminAlbum.vue'
import AdminCategory from '../views/admin/AdminCategory.vue'
import AdminPost from '../views/admin/AdminPost.vue'
import Community from '../views/Community.vue'
import Follow from '../views/Follow.vue'

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
      { path: 'community', component: Community },
      { path: 'follow', component: Follow },
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
      { path: 'singer', component: AdminSinger },
      { path: 'album', component: AdminAlbum },
      { path: 'category', component: AdminCategory },
      { path: 'add-music', component: AdminAddMusic },
      { path: 'music', component: AdminMusic },
      { path: 'post', component: AdminPost }
    ]
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// ========== 路由守卫：未登录自动跳转登录页 ==========
// 白名单：不需要登录就能访问的页面
const publicPages = ['/login', '/register']

router.beforeEach((to, from, next) => {
  const token = localStorage.getItem('token')

  if (token) {
    // 已登录状态下，访问登录/注册页会自动跳转到首页
    if (publicPages.includes(to.path)) {
      next('/home')
    } else {
      next()
    }
  } else {
    // 未登录：只允许访问登录和注册页，其他页面一律跳回登录
    if (publicPages.includes(to.path)) {
      next()
    } else {
      next('/login')
    }
  }
})

export default router
