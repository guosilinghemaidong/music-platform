<template>
  <div>
    <h2>用户管理</h2>

    <!-- 用户表格 -->
    <el-table :data="userList" border style="width: 100%">
      <el-table-column prop="id" label="ID" width="80" />
      <el-table-column prop="username" label="用户名" width="120" />
      <el-table-column prop="nickname" label="昵称" width="120">
        <template #default="{ row }">
          <el-input v-if="row._editing" v-model="row.nickname" size="small" />
          <span v-else>{{ row.nickname || '-' }}</span>
        </template>
      </el-table-column>
      <el-table-column prop="avatar" label="头像" width="150">
        <template #default="{ row }">
          <el-input v-if="row._editing" v-model="row.avatar" size="small" placeholder="头像路径" />
          <span v-else>{{ row.avatar || '-' }}</span>
        </template>
      </el-table-column>
      <el-table-column prop="role" label="角色" width="100">
        <template #default="{ row }">
          <el-tag :type="row.role === 'admin' ? 'danger' : 'success'">
            {{ row.role === 'admin' ? '管理员' : '用户' }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="status" label="状态" width="100">
        <template #default="{ row }">
          <el-tag :type="row.status === 1 ? 'success' : 'danger'">
            {{ row.status === 1 ? '正常' : '禁用' }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column label="操作" width="250">
        <template #default="{ row }">
          <!-- 编辑模式 -->
          <template v-if="row._editing">
            <el-button type="success" size="small" @click="handleSave(row)">保存</el-button>
            <el-button size="small" @click="handleCancel(row)">取消</el-button>
          </template>
          <!-- 查看模式 -->
          <template v-else>
            <el-button type="primary" size="small" @click="handleEdit(row)">编辑</el-button>
            <el-button
              :type="row.status === 1 ? 'danger' : 'success'"
              size="small"
              @click="handleToggleStatus(row)"
            >
              {{ row.status === 1 ? '禁用' : '启用' }}
            </el-button>
          </template>
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
        @current-change="fetchUsers"
      />
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import api from '../../api/index.js'
import { ElMessage, ElMessageBox } from 'element-plus'

const userList = ref([])
const page = ref(1)
const pageSize = ref(10)
const total = ref(0)

// 获取管理员请求头（所有管理员接口都需要带 Token）
const getAuthHeaders = () => {
  const token = localStorage.getItem('token')
  return { Authorization: 'Bearer ' + token }
}

// 获取用户列表（只查普通用户，role=user）
const fetchUsers = async () => {
  try {
    const res = await api.get('/admin/users', {
      params: { page: page.value, page_size: pageSize.value, role: 'user' },  // 只查普通用户
      headers: getAuthHeaders()  // 带管理员 Token
    })
    // 给每行加一个 _editing 属性，控制编辑模式
    userList.value = res.data.items.map(item => ({ ...item, _editing: false }))
    total.value = res.data.total
  } catch (error) {
    ElMessage.error('获取用户列表失败')
  }
}

// 点击编辑按钮
const handleEdit = (row) => {
  // 保存原始数据，用于取消时恢复
  row._originalNickname = row.nickname
  row._originalAvatar = row.avatar
  row._editing = true
}

// 点击取消按钮
const handleCancel = (row) => {
  // 恢复原始数据
  row.nickname = row._originalNickname
  row.avatar = row._originalAvatar
  row._editing = false
}

// 点击保存按钮
const handleSave = async (row) => {
  try {
    // 调用后端接口修改用户信息（带管理员 Token）
    await api.put(`/admin/user/${row.id}/update`, {
      nickname: row.nickname,
      avatar: row.avatar
    }, { headers: getAuthHeaders() })
    ElMessage.success('修改成功')
    row._editing = false
  } catch (error) {
    ElMessage.error(error.response?.data?.detail || '修改失败')
  }
}

// 切换用户状态（禁用/启用）
const handleToggleStatus = async (row) => {
  const newStatus = row.status === 1 ? 0 : 1
  const action = newStatus === 1 ? '启用' : '禁用'

  try {
    // 弹出确认框
    await ElMessageBox.confirm(`确定要${action}用户 "${row.username}" 吗？`, '提示', {
      type: 'warning'
    })

    // 调用后端接口修改状态（带管理员 Token）
    await api.put(`/admin/user/${row.id}/status`, { status: newStatus }, {
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

onMounted(() => {
  fetchUsers()
})
</script>
