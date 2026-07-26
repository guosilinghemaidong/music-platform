<template>
  <div class="community-page">
    <h2>动态社区</h2>

    <!-- ==================== 发布动态区域 ==================== -->
    <el-card class="post-create-card" shadow="never">
      <!-- 文字输入 -->
      <el-input
        v-model="postForm.content"
        type="textarea"
        :rows="3"
        placeholder="分享你的动态..."
        maxlength="500"
        show-word-limit
      />

      <!-- 图片上传区域 -->
      <div class="post-tools">
        <el-upload
          action=""
          :http-request="uploadImage"
          :before-upload="beforeImageUpload"
          :show-file-list="false"
          :limit="9"
        >
          <el-button type="primary" link>
            <el-icon style="margin-right: 4px"><Picture /></el-icon>图片
          </el-button>
        </el-upload>

        <!-- 音乐选择 -->
        <el-popover trigger="click" width="300">
          <template #reference>
            <el-button type="primary" link>
              <el-icon style="margin-right: 4px"><Headset /></el-icon>音乐
            </el-button>
          </template>
          <div>
            <el-select v-model="postForm.music_id" placeholder="选择一首音乐（可选）" clearable style="width: 100%">
              <el-option
                v-for="m in musicList"
                :key="m.id"
                :label="m.title"
                :value="m.id"
              />
            </el-select>
          </div>
        </el-popover>
      </div>

      <!-- 已选图片预览 -->
      <div v-if="uploadedImages.length > 0" class="image-preview-list">
        <div v-for="(img, index) in uploadedImages" :key="index" class="preview-item">
          <img :src="'http://localhost:8000' + img" />
          <el-icon class="remove-btn" @click="removeImage(index)"><Close /></el-icon>
        </div>
      </div>

      <!-- 已选音乐显示 -->
      <div v-if="postForm.music_id" class="selected-music">
        <el-icon><Headset /></el-icon>
        <span>已选择：{{ getMusicName(postForm.music_id) }}</span>
        <el-button type="danger" link size="small" @click="postForm.music_id = null">取消</el-button>
      </div>

      <!-- 发布按钮 -->
      <div style="margin-top: 12px; text-align: right">
        <el-button type="primary" @click="handlePublish" :loading="publishing">发布动态</el-button>
      </div>
    </el-card>

    <!-- ==================== 动态列表 ==================== -->
    <div class="post-list">
      <div v-for="post in postList" :key="post.id" class="post-card">
        <!-- 头部：作者信息 -->
        <div class="post-header">
          <el-avatar :size="40" :src="post.avatar ? 'http://localhost:8000' + post.avatar : ''">
            {{ post.username?.charAt(0) || '?' }}
          </el-avatar>
          <div class="post-author-info">
            <span class="author-name">{{ post.username }}</span>
            <span class="post-time">{{ formatTime(post.create_time) }}</span>
          </div>
          <!-- 关注按钮（不显示在自己的动态上） -->
          <el-button
            v-if="!isMyPost(post)"
            :type="followingSet.has(post.user_id) ? 'default' : 'primary'"
            size="small"
            style="margin-left: auto"
            :loading="followingToggleId === post.user_id"
            @click.stop="handleFollow(post.user_id)"
          >
            {{ followingSet.has(post.user_id) ? '已关注' : '+ 关注' }}
          </el-button>
        </div>

        <!-- 文字内容 -->
        <div class="post-content">{{ post.content }}</div>

        <!-- 图片展示 -->
        <div v-if="parseImages(post.images).length > 0" class="post-images">
          <img
            v-for="(img, idx) in parseImages(post.images)"
            :key="idx"
            :src="'http://localhost:8000' + img"
            class="post-image"
          />
        </div>

        <!-- 关联音乐卡片（点击播放） -->
        <div v-if="post.music_id && musicMap[post.music_id]" class="post-music-card" @click="playMusic(post.music_id)">
          <img
            v-if="musicMap[post.music_id].cover"
            :src="'http://localhost:8000' + musicMap[post.music_id].cover"
            class="music-cover"
          />
          <div class="music-info">
            <span class="music-title">{{ musicMap[post.music_id].title }}</span>
            <span class="music-hint">分享的音乐</span>
          </div>
        </div>

        <!-- 底部操作栏：点赞 + 评论 -->
        <div class="post-actions">
          <span
            class="action-btn"
            :class="{ liked: post.is_liked }"
            @click="handleLike(post)"
          >
            <el-icon><Star /></el-icon>
            {{ post.like_count || '' }} 点赞
          </span>
          <span class="action-btn" @click="toggleComments(post)">
            <el-icon><ChatDotRound /></el-icon>
            {{ post.comment_count || '' }} 评论
          </span>
          <!-- 删除自己的动态 -->
          <el-popconfirm
            v-if="isMyPost(post)"
            title="确定删除这条动态吗？"
            @confirm="handleDeletePost(post.id)"
          >
            <template #reference>
              <span class="action-btn delete-btn">
                <el-icon><Delete /></el-icon> 删除
              </span>
            </template>
          </el-popconfirm>
        </div>

        <!-- 评论区（展开/收起） -->
        <div v-if="expandedPosts.has(post.id)" class="comment-section">
          <!-- 发评论 -->
          <div class="comment-input">
            <el-input
              v-model="commentInputs[post.id]"
              placeholder="写评论..."
              size="small"
              @keyup.enter="handleComment(post)"
            />
            <el-button type="primary" size="small" @click="handleComment(post)" :loading="commentingId === post.id">发送</el-button>
          </div>
          <!-- 评论列表 -->
          <div v-if="commentsMap[post.id]" class="comment-list">
            <div v-for="c in commentsMap[post.id]" :key="c.id" class="comment-item">
              <el-avatar :size="28" :src="c.avatar ? 'http://localhost:8000' + c.avatar : ''">
                {{ c.username?.charAt(0) || '?' }}
              </el-avatar>
              <div class="comment-body">
                <span class="comment-author">{{ c.username }}</span>
                <span class="comment-text">{{ c.content }}</span>
                <span class="comment-time">{{ formatTime(c.create_time) }}</span>
              </div>
              <!-- 删除自己的评论 -->
              <el-popconfirm
                v-if="isMyComment(c)"
                title="确定删除？"
                @confirm="handleDeleteComment(post.id, c.id)"
              >
                <template #reference>
                  <el-button type="danger" link size="small" style="margin-left: auto">删除</el-button>
                </template>
              </el-popconfirm>
            </div>
          </div>
        </div>
      </div>

      <!-- 空状态 -->
      <el-empty v-if="postList.length === 0 && !loading" description="还没有动态，快来发布第一条吧" />

      <!-- 分页 -->
      <div v-if="total > pageSize" style="margin-top: 20px; display: flex; justify-content: center">
        <el-pagination
          v-model:current-page="page"
          :page-size="pageSize"
          :total="total"
          layout="total, prev, pager, next"
          @current-change="fetchPosts"
        />
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import api from '../api/index.js'
import { ElMessage } from 'element-plus'
import { Picture, Headset, Close, Star, ChatDotRound, Delete } from '@element-plus/icons-vue'
import { usePlayerStore } from '../stores/player'

