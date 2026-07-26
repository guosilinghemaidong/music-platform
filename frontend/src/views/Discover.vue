<template>
  <div>
    <h2>音乐发现</h2>

    <!-- 搜索栏 + 分类筛选 -->
    <div style="margin-top: 20px; display: flex; gap: 12px; align-items: center">
      <!-- 搜索输入框 -->
      <el-input
        v-model="searchKeyword"
        placeholder="搜索歌曲名称..."
        clearable
        style="width: 260px"
        @keyup.enter="handleSearch"
        @clear="handleSearch"
      >
        <template #prefix>
          <el-icon><Search /></el-icon>
        </template>
      </el-input>

      <!-- 分类筛选下拉 -->
      <el-select
        v-model="selectedCategoryId"
        placeholder="全部分类"
        clearable
        style="width: 150px"
        @change="handleCategoryChange"
      >
        <el-option
          v-for="cat in categoryList"
          :key="cat.id"
          :label="cat.name"
          :value="cat.id"
        />
      </el-select>
    </div>

    <!-- 音乐列表区域 -->
    <div v-loading="loading" style="margin-top: 20px">
      <!-- 没有音乐时的提示 -->
      <el-empty v-if="!loading && musicList.length === 0" description="暂无音乐" />

      <!-- 音乐卡片网格 -->
      <el-row :gutter="16">
        <el-col
          v-for="music in musicList"
          :key="music.id"
          :xs="24" :sm="12" :md="8" :lg="6"
          style="margin-bottom: 16px"
        >
          <el-card :body-style="{ padding: '0px' }" shadow="hover">
            <!-- 封面图片区域（悬停显示播放按钮） -->
            <div class="music-cover" @click="playFromDiscover(music)">
              <!-- 有封面就显示封面，没有就显示默认图标 -->
              <img v-if="music.cover" :src="getCoverUrl(music.cover)" alt="封面" />
              <div v-else class="no-cover">
                <el-icon :size="48"><Headset /></el-icon>
              </div>
              <!-- 悬停时显示的播放遮罩层 -->
              <div class="play-overlay">
                <el-icon :size="36"><VideoPlay /></el-icon>
              </div>
              <!-- 正在播放的歌曲显示播放中指示 -->
              <div v-if="playerStore.isCurrentMusic(music.id)" class="playing-indicator">
                <el-icon :size="20"><VideoPause /></el-icon>
                <span>播放中</span>
              </div>
            </div>

            <!-- 歌曲信息 -->
            <div style="padding: 12px">
              <div class="music-title">{{ music.title }}</div>
              <div class="music-info">
                <span>{{ getSingerName(music.singer_id) }}</span>
                <span class="play-count">
                  <el-icon><Headset /></el-icon>
                  {{ music.play_count }}
                </span>
              </div>
            </div>
          </el-card>
        </el-col>
      </el-row>
    </div>

    <!-- 分页组件 -->
    <div v-if="total > 0" style="margin-top: 20px; display: flex; justify-content: center">
      <el-pagination
        v-model:current-page="currentPage"
        v-model:page-size="pageSize"
        :total="total"
        :page-sizes="[12, 24, 48]"
        layout="total, sizes, prev, pager, next"
        @current-change="fetchMusicList"
        @size-change="handleSizeChange"
      />
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { Headset, Search, VideoPlay, VideoPause } from '@element-plus/icons-vue'
import api from '../api/index.js'
import { ElMessage } from 'element-plus'
import { usePlayerStore } from '../stores/player'  // 导入全局播放器状态

// 获取全局播放器状态
const playerStore = usePlayerStore()

// ========== 数据 ==========

// 音乐列表
const musicList = ref([])
// 总数（用于分页）
const total = ref(0)
// 当前页码
const currentPage = ref(1)
// 每页数量
const pageSize = ref(12)
// 加载状态
const loading = ref(false)

// 歌手映射表：singerId -> 歌手名字
const singerMap = ref({})
// 分类映射表：categoryId -> 分类名字
const categoryMap = ref({})
// 分类列表（用于下拉框渲染）
const categoryList = ref([])
// 搜索关键词
const searchKeyword = ref('')
// 当前选中的分类 ID
const selectedCategoryId = ref(null)

