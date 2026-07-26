<template>
  <el-container style="height: 100vh">
    <!-- 顶部导航栏 -->
    <el-header style="display: flex; align-items: center; justify-content: space-between; border-bottom: 1px solid #eee; background: #fff">
      <h2 style="margin: 0; color: #E6A23C">⚙️ 管理后台</h2>
      <div style="display: flex; align-items: center; gap: 15px">
        <span>管理员：{{ username }}</span>
        <el-button type="danger" size="small" @click="handleLogout">退出登录</el-button>
      </div>
    </el-header>

    <el-container>
      <!-- 左侧菜单栏 -->
      <el-aside width="200px" style="background: #fff; border-right: 1px solid #eee">
        <el-menu :default-active="activeMenu" router>
          <el-menu-item index="/admin">
            <span>👥 用户管理</span>
          </el-menu-item>
          <el-menu-item index="/admin/singer">
            <span>🎤 歌手管理</span>
          </el-menu-item>
          <el-menu-item index="/admin/album">
            <span>💿 专辑管理</span>
          </el-menu-item>
          <el-menu-item index="/admin/category">
            <span>📂 分类管理</span>
          </el-menu-item>
          <el-menu-item index="/admin/add-music">
            <span>📀 上架音乐</span>
          </el-menu-item>
          <el-menu-item index="/admin/music">
            <span>🎵 音乐审核</span>
          </el-menu-item>
          <el-menu-item index="/admin/post">
            <span>💬 动态管理</span>
          </el-menu-item>
        </el-menu>
      </el-aside>

      <!-- 右侧内容区域 -->
      <el-main style="background: #f5f5f5">
        <router-view />
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'

const route = useRoute()
const router = useRouter()
const username = localStorage.getItem('username') || '管理员'

const activeMenu = computed(() => route.path)

const handleLogout = () => {
  localStorage.removeItem('token')
  localStorage.removeItem('username')
  localStorage.removeItem('role')
  router.push('/login')
}
</script>
