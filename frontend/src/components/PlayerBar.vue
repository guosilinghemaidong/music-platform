<template>
  <!-- ========== 隐藏的 audio 元素：始终在 DOM 中，避免首次点击歌曲时 ref 还未创建导致无法播放 ========== -->
  <audio
    ref="audioRef"
    @timeupdate="onTimeUpdate"
    @loadedmetadata="onLoadedMetadata"
    @ended="onEnded"
  />

  <!-- 全局播放栏：只在有歌曲播放时显示 -->
  <div v-if="playerStore.currentMusic" class="player-bar">

    <!-- ========== 左侧：封面 + 歌曲信息 + 收藏 ========== -->
    <div class="player-left">
      <!-- 小封面图（点击弹出歌词弹窗） -->
      <div class="player-cover" @click="showLyricDialog = true">
        <img v-if="playerStore.currentMusic.cover" :src="getFullUrl(playerStore.currentMusic.cover)" alt="封面" />
        <el-icon v-else :size="28"><Headset /></el-icon>
      </div>
      <div class="player-info">
        <div class="player-title-row">
          <span class="player-title">{{ playerStore.currentMusic.title }}</span>
          <!-- 收藏按钮（星星）放在歌名旁边 -->
          <el-icon
            class="favorite-btn"
            :size="16"
            :class="{ 'is-favorite': isFavorited }"
            @click.stop="toggleFavorite"
          >
            <StarFilled v-if="isFavorited" />
            <Star v-else />
          </el-icon>
        </div>
        <div class="player-singer">{{ getSingerName(playerStore.currentMusic.singer_id) }}</div>
      </div>
    </div>

    <!-- ========== 中间：控制按钮 + 进度条 ========== -->
    <div class="player-center">
      <!-- 控制按钮组 -->
      <div class="player-controls">
        <!-- 上一首 -->
        <el-icon class="control-btn" :size="20" @click="playerStore.playPrev()"><CaretLeft /></el-icon>
        <!-- 播放 / 暂停 -->
        <el-icon class="control-btn main-btn" :size="28" @click="playerStore.togglePlay()">
          <VideoPause v-if="playerStore.isPlaying" />
          <VideoPlay v-else />
        </el-icon>
        <!-- 下一首 -->
        <el-icon class="control-btn" :size="20" @click="playerStore.playNext()"><CaretRight /></el-icon>
      </div>

      <!-- 进度条 -->
      <div class="progress-area">
        <span class="time-text">{{ formatTime(playerStore.currentTime) }}</span>
        <el-slider
          v-model="sliderValue"
          :max="maxSlider"
          :show-tooltip="false"
          @input="onSliderInput"
          @change="onSliderChange"
          style="flex: 1"
        />
        <span class="time-text">{{ formatTime(playerStore.duration) }}</span>
      </div>
    </div>

    <!-- ========== 右侧：音量 ========== -->
    <div class="player-right">
      <!-- 音量滑块 -->
      <el-slider
        v-model="playerStore.volume"
        :max="100"
        :show-tooltip="false"
        style="width: 100px"
        @input="onVolumeChange"
      />
    </div>

    <!-- ========== 歌词弹窗 ========== -->
    <el-dialog
      v-model="showLyricDialog"
      :title="playerStore.currentMusic?.title"
      width="500px"
      top="10vh"
    >
      <div class="lyric-dialog-body">
        <!-- 弹窗内的封面 + 歌曲信息 -->
        <div class="lyric-song-info">
          <div class="lyric-cover">
            <img v-if="playerStore.currentMusic?.cover" :src="getFullUrl(playerStore.currentMusic.cover)" alt="封面" />
            <el-icon v-else :size="60"><Headset /></el-icon>
          </div>
          <div>
            <div class="lyric-title">{{ playerStore.currentMusic?.title }}</div>
            <div class="lyric-singer">{{ getSingerName(playerStore.currentMusic?.singer_id) }}</div>
          </div>
        </div>

        <!-- 歌词内容 -->
        <div class="lyric-content" v-loading="lyricLoading">
          <p v-if="lyricText" class="lyric-text">{{ lyricText }}</p>
          <el-empty v-else-if="!lyricLoading" description="暂无歌词" :image-size="60" />
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, watch, onMounted, onUnmounted, computed } from 'vue'
import { Headset, VideoPlay, VideoPause, CaretLeft, CaretRight, Star, StarFilled } from '@element-plus/icons-vue'
import { usePlayerStore } from '../stores/player'
import api from '../api/index.js'
import { ElMessage } from 'element-plus'

// ========== 基础数据 ==========

// 获取播放器全局状态
const playerStore = usePlayerStore()

// audio DOM 引用（页面中隐藏的 <audio> 元素）
const audioRef = ref(null)

// 歌手映射表：singerId -> 歌手名字
const singerMap = ref({})

