<template>
  <div>
    <h2 style="margin: 0 0 15px 0">动态管理</h2>

    <!-- 状态筛选栏 -->
    <div style="margin-bottom: 15px; display: flex; gap: 10px">
      <el-radio-group v-model="statusFilter" @change="handleStatusChange">
        <el-radio-button :value="-1">全部</el-radio-button>
        <el-radio-button :value="0">待审核</el-radio-button>
        <el-radio-button :value="1">已通过</el-radio-button>
        <el-radio-button :value="2">已拒绝</el-radio-button>
      </el-radio-group>
    </div>

    <!-- 动态列表 -->
    <el-table :data="postList" border stripe>
      <!-- 内容列 -->
      <el-table-column prop="content" label="内容" show-overflow-tooltip min-width="200" />
      <!-- 发布者 -->
      <el-table-column prop="username" label="发布者" width="100" />
      <!-- 图片预览 -->
      <el-table-column label="图片" width="100">
        <template #default="{ row }">
          <template v-if="parseImages(row.images).length > 0">
            <img
              :src="'http://localhost:8000' + parseImages(row.images)[0]"
              style="width: 40px; height: 40px; object-fit: cover; border-radius: 4px"
            />
            <span v-if="parseImages(row.images).length > 1" style="margin-left: 4px; color: #999; font-size: 12px">
              +{{ parseImages(row.images).length - 1 }}
            </span>
          </template>
          <span v-else style="color: #999">无</span>
        </template>
      </el-table-column>
      <!-- 关联音乐 -->
      <el-table-column label="关联音乐" width="100">
        <template #default="{ row }">
          <span v-if="row.music_id">ID: {{ row.music_id }}</span>
          <span v-else style="color: #999">无</span>
        </template>
      </el-table-column>
      <!-- 状态标签 -->
      <el-table-column label="状态" width="90">
        <template #default="{ row }">
          <el-tag v-if="row.status === 0" type="warning" size="small">待审核</el-tag>
          <el-tag v-else-if="row.status === 1" type="success" size="small">已通过</el-tag>
          <el-tag v-else-if="row.status === 2" type="danger" size="small">已拒绝</el-tag>
        </template>
      </el-table-column>
      <!-- 点赞数 -->
      <el-table-column prop="like_count" label="点赞" width="70" />
      <!-- 评论数 -->
      <el-table-column prop="comment_count" label="评论" width="70" />
      <!-- 发布时间 -->
      <el-table-column label="发布时间" width="160">
        <template #default="{ row }">
          {{ formatTime(row.create_time) }}
        </template>
      </el-table-column>
      <!-- 操作列 -->
      <el-table-column label="操作" width="200" fixed="right">
        <template #default="{ row }">
          <!-- 待审核状态：显示通过/拒绝按钮 -->
          <template v-if="row.status === 0">
            <el-button type="success" link @click="handleAudit(row.id, 1)">通过</el-button>
            <el-button type="warning" link @click="handleAudit(row.id, 2)">拒绝</el-button>
          </template>
          <!-- 已通过/已拒绝：显示撤回/恢复按钮 -->
          <template v-else-if="row.status === 1">
            <el-button type="warning" link @click="handleAudit(row.id, 2)">拒绝</el-button>
          </template>
          <template v-else-if="row.status === 2">
            <el-button type="success" link @click="handleAudit(row.id, 1)">通过</el-button>
          </template>
          <!-- 删除按钮（所有状态都可删除） -->
          <el-popconfirm title="确定删除该动态吗？删除后不可恢复。" @confirm="handleDelete(row.id)">
            <template #reference>
              <el-button type="danger" link>删除</el-button>
            </template>
          </el-popconfirm>
        </template>
      </el-table-column>
    </el-table>

    <!-- 分页组件 -->
    <div style="margin-top: 15px; display: flex; justify-content: flex-end">
      <el-pagination
        v-model:current-page="page"
        :page-size="pageSize"
        :total="total"
        layout="total, prev, pager, next"
        @current-change="fetchList"
      />
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import api from '../../api/index.js'
import { ElMessage } from 'element-plus'

// ========== 列表相关 ==========

const postList = ref([])   // 动态列表
const page = ref(1)        // 当前页
const pageSize = ref(10)   // 每页条数
const total = ref(0)       // 总数
const statusFilter = ref(-1)  // 状态筛选：-1=全部，0=待审核，1=已通过，2=已拒绝

// 获取动态列表
const fetchList = async () => {
  try {
    const res = await api.get('/admin/post/list', {
      params: {
        page: page.value,
        page_size: pageSize.value,
        status: statusFilter.value
      },
      headers: getAuthHeaders()
    })
    postList.value = res.data.items
    total.value = res.data.total
  } catch (error) {
    ElMessage.error('获取动态列表失败')
  }
}

// 切换状态筛选时，重置到第一页
const handleStatusChange = () => {
  page.value = 1
  fetchList()
}

// ========== 审核操作 ==========

// 审核动态（通过/拒绝）
const handleAudit = async (postId, status) => {
  const actionText = status === 1 ? '通过' : '拒绝'
  try {
    await api.put(`/admin/post/${postId}/audit`, { status }, {
      headers: getAuthHeaders()
    })
    ElMessage.success(`已${actionText}`)
    fetchList()  // 刷新列表
  } catch (error) {
    ElMessage.error(error.response?.data?.detail || '操作失败')
  }
}

// ========== 删除操作 ==========

// 删除动态
const handleDelete = async (postId) => {
  try {
    await api.delete(`/admin/post/${postId}`, {
      headers: getAuthHeaders()
    })
    ElMessage.success('删除成功')
    fetchList()  // 刷新列表
  } catch (error) {
    ElMessage.error(error.response?.data?.detail || '删除失败')
  }
}

// ========== 工具函数 ==========

// 获取请求头（带 JWT token）
const getAuthHeaders = () => {
  const token = localStorage.getItem('token')
  return token ? { Authorization: 'Bearer ' + token } : {}
}

// 解析图片 JSON 字符串为数组
const parseImages = (imagesStr) => {
  if (!imagesStr) return []
  try {
    const arr = JSON.parse(imagesStr)
    return Array.isArray(arr) ? arr : []
  } catch {
    return []
  }
}

// 格式化时间
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

// ========== 生命周期 ==========

onMounted(() => {
  fetchList()
})
</script>