// ========== 播放器 ==========
const playerStore = usePlayerStore()

// 点击社区里的音乐卡片 → 触发全局播放
const playMusic = (musicId) => {
  const music = musicMap.value[musicId]
  if (!music) return
  playerStore.playMusic(music)
}

// ========== 请求头 ==========
const getAuthHeaders = () => {
  const token = localStorage.getItem('token')
  return token ? { Authorization: 'Bearer ' + token } : {}
}

// ========== 当前用户 ==========
const currentUserId = ref(null)
const fetchCurrentUser = async () => {
  try {
    const res = await api.get('/user/me', { headers: getAuthHeaders() })
    currentUserId.value = res.data.id
  } catch (e) {
    console.error('获取用户信息失败', e)
  }
}

// ========== 关注功能 ==========
const followingSet = ref(new Set())          // 当前用户已关注的用户ID集合
const followingToggleId = ref(null)          // 正在切换关注状态的用户ID（防重复点击）

// 获取我的关注列表，构建 ID 集合
const fetchFollowingList = async () => {
  try {
    const res = await api.get('/follow/following')
    const ids = new Set()
    res.data.items.forEach(u => ids.add(u.id))
    followingSet.value = ids
  } catch (e) {
    console.error('获取关注列表失败', e)
  }
}

// 关注 / 取消关注
const handleFollow = async (userId) => {
  followingToggleId.value = userId
  try {
    const res = await api.post('/follow/toggle', { following_id: userId })
    if (res.data.is_followed) {
      followingSet.value.add(userId)
      ElMessage.success('已关注')
    } else {
      followingSet.value.delete(userId)
      ElMessage.success('已取消关注')
    }
  } catch (e) {
    ElMessage.error('操作失败')
  } finally {
    followingToggleId.value = null
  }
}