// 进度条的值（用于拖拽，和 store 里的 currentTime 分开，避免拖拽时抖动）
const sliderValue = ref(0)
// 进度条最大值（等于歌曲总时长）
const maxSlider = ref(0)
// 是否正在拖拽进度条
const isDragging = ref(false)

// ========== 收藏相关 ==========

// 当前歌曲是否已收藏
const isFavorited = ref(false)

// 获取当前歌曲的收藏状态
const checkFavoriteStatus = async () => {
  if (!playerStore.currentMusic) return
  try {
    const token = localStorage.getItem('token')
    const res = await api.get(`/collection/status/${playerStore.currentMusic.id}`, {
      headers: { Authorization: `Bearer ${token}` }
    })
    isFavorited.value = res.data.is_collected
  } catch {
    // 未登录或接口不存在时，默认未收藏
    isFavorited.value = false
  }
}

// 切换收藏状态（点击星星按钮）
const toggleFavorite = async () => {
  if (!playerStore.currentMusic) return
  try {
    const token = localStorage.getItem('token')
    const res = await api.post('/collection/toggle', {
      music_id: playerStore.currentMusic.id
    }, {
      headers: { Authorization: `Bearer ${token}` }
    })
    // 后端返回 { is_collected: true/false }
    isFavorited.value = res.data.is_collected
    ElMessage.success(res.data.is_collected ? '已收藏' : '已取消收藏')
  } catch {
    ElMessage.error('操作失败，请先登录')
  }
}

// ========== 歌词弹窗 ==========

// 弹窗是否显示
const showLyricDialog = ref(false)
// 歌词文本内容
const lyricText = ref('')
// 歌词加载状态
const lyricLoading = ref(false)

// 监听弹窗打开时，加载歌词
watch(showLyricDialog, async (visible) => {
  if (visible && playerStore.currentMusic) {
    await fetchLyric(playerStore.currentMusic.id)
  }
})

// 获取歌词
const fetchLyric = async (musicId) => {
  lyricLoading.value = true
  lyricText.value = ''
  try {
    const res = await api.get(`/music/lyric/${musicId}`)
    lyricText.value = res.data.lyric || ''
  } catch {
    lyricText.value = ''
  } finally {
    lyricLoading.value = false
  }
}

// ========== 方法 ==========

// 获取歌手列表，构建 ID->名字 的映射
const fetchSingerMap = async () => {
  try {
    const res = await api.get('/singer/list', {
      params: { page: 1, page_size: 200 }
    })
    const map = {}
    res.data.items.forEach(singer => {
      map[singer.id] = singer.name
    })
    singerMap.value = map
  } catch (error) {
    console.error('获取歌手列表失败', error)
  }
}

// 根据歌手 ID 获取名字
const getSingerName = (singerId) => {
  if (!singerId) return '未知歌手'
  return singerMap.value[singerId] || '未知歌手'
}

// 拼接完整 URL（后端返回的是 /static/xxx 相对路径）
const getFullUrl = (path) => {
  if (!path) return ''
  if (path.startsWith('http')) return path
  return '' + path
}

// ========== 音频控制（监听 store 状态变化） ==========

// 监听 currentMusic 变化 → 切换歌曲时重新加载音频
watch(() => playerStore.currentMusic, (newMusic) => {
  if (!newMusic || !audioRef.value) return
  // 设置新的音频源
  audioRef.value.src = getFullUrl(newMusic.file_url)
  audioRef.value.volume = playerStore.volume / 100
  // 自动开始播放
  audioRef.value.play().catch(() => {})
  // 播放次数 +1（通知后端给这首歌的播放计数加一）
  api.post(`/music/${newMusic.id}/play`).catch(() => {})
  // 检查收藏状态
  checkFavoriteStatus()
  // 重置歌词（下次打开弹窗时会重新加载）
  lyricText.value = ''
})

// 监听 isPlaying 变化 → 控制播放/暂停
watch(() => playerStore.isPlaying, (playing) => {
  if (!audioRef.value || !audioRef.value.src) return
  if (playing) {
    audioRef.value.play().catch(() => {})
  } else {
    audioRef.value.pause()
  }
})

// ========== audio 事件回调 ==========

// 播放进度更新（大约每 250ms 触发一次）
const onTimeUpdate = () => {
  playerStore.currentTime = audioRef.value.currentTime
  // 如果没在拖拽，同步更新进度条
  if (!isDragging.value) {
    sliderValue.value = audioRef.value.currentTime
  }
}

// 音频元数据加载完成（拿到总时长）
const onLoadedMetadata = () => {
  playerStore.duration = audioRef.value.duration
  maxSlider.value = audioRef.value.duration
}

// 歌曲播放结束 → 自动下一首
const onEnded = () => {
  playerStore.isPlaying = false
  playerStore.playNext()
}

// ========== 进度条操作 ==========

