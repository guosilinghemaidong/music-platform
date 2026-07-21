<template>
  <div>
    <h1>用户首页</h1>
    <p>欢迎回来，{{ username }}！</p>
    <el-button @click="handleLogout">退出登录</el-button>
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router'

const router = useRouter()
const username = localStorage.getItem('username') || '用户'

const handleLogout = () => {
  localStorage.removeItem('token')
  localStorage.removeItem('username')
  localStorage.removeItem('role')
  router.push('/login')
}
</script>