// ========== 发布动态 ==========
const postForm = ref({ content: '', music_id: null })
const uploadedImages = ref([])  // 已上传的图片路径数组
const publishing = ref(false)

// 上传图片
const beforeImageUpload = (file) => {
  if (uploadedImages.value.length >= 9) {
    ElMessage.error('最多上传 9 张图片')
    return false
  }
  const ext = file.name.split('.').pop().toLowerCase()
  if (!['jpg', 'jpeg', 'png', 'gif', 'webp'].includes(ext)) {
    ElMessage.error(`不支持的图片格式：.${ext}`)
    return false
  }
  return true
}

const uploadImage = async (options) => {
  const formData = new FormData()
  formData.append('file', options.file)
  try {
    const res = await api.post('/upload/image', formData, {
      headers: { ...getAuthHeaders(), 'Content-Type': 'multipart/form-data' }
    })
    uploadedImages.value.push(res.data.filename)
    ElMessage.success('图片上传成功')
  } catch (e) {
    ElMessage.error('图片上传失败')
  }
}

const removeImage = (index) => {
  uploadedImages.value.splice(index, 1)
}

// 发布动态
const handlePublish = async () => {
  if (!postForm.value.content.trim() && uploadedImages.value.length === 0 && !postForm.value.music_id) {
    ElMessage.warning('请输入内容、上传图片或选择音乐')
    return
  }
  publishing.value = true
  try {
    const data = {
      content: postForm.value.content || '分享了一首音乐',
      images: uploadedImages.value.length > 0 ? JSON.stringify(uploadedImages.value) : null,
      music_id: postForm.value.music_id || null
    }
    await api.post('/post/add', data, { headers: getAuthHeaders() })
    ElMessage.success('发布成功，等待审核')
    // 重置表单
    postForm.value = { content: '', music_id: null }
    uploadedImages.value = []
    fetchPosts()  // 刷新列表（虽然新动态要审核后才可见）
  } catch (e) {
    ElMessage.error(e.response?.data?.detail || '发布失败')
  } finally {
    publishing.value = false
  }
}

// ========== 动态列表 ==========
const postList = ref([])
const page = ref(1)
const pageSize = ref(10)
const total = ref(0)
const loading = ref(false)

const fetchPosts = async () => {
  loading.value = true
  try {
    const res = await api.get('/post/list', {
      params: { page: page.value, page_size: pageSize.value },
      headers: getAuthHeaders()
    })
    postList.value = res.data.items
    total.value = res.data.total
  } catch (e) {
    ElMessage.error('获取动态列表失败')
  } finally {
    loading.value = false
  }
}