// 拖拽进度条时触发（实时更新显示值，但不跳转播放位置）
const onSliderInput = (val) => {
  isDragging.value = true
  playerStore.currentTime = val
}

// 进度条拖拽结束 / 点击定位 → 跳转播放位置
const onSliderChange = (val) => {
  audioRef.value.currentTime = val
  isDragging.value = false
}

// ========== 音量操作 ==========

// 音量变化 → 同步到 audio 元素
const onVolumeChange = (val) => {
  if (audioRef.value) {
    audioRef.value.volume = val / 100
  }
}

// ========== 工具方法 ==========

// 格式化时间（秒 → mm:ss）
const formatTime = (seconds) => {
  if (!seconds || isNaN(seconds)) return '00:00'
  const min = Math.floor(seconds / 60)
  const sec = Math.floor(seconds % 60)
  return `${min.toString().padStart(2, '0')}:${sec.toString().padStart(2, '0')}`
}

// ========== 生命周期 ==========

onMounted(() => {
  fetchSingerMap()
})

// 组件销毁时清理 audio
onUnmounted(() => {
  if (audioRef.value) {
    audioRef.value.pause()
    audioRef.value.src = ''
  }
})
</script>

<style scoped>
/* ===== 底部播放栏 ===== */
.player-bar {
  position: fixed;
  bottom: 0;
  left: 200px;   /* 跳过左侧菜单栏 */
  right: 0;
  height: 80px;
  background: #fff;
  border-top: 1px solid #e8e8e8;
  display: flex;
  align-items: center;
  padding: 0 24px;
  gap: 20px;
  z-index: 100;
  box-shadow: 0 -2px 8px rgba(0, 0, 0, 0.06);
}

/* 播放器左侧：封面 + 歌名 */
.player-left {
  display: flex;
  align-items: center;
  gap: 12px;
  min-width: 200px;
}

/* 小封面图（可点击） */
.player-cover {
  width: 50px;
  height: 50px;
  border-radius: 6px;
  background: #f0f0f0;
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
  color: #ccc;
  cursor: pointer;
  transition: opacity 0.2s;
}

.player-cover:hover {
  opacity: 0.8;
}

.player-cover img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

/* 歌曲信息文字 */
.player-info {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

/* 歌名行：歌名 + 收藏星星在同一行 */
.player-title-row {
  display: flex;
  align-items: center;
  gap: 6px;
}

.player-title {
  font-size: 14px;
  font-weight: bold;
  max-width: 120px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.player-singer {
  font-size: 12px;
  color: #999;
  margin-top: 4px;
}

/* 播放器中间：按钮 + 进度条 */
.player-center {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
}

/* 控制按钮组 */
.player-controls {
  display: flex;
  align-items: center;
  gap: 20px;
}

/* 控制按钮通用样式 */
.control-btn {
  cursor: pointer;
  color: #333;
  transition: color 0.2s;
}

.control-btn:hover {
  color: #409EFF;
}

/* 主按钮（播放/暂停）稍微大一点，蓝色圆形背景 */
.main-btn {
  background: #409EFF;
  color: #fff;
  border-radius: 50%;
  padding: 6px;
}

.main-btn:hover {
  background: #66b1ff;
  color: #fff;
}

/* 进度条区域 */
.progress-area {
  display: flex;
  align-items: center;
  gap: 8px;
  width: 100%;
  max-width: 500px;
}

/* 时间文字 */
.time-text {
  font-size: 12px;
  color: #999;
  min-width: 40px;
  text-align: center;
}

/* 播放器右侧：音量 */
.player-right {
  min-width: 100px;
  display: flex;
  align-items: center;
  justify-content: flex-end;
}

/* 收藏按钮样式 */
.favorite-btn {
  cursor: pointer;
  color: #999;
  transition: color 0.2s, transform 0.2s;
}

.favorite-btn:hover {
  transform: scale(1.2);
}

/* 已收藏状态：金色 */
.is-favorite {
  color: #f7ba2a;
}

/* ===== 歌词弹窗内容 ===== */
.lyric-dialog-body {
  padding: 0 10px;
}

/* 弹窗内歌曲信息 */
.lyric-song-info {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-bottom: 20px;
  padding-bottom: 16px;
  border-bottom: 1px solid #eee;
}

/* 弹窗内封面 */
.lyric-cover {
  width: 80px;
  height: 80px;
  border-radius: 8px;
  background: #f0f0f0;
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
  color: #ccc;
  flex-shrink: 0;
}

.lyric-cover img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.lyric-title {
  font-size: 18px;
  font-weight: bold;
}

.lyric-singer {
  font-size: 14px;
  color: #999;
  margin-top: 6px;
}

/* 歌词文本区域 */
.lyric-content {
  max-height: 400px;
  overflow-y: auto;
}

.lyric-text {
  white-space: pre-wrap;
  line-height: 2;
  font-size: 14px;
  color: #333;
  text-align: center;
}
</style>
