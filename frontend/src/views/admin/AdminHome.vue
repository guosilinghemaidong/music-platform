<template>
  <div>
    <h1>管理员后台</h1>
    <p>欢迎，管理员 {{ username }}！</p>
    <el-button @click="handleLogout">退出登录</el-button>
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router'

const router = useRouter()
const username = localStorage.getItem('username') || '管理员'

const handleLogout = () => {
  localStorage.removeItem('token')
  localStorage.removeItem('username')
  localStorage.removeItem('role')
  router.push('/login')
}
</script>