// ========== 方法 ==========

// 获取音乐列表（调用 GET /music/list）
const fetchMusicList = async () => {
  loading.value = true
  try {
    // 构造请求参数，包含分页 + 搜索 + 筛选
    const params = {
      page: currentPage.value,
      page_size: pageSize.value
    }
    // 有搜索关键词就带上
    if (searchKeyword.value) {
      params.keyword = searchKeyword.value
    }
    // 选了分类就带上分类 ID
    if (selectedCategoryId.value) {
      params.category_id = selectedCategoryId.value
    }

    const res = await api.get('/music/list', { params })
    musicList.value = res.data.items
    total.value = res.data.total
  } catch (error) {
    ElMessage.error('获取音乐列表失败')
  } finally {
    loading.value = false
  }
}

// 获取歌手列表，构建 ID->名字 的映射
const fetchSingerMap = async () => {
  try {
    // 一次取足够多的歌手（歌手数量一般不会太多）
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

// 获取分类列表，构建 ID->名字 的映射 + 下拉框数据
const fetchCategoryMap = async () => {
  try {
    const res = await api.get('/category/list', {
      params: { page: 1, page_size: 100 }
    })
    const map = {}
    res.data.items.forEach(cat => {
      map[cat.id] = cat.name
    })
    categoryMap.value = map
    // 同时保存原始列表，给下拉框渲染用
    categoryList.value = res.data.items
  } catch (error) {
    console.error('获取分类列表失败', error)
  }
}

// 根据歌手 ID 获取歌手名字
const getSingerName = (singerId) => {
  return singerMap.value[singerId] || '未知歌手'
}

// 点击封面 → 用全局播放器播放这首歌
const playFromDiscover = (music) => {
  // 把当前页面的音乐列表作为播放列表传给 store
  playerStore.playMusic(music, musicList.value)
}

// 拼接封面的完整 URL（后端返回的是 /static/images/xxx 相对路径）
const getCoverUrl = (cover) => {
  if (!cover) return ''
  if (cover.startsWith('http')) return cover
  return 'http://localhost:8000' + cover
}

// 切换每页数量时，重置到第一页并重新请求
const handleSizeChange = () => {
  currentPage.value = 1
  fetchMusicList()
}

// 点搜索 / 按回车 / 清空搜索框时，重置页码并重新请求
const handleSearch = () => {
  currentPage.value = 1
  fetchMusicList()
}

// 切换分类筛选时，重置页码并重新请求
const handleCategoryChange = () => {
  currentPage.value = 1
  fetchMusicList()
}

// ========== 生命周期 ==========

onMounted(() => {
  // 页面加载时，同时请求音乐列表、歌手映射、分类映射
  fetchMusicList()
  fetchSingerMap()
  fetchCategoryMap()
})
</script>

<style scoped>
/* 封面图片区域样式 */
.music-cover {
  position: relative;
  width: 100%;
  height: 180px;
  background: #f5f5f5;
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
  cursor: pointer;
}

/* 封面图片自适应填满 */
.music-cover img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

/* 没有封面时的占位区域 */
.no-cover {
  color: #ccc;
  display: flex;
  align-items: center;
  justify-content: center;
  width: 100%;
  height: 100%;
  background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
}

/* 悬停时显示的播放按钮遮罩层 */
.play-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.35);
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
  opacity: 0;
  transition: opacity 0.3s;
  cursor: pointer;
}

/* 鼠标悬停时显示遮罩层 */
.music-cover:hover .play-overlay {
  opacity: 1;
}

/* 正在播放的指示标签（左下角） */
.playing-indicator {
  position: absolute;
  bottom: 8px;
  left: 8px;
  background: #409EFF;
  color: #fff;
  padding: 2px 8px;
  border-radius: 10px;
  font-size: 12px;
  display: flex;
  align-items: center;
  gap: 4px;
}

/* 歌曲标题 */
.music-title {
  font-size: 15px;
  font-weight: bold;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  margin-bottom: 6px;
}

/* 歌曲信息行（歌手 + 播放量） */
.music-info {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 13px;
  color: #999;
}

/* 播放次数样式 */
.play-count {
  display: flex;
  align-items: center;
  gap: 4px;
}
</style>
