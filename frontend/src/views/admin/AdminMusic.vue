<template>
  <div>
    <h2>音乐审核</h2>

    <!-- 筛选栏 -->
    <div style="margin-bottom: 20px; display: flex; gap: 10px">
      <el-radio-group v-model="statusFilter" @change="fetchMusicList">
        <el-radio-button :value="-1">全部</el-radio-button>
        <el-radio-button :value="0">待审核</el-radio-button>
        <el-radio-button :value="1">已上架</el-radio-button>
      </el-radio-group>
    </div>

    <!-- 音乐表格 -->
    <el-table :data="musicList" border style="width: 100%">
      <el-table-column prop="id" label="ID" width="80" />
      <el-table-column prop="title" label="歌曲名" width="150" />
      <!-- 歌手：通过 ID 查映射表显示名字 -->
      <el-table-column label="歌手" width="120">
        <template #default="{ row }">
          {{ getSingerName(row.singer_id) }}
        </template>
      </el-table-column>
      <!-- 专辑：通过 ID 查映射表显示名字 -->
      <el-table-column label="专辑" width="120">
        <template #default="{ row }">
          {{ getAlbumName(row.album_id) }}
        </template>
      </el-table-column>
      <el-table-column prop="file_url" label="文件路径" width="200" />
      <el-table-column prop="duration" label="时长(秒)" width="100" />
      <el-table-column prop="play_count" label="播放次数" width="100" />
      <el-table-column prop="status" label="状态" width="100">
        <template #default="{ row }">
          <el-tag :type="row.status === 1 ? 'success' : 'warning'">
            {{ row.status === 1 ? '已上架' : '待审核' }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column label="操作" width="200">
        <template #default="{ row }">
          <el-button
            v-if="row.status === 0"
            type="success"
            size="small"
            @click="handleAudit(row, 1)"
          >
            通过上架
          </el-button>
          <el-button
            v-if="row.status === 1"
            type="warning"
            size="small"
            @click="handleAudit(row, 0)"
          >
            下架
          </el-button>
        </template>
      </el-table-column>
    </el-table>

    <!-- 分页 -->
    <div style="margin-top: 20px; display: flex; justify-content: center">
      <el-pagination
        v-model:current-page="page"
        :page-size="pageSize"
        :total="total"
        layout="prev, pager, next"
        @current-change="fetchMusicList"
      />
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import api from '../../api/index.js'
import { ElMessage, ElMessageBox } from 'element-plus'

const musicList = ref([])
const page = ref(1)
const pageSize = ref(10)
const total = ref(0)
const statusFilter = ref(-1)  // -1 表示全部，0 表示待审核，1 表示已上架
const singerMap = ref({})      // 歌手 ID → 歌手名 的映射表
const albumMap = ref({})       // 专辑 ID → 专辑名 的映射表

// 获取管理员请求头（所有管理员接口都需要带 Token）
const getAuthHeaders = () => {
  const token = localStorage.getItem('token')
  return { Authorization: 'Bearer ' + token }
}

// 获取音乐列表（统一使用管理员接口，通过 status 参数筛选）
const fetchMusicList = async () => {
  try {
    const res = await api.get('/admin/music/list', {
      params: {
        page: page.value,
        page_size: pageSize.value,
        status: statusFilter.value  // -1=全部，0=待审核，1=已上架
      },
      headers: getAuthHeaders()  // 带管理员 Token
    })
    musicList.value = res.data.items
    total.value = res.data.total
  } catch (error) {
    ElMessage.error('获取音乐列表失败')
  }
}

// 审核音乐（上架/下架）
const handleAudit = async (row, newStatus) => {
  const action = newStatus === 1 ? '上架' : '下架'

  try {
    await ElMessageBox.confirm(`确定要${action}歌曲 "${row.title}" 吗？`, '提示', {
      type: 'warning'
    })

    // 调用管理员审核接口（带 Token）
    await api.put(`/admin/music/${row.id}/audit`, { status: newStatus }, {
      headers: getAuthHeaders()
    })
    ElMessage.success(`${action}成功`)
    row.status = newStatus
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error(error.response?.data?.detail || `${action}失败`)
    }
  }
}

// 获取歌手列表，构建 ID → 名字 映射
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

// 获取专辑列表，构建 ID → 名字 映射
const fetchAlbumMap = async () => {
  try {
    const res = await api.get('/album/list', {
      params: { page: 1, page_size: 200 }
    })
    const map = {}
    res.data.items.forEach(album => {
      map[album.id] = album.name
    })
    albumMap.value = map
  } catch (error) {
    console.error('获取专辑列表失败', error)
  }
}

// 根据歌手 ID 获取名字
const getSingerName = (singerId) => {
  return singerMap.value[singerId] || '未知歌手'
}

// 根据专辑 ID 获取名字
const getAlbumName = (albumId) => {
  if (!albumId) return '-'
  return albumMap.value[albumId] || '未知专辑'
}

onMounted(() => {
  fetchMusicList()
  fetchSingerMap()
  fetchAlbumMap()
})
</script>
