<template>
  <el-container style="height: 100vh">
    <!-- 顶部导航栏 -->
    <el-header style="display: flex; align-items: center; justify-content: space-between; border-bottom: 1px solid #eee; background: #fff">
      <h2 style="margin: 0; color: #409EFF">🎵 音乐平台</h2>
      <div style="display: flex; align-items: center; gap: 15px">
        <span>欢迎，{{ username }}</span>
        <el-button type="danger" size="small" @click="handleLogout">退出登录</el-button>
      </div>
    </el-header>

    <el-container>
      <!-- 左侧菜单栏 -->
      <el-aside width="200px" style="background: #fff; border-right: 1px solid #eee">
        <el-menu :default-active="activeMenu" router>
          <el-menu-item index="/home">
            <span>🏠 首页</span>
          </el-menu-item>
          <el-menu-item index="/discover">
            <span>🔍 音乐发现</span>
          </el-menu-item>
          <el-menu-item index="/collection">
            <span>❤️ 我的收藏</span>
          </el-menu-item>
          <el-menu-item index="/community">
            <span>💬 社区动态</span>
          </el-menu-item>
          <el-menu-item index="/follow">
            <span>👥 我的关注</span>
          </el-menu-item>
          <el-menu-item index="/profile">
            <span>👤 个人资料</span>
          </el-menu-item>
          <el-menu-item index="/about">
            <span>📖 关于</span>
          </el-menu-item>
        </el-menu>
      </el-aside>

      <!-- 右侧内容区域（底部留出播放栏的高度） -->
      <el-main style="background: #f5f5f5; padding-bottom: 100px">
        <router-view />
      </el-main>
    </el-container>

    <!-- 全局播放栏（固定在底部，所有页面共享） -->
    <PlayerBar />
  </el-container>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import PlayerBar from '../components/PlayerBar.vue'  // 导入全局播放栏组件

const route = useRoute()
const router = useRouter()
const username = localStorage.getItem('username') || '用户'

const activeMenu = computed(() => route.path)

const handleLogout = () => {
  localStorage.removeItem('token')
  localStorage.removeItem('username')
  localStorage.removeItem('role')
  router.push('/login')
}
</script>
