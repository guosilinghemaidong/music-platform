<template>
  <div class="follow-page">
    <h2>我的关注</h2>

    <!-- Tab 切换：我的关注 / 我的粉丝 -->
    <el-tabs v-model="activeTab" @tab-change="handleTabChange">
      <el-tab-pane :label="`我的关注 (${followingCount})`" name="following" />
      <el-tab-pane :label="`我的粉丝 (${followersCount})`" name="followers" />
    </el-tabs>

    <!-- 用户列表 -->
    <div v-loading="loading" class="user-list">
      <el-empty v-if="!loading && userList.length === 0" :description="activeTab === 'following' ? '还没有关注任何人' : '还没有粉丝'" />

      <div v-for="user in userList" :key="user.id" class="user-card">
        <!-- 头像 -->
        <el-avatar :size="48" :src="user.avatar ? '' + user.avatar : ''">
          {{ user.nickname?.charAt(0) || user.username?.charAt(0) || '?' }}
        </el-avatar>

        <!-- 用户信息 -->
        <div class="user-info">
          <span class="user-name">{{ user.nickname || user.username }}</span>
          <span class="user-sub">{{ user.username }}</span>
        </div>

        <!-- 关注/取关按钮 -->
        <el-button
          :type="getIsFollowing(user) ? 'default' : 'primary'"
          size="small"
          :loading="togglingId === user.id"
          @click="handleToggleFollow(user)"
        >
          {{ getIsFollowing(user) ? '已关注' : '关注' }}
        </el-button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import api from '../api/index.js'
import { ElMessage } from 'element-plus'

// ========== 状态 ==========
const activeTab = ref('following')      // 当前选中的 Tab
const userList = ref([])                // 当前列表的用户数据
const followingCount = ref(0)           // 关注总数
const followersCount = ref(0)           // 粉丝总数
const loading = ref(false)              // 加载状态
const togglingId = ref(null)            // 正在切换关注状态的用户ID（防重复点击）

// ========== 请求方法 ==========

// 判断当前用户是否正在关注该用户
// - "我的关注" Tab：列表里的人默认就是已关注的（_following 默认 true）
// - "我的粉丝" Tab：根据 is_followed_back（是否互关）判断
const getIsFollowing = (user) => {
  if (activeTab.value === 'following') {
    return user._following !== false
  }
  return user.is_followed_back
}

// 获取关注列表
const fetchFollowing = async () => {
  loading.value = true
  try {
    const res = await api.get('/follow/following')
    // 关注列表里的人都是已关注的，标记 _following = true
    userList.value = res.data.items.map(u => ({ ...u, _following: true }))
    followingCount.value = res.data.following_count
    followersCount.value = res.data.followers_count
  } catch {
    ElMessage.error('获取关注列表失败')
  } finally {
    loading.value = false
  }
}

// 获取粉丝列表
const fetchFollowers = async () => {
  loading.value = true
  try {
    const res = await api.get('/follow/followers')
    userList.value = res.data.items
    followingCount.value = res.data.following_count
    followersCount.value = res.data.followers_count
  } catch {
    ElMessage.error('获取粉丝列表失败')
  } finally {
    loading.value = false
  }
}

// 切换 Tab 时重新加载对应列表
const handleTabChange = (tab) => {
  if (tab === 'following') {
    fetchFollowing()
  } else {
    fetchFollowers()
  }
}

// 关注 / 取消关注
const handleToggleFollow = async (user) => {
  togglingId.value = user.id
  try {
    const res = await api.post('/follow/toggle', { following_id: user.id })
    // 更新本地的关注状态（用 _following 字段，和 getIsFollowing 对应）
    user._following = res.data.is_followed
    if (res.data.is_followed) {
      ElMessage.success('已关注')
      followingCount.value++
    } else {
      ElMessage.success('已取消关注')
      followingCount.value--
    }
  } catch {
    ElMessage.error('操作失败')
  } finally {
    togglingId.value = null
  }
}

// ========== 生命周期 ==========
onMounted(() => {
  fetchFollowing()
})
</script>

<style scoped>
.follow-page {
  max-width: 600px;
  margin: 0 auto;
}

.user-list {
  margin-top: 16px;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.user-card {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 16px;
  background: #fff;
  border-radius: 8px;
  border: 1px solid #eee;
}

.user-info {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.user-name {
  font-size: 15px;
  font-weight: 600;
}

.user-sub {
  font-size: 12px;
  color: #999;
  margin-top: 2px;
}
</style>