// ========== 音乐列表（用于选择 + 显示关联音乐信息） ==========
const musicList = ref([])
const musicMap = ref({})

const fetchMusicList = async () => {
  try {
    const res = await api.get('/music/list', { params: { page: 1, page_size: 200 } })
    musicList.value = res.data.items || []
    const map = {}
    musicList.value.forEach(m => { map[m.id] = m })
    musicMap.value = map
  } catch (e) {
    console.error('获取音乐列表失败', e)
  }
}

const getMusicName = (id) => {
  return musicMap.value[id]?.title || `音乐ID:${id}`
}

// ========== 解析图片 JSON ==========
const parseImages = (imagesStr) => {
  if (!imagesStr) return []
  try {
    const arr = JSON.parse(imagesStr)
    return Array.isArray(arr) ? arr : []
  } catch {
    return []
  }
}

// ========== 点赞 ==========
const handleLike = async (post) => {
  try {
    const res = await api.post('/post/like/toggle', { post_id: post.id }, {
      headers: getAuthHeaders()
    })
    post.is_liked = res.data.is_liked
    post.like_count = res.data.like_count
  } catch (e) {
    ElMessage.error('操作失败')
  }
}

// ========== 评论 ==========
const expandedPosts = reactive(new Set())   // 当前展开评论区的动态ID
const commentsMap = ref({})                 // { postId: [comments] }
const commentInputs = ref({})              // { postId: '输入内容' }
const commentingId = ref(null)             // 正在发评论的动态ID

// 展开/收起评论区
const toggleComments = async (post) => {
  if (expandedPosts.has(post.id)) {
    expandedPosts.delete(post.id)
  } else {
    expandedPosts.add(post.id)
    // 首次展开时加载评论
    if (!commentsMap.value[post.id]) {
      await fetchComments(post.id)
    }
  }
}

// 获取评论列表
const fetchComments = async (postId) => {
  try {
    const res = await api.get(`/post/comment/list/${postId}`)
    commentsMap.value[postId] = res.data
  } catch (e) {
    console.error('获取评论失败', e)
  }
}

// 发评论
const handleComment = async (post) => {
  const content = (commentInputs.value[post.id] || '').trim()
  if (!content) {
    ElMessage.warning('请输入评论内容')
    return
  }
  commentingId.value = post.id
  try {
    await api.post('/post/comment/add', {
      post_id: post.id,
      content: content
    }, { headers: getAuthHeaders() })
    commentInputs.value[post.id] = ''
    post.comment_count += 1
    // 重新加载评论列表
    await fetchComments(post.id)
  } catch (e) {
    ElMessage.error(e.response?.data?.detail || '评论失败')
  } finally {
    commentingId.value = null
  }
}

// ========== 删除 ==========
const handleDeletePost = async (postId) => {
  try {
    await api.delete(`/post/delete/${postId}`, { headers: getAuthHeaders() })
    ElMessage.success('删除成功')
    fetchPosts()
  } catch (e) {
    ElMessage.error(e.response?.data?.detail || '删除失败')
  }
}

const handleDeleteComment = async (postId, commentId) => {
  try {
    await api.delete(`/post/comment/delete/${commentId}`, { headers: getAuthHeaders() })
    ElMessage.success('评论已删除')
    // 更新计数
    const post = postList.value.find(p => p.id === postId)
    if (post) post.comment_count = Math.max(0, post.comment_count - 1)
    // 重新加载评论
    await fetchComments(postId)
  } catch (e) {
    ElMessage.error(e.response?.data?.detail || '删除失败')
  }
}

// ========== 工具函数 ==========
const isMyPost = (post) => currentUserId.value && post.user_id === currentUserId.value
const isMyComment = (comment) => currentUserId.value && comment.user_id === currentUserId.value

