<template>
  <div>
    <h2>我的收藏</h2>

    <!-- 收藏列表 -->
    <el-table
      :data="collectionList"
      v-loading="loading"
      style="margin-top: 20px; width: 100%"
    >
      <!-- 序号 -->
      <el-table-column label="#" width="60">
        <template #default="scope">
          <span style="color: #999">{{ (currentPage - 1) * pageSize + scope.$index + 1 }}</span>
        </template>
      </el-table-column>

      <!-- 封面（小图，点击播放） -->
      <el-table-column label="封面" width="80">
        <template #default="scope">
          <!-- 已下架的歌曲：封面变灰，点击提示下架 -->
          <div v-if="scope.row.status === 0" class="mini-cover mini-cover-disabled">
            <img v-if="scope.row.cover" :src="getFullUrl(scope.row.cover)" alt="封面" />
            <el-icon v-else :size="20"><Headset /></el-icon>
            <!-- 灰色遮罩 + 下架图标 -->
            <div class="mini-disabled-overlay">
              <el-icon :size="16"><Close /></el-icon>
            </div>
          </div>
          <!-- 正常的歌曲：可以点击播放 -->
          <div v-else class="mini-cover" @click="playFromCollection(scope.row)">
            <img v-if="scope.row.cover" :src="getFullUrl(scope.row.cover)" alt="封面" />
            <el-icon v-else :size="20"><Headset /></el-icon>
            <!-- 悬停显示播放按钮 -->
            <div class="mini-play-overlay">
              <el-icon :size="18"><VideoPlay /></el-icon>
            </div>
          </div>
        </template>
      </el-table-column>

      <!-- 歌名 -->
      <el-table-column prop="title" label="歌曲" />

      <!-- 状态（已下架的歌曲显示标签） -->
      <el-table-column label="状态" width="90">
        <template #default="scope">
          <el-tag v-if="scope.row.status === 0" type="info" size="small">已下架</el-tag>
          <el-tag v-else type="success" size="small">正常</el-tag>
        </template>
      </el-table-column>

      <!-- 歌手 -->
      <el-table-column label="歌手" width="160">
        <template #default="scope">
          <router-link :to="'/singer/' + scope.row.singer_id" class="singer-link">{{ getSingerName(scope.row.singer_id) }}</router-link>
        </template>
      </el-table-column>

      <!-- 播放次数 -->
      <el-table-column label="播放" width="80">
        <template #default="scope">
          {{ scope.row.play_count }}
        </template>
      </el-table-column>

      <!-- 收藏时间 -->
      <el-table-column label="收藏时间" width="180">
        <template #default="scope">
          {{ formatTime(scope.row.collected_at) }}
        </template>
      </el-table-column>

      <!-- 操作 -->
      <el-table-column label="操作" width="100">
        <template #default="scope">
          <el-button type="danger" size="small" text @click="handleUnCollect(scope.row.id)">
            取消收藏
          </el-button>
        </template>
      </el-table-column>
    </el-table>

    <!-- 没有收藏时的提示 -->
    <el-empty v-if="!loading && collectionList.length === 0" description="还没有收藏任何歌曲" />

    <!-- 分页 -->
    <div v-if="total > 0" style="margin-top: 20px; display: flex; justify-content: center">
      <el-pagination
        v-model:current-page="currentPage"
        v-model:page-size="pageSize"
        :total="total"
        :page-sizes="[10, 20, 50]"
        layout="total, sizes, prev, pager, next"
        @current-change="fetchCollectionList"
        @size-change="handleSizeChange"
      />
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { Headset, VideoPlay, Close } from '@element-plus/icons-vue'
import api from '../api/index.js'
import { ElMessage, ElMessageBox } from 'element-plus'
import { usePlayerStore } from '../stores/player'  // 导入全局播放器状态

// 获取全局播放器状态
const playerStore = usePlayerStore()

// ========== 数据 ==========

// 收藏列表
const collectionList = ref([])
// 总数
const total = ref(0)
// 当前页码
const currentPage = ref(1)
// 每页数量
const pageSize = ref(10)
// 加载状态
const loading = ref(false)
// 歌手映射表
const singerMap = ref({})

// ========== 方法 ==========

// 获取收藏列表（调用 GET /collection/list，需要带 Token）
const fetchCollectionList = async () => {
  loading.value = true
  try {
    const token = localStorage.getItem('token')
    const res = await api.get('/collection/list', {
      params: {
        page: currentPage.value,
        page_size: pageSize.value
      },
      headers: { Authorization: 'Bearer ' + token }
    })
    collectionList.value = res.data.items
    total.value = res.data.total
  } catch (error) {
    ElMessage.error('获取收藏列表失败')
  } finally {
    loading.value = false
  }
}

// 获取歌手列表，构建映射
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
  return singerMap.value[singerId] || '未知歌手'
}

// 点击封面 → 用全局播放器播放这首收藏的歌
const playFromCollection = (music) => {
  // 已下架的歌曲不能播放
  if (music.status === 0) {
    ElMessage.warning('该歌曲已下架，无法播放')
    return
  }
  // 把当前收藏列表作为播放列表传给 store
  playerStore.playMusic(music, collectionList.value)
}

// 拼接完整 URL
const getFullUrl = (path) => {
  if (!path) return ''
  if (path.startsWith('http')) return path
  return '' + path
}

// 格式化收藏时间（ISO 字符串 → 可读格式）
const formatTime = (timeStr) => {
  if (!timeStr) return ''
  const date = new Date(timeStr)
  const y = date.getFullYear()
  const m = String(date.getMonth() + 1).padStart(2, '0')
  const d = String(date.getDate()).padStart(2, '0')
  const h = String(date.getHours()).padStart(2, '0')
  const min = String(date.getMinutes()).padStart(2, '0')
  return `${y}-${m}-${d} ${h}:${min}`
}

// 取消收藏（弹出确认框，确认后调用 toggle 接口）
const handleUnCollect = async (musicId) => {
  try {
    // 先弹确认框
    await ElMessageBox.confirm('确定要取消收藏吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })

    // 用户点了确定，调用取消收藏接口
    const token = localStorage.getItem('token')
    await api.post('/collection/toggle', { music_id: musicId }, {
      headers: { Authorization: 'Bearer ' + token }
    })
    ElMessage.success('已取消收藏')

    // 刷新列表
    fetchCollectionList()
  } catch (error) {
    // 用户点了取消，不做任何处理
    if (error !== 'cancel') {
      ElMessage.error('操作失败')
    }
  }
}

// 切换每页数量
const handleSizeChange = () => {
  currentPage.value = 1
  fetchCollectionList()
}

// ========== 生命周期 ==========

onMounted(() => {
  fetchCollectionList()
  fetchSingerMap()
})
</script>

<style scoped>
/* 小封面图（可点击） */
.mini-cover {
  position: relative;
  width: 45px;
  height: 45px;
  border-radius: 4px;
  background: #f0f0f0;
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
  color: #ccc;
  cursor: pointer;
}

.mini-cover img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

/* 封面上的悬停播放遮罩 */
.mini-play-overlay {
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
}

/* 鼠标悬停时显示遮罩 */
.mini-cover:hover .mini-play-overlay {
  opacity: 1;
}

/* 已下架歌曲的封面：变灰、不可点击 */
.mini-cover-disabled {
  cursor: not-allowed;
  filter: grayscale(80%);
}

/* 已下架封面上的灰色遮罩 */
.mini-disabled-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.4);
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
}
</style>
