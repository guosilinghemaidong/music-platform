<template>
  <div>
    <h2>欢迎回来，{{ username }}！</h2>
    <p>这是音乐平台的首页，更多功能正在开发中...</p>

    <el-card style="margin-top: 20px">
      <template #header>
        <span>🎵 快速导航</span>
      </template>
      <div style="display: flex; gap: 20px">
        <el-button type="primary" @click="$router.push('/discover')">音乐发现</el-button>
        <el-button type="success" @click="$router.push('/collection')">我的收藏</el-button>
        <el-button type="warning" @click="$router.push('/profile')">个人资料</el-button>
      </div>
    </el-card>
  </div>
</template>

<script setup>
const username = localStorage.getItem('username') || '用户'
</script>
