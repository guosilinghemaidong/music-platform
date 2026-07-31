<template>
  <el-container style="height: 100vh">
    <!-- 顶部导航栏 -->
    <el-header class="app-header">
      <!-- 左侧 Logo -->
      <h2 class="app-logo">🎵 音乐平台</h2>

      <!-- 右侧：用户头像下拉菜单 -->
      <el-dropdown trigger="click" @command="handleCommand">
        <div class="avatar-trigger">
          <el-avatar :size="32" :src="avatarUrl">
            <el-icon :size="16"><User /></el-icon>
          </el-avatar>
          <span class="avatar-name">{{ username }}</span>
        </div>
        <template #dropdown>
          <el-dropdown-menu>
            <el-dropdown-item command="/profile">
              <el-icon><User /></el-icon> 个人资料
            </el-dropdown-item>
            <el-dropdown-item command="/recent">
              <el-icon><Clock /></el-icon> 最近播放
            </el-dropdown-item>
            <el-dropdown-item command="/playlist">
              <el-icon><FolderOpened /></el-icon> 我的歌单
            </el-dropdown-item>
            <el-dropdown-item command="/about">
              <el-icon><InfoFilled /></el-icon> 关于
            </el-dropdown-item>
            <el-dropdown-item divided command="logout">
              <el-icon><SwitchButton /></el-icon> 退出登录
            </el-dropdown-item>
          </el-dropdown-menu>
        </template>
      </el-dropdown>
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
          <el-menu-item index="/ranking">
            <span>🏆 排行榜</span>
          </el-menu-item>
          <el-menu-item index="/search">
            <span>🔍 搜索</span>
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
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { User, Clock, FolderOpened, InfoFilled, SwitchButton } from '@element-plus/icons-vue'
import api from '../api/index.js'
import PlayerBar from '../components/PlayerBar.vue'  // 导入全局播放栏组件

const route = useRoute()
const router = useRouter()
const username = localStorage.getItem('username') || '用户'
const avatarUrl = ref('')

const activeMenu = computed(() => route.path)

// 获取用户头像
const fetchAvatar = async () => {
  try {
    const token = localStorage.getItem('token')
    const res = await api.get('/user/me', {
      headers: { Authorization: 'Bearer ' + token }
    })
    if (res.data.avatar) {
      avatarUrl.value = res.data.avatar
    }
  } catch (e) {
    // 获取失败不影响页面显示
  }
}

// 下拉菜单点击处理
const handleCommand = (command) => {
  if (command === 'logout') {
    localStorage.removeItem('token')
    localStorage.removeItem('username')
    localStorage.removeItem('role')
    router.push('/login')
  } else {
    router.push(command)
  }
}

onMounted(() => {
  fetchAvatar()
})
</script>

<style scoped>
/* 顶部导航栏 */
.app-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  border-bottom: 1px solid #eee;
  background: #fff;
}

.app-logo {
  margin: 0;
  color: #409EFF;
  font-size: 20px;
}

/* 头像触发器 */
.avatar-trigger {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  padding: 4px 8px;
  border-radius: 20px;
  transition: background 0.2s;
}

.avatar-trigger:hover {
  background: #f5f5f5;
}

.avatar-name {
  font-size: 14px;
  color: #333;
  max-width: 80px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
</style>