const formatTime = (timeStr) => {
  if (!timeStr) return ''
  const d = new Date(timeStr)
  const now = new Date()
  const diff = now - d
  if (diff < 60000) return '刚刚'
  if (diff < 3600000) return `${Math.floor(diff / 60000)}分钟前`
  if (diff < 86400000) return `${Math.floor(diff / 3600000)}小时前`
  return `${d.getMonth() + 1}月${d.getDate()}日`
}

// ========== 生命周期 ==========
onMounted(() => {
  fetchCurrentUser()
  fetchFollowingList()   // 加载关注列表，用于显示关注按钮状态
  fetchMusicList()
  fetchPosts()
})
</script>

<style scoped>
.community-page {
  max-width: 700px;
  margin: 0 auto;
}

/* 发布区域 */
.post-create-card {
  margin-bottom: 20px;
  border-radius: 8px;
}
.post-tools {
  display: flex;
  gap: 16px;
  margin-top: 10px;
}
.image-preview-list {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-top: 10px;
}
.preview-item {
  position: relative;
  width: 80px;
  height: 80px;
}
.preview-item img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  border-radius: 4px;
}
.remove-btn {
  position: absolute;
  top: -6px;
  right: -6px;
  background: #f56c6c;
  color: #fff;
  border-radius: 50%;
  width: 18px;
  height: 18px;
  font-size: 12px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
}
.selected-music {
  display: flex;
  align-items: center;
  gap: 6px;
  margin-top: 8px;
  padding: 6px 10px;
  background: #f0f9eb;
  border-radius: 4px;
  font-size: 13px;
  color: #67c23a;
}

/* 动态卡片 */
.post-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}
.post-card {
  background: #fff;
  border-radius: 8px;
  padding: 16px;
  border: 1px solid #eee;
}
.post-header {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 12px;
}
.post-author-info {
  display: flex;
  flex-direction: column;
}
.author-name {
  font-weight: 600;
  font-size: 14px;
}
.post-time {
  font-size: 12px;
  color: #999;
}
.post-content {
  font-size: 14px;
  line-height: 1.6;
  margin-bottom: 10px;
  white-space: pre-wrap;
}

/* 图片展示 */
.post-images {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  margin-bottom: 10px;
}
.post-image {
  width: 120px;
  height: 120px;
  object-fit: cover;
  border-radius: 6px;
  cursor: pointer;
}

/* 音乐卡片 */
.post-music-card {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px;
  background: #f5f7fa;
  border-radius: 8px;
  margin-bottom: 10px;
  cursor: pointer;
  transition: background 0.2s;
}
.post-music-card:hover {
  background: #e8eaed;
}
.music-cover {
  width: 48px;
  height: 48px;
  border-radius: 4px;
  object-fit: cover;
}
.music-info {
  display: flex;
  flex-direction: column;
}
.music-title {
  font-size: 14px;
  font-weight: 500;
}
.music-hint {
  font-size: 12px;
  color: #999;
}

/* 操作栏 */
.post-actions {
  display: flex;
  gap: 20px;
  padding-top: 8px;
  border-top: 1px solid #f0f0f0;
}
.action-btn {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 13px;
  color: #666;
  cursor: pointer;
  padding: 4px 0;
}
.action-btn:hover {
  color: #409eff;
}
.action-btn.liked {
  color: #f56c6c;
}
.delete-btn:hover {
  color: #f56c6c;
}

/* 评论区 */
.comment-section {
  margin-top: 12px;
  padding-top: 12px;
  border-top: 1px solid #f0f0f0;
}
.comment-input {
  display: flex;
  gap: 8px;
  margin-bottom: 12px;
}
.comment-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}
.comment-item {
  display: flex;
  align-items: flex-start;
  gap: 8px;
}
.comment-body {
  display: flex;
  flex-direction: column;
  flex: 1;
}
.comment-author {
  font-size: 13px;
  font-weight: 600;
}
.comment-text {
  font-size: 13px;
  margin-top: 2px;
}
.comment-time {
  font-size: 11px;
  color: #999;
  margin-top: 2px;
}
</style>
