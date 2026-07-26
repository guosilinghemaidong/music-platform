<template>
  <div>
    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px">
      <h2 style="margin: 0">歌手管理</h2>
      <el-button type="primary" @click="openAddDialog">+ 新增歌手</el-button>
    </div>

    <!-- 歌手列表 -->
    <el-table :data="singerList" border stripe>
      <!-- 头像列 -->
      <el-table-column label="头像" width="80">
        <template #default="{ row }">
          <img
            v-if="row.avatar"
            :src="'http://localhost:8000' + row.avatar"
            style="width: 40px; height: 40px; border-radius: 50%; object-fit: cover"
          />
          <span v-else style="color: #999">无</span>
        </template>
      </el-table-column>
      <!-- 歌手名列 -->
      <el-table-column prop="name" label="歌手名" />
      <!-- 性别列：0未知 1男 2女 -->
      <el-table-column label="性别" width="80">
        <template #default="{ row }">
          <span v-if="row.gender === 1">男</span>
          <span v-else-if="row.gender === 2">女</span>
          <span v-else style="color: #999">未知</span>
        </template>
      </el-table-column>
      <!-- 简介列 -->
      <el-table-column prop="introduction" label="简介" show-overflow-tooltip />
      <!-- 操作列：编辑 + 删除 -->
      <el-table-column label="操作" width="160">
        <template #default="{ row }">
          <el-button type="primary" link @click="openEditDialog(row)">编辑</el-button>
          <el-popconfirm title="确定删除该歌手吗？" @confirm="handleDelete(row.id)">
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

    <!-- 新增 / 编辑弹窗 -->
    <el-dialog v-model="dialogVisible" :title="isEdit ? '编辑歌手' : '新增歌手'" width="500px">
      <el-form ref="dialogFormRef" :model="dialogForm" :rules="dialogRules" label-width="80px">
        <!-- 歌手名（必填） -->
        <el-form-item label="歌手名" prop="name">
          <el-input v-model="dialogForm.name" placeholder="请输入歌手名" />
        </el-form-item>
        <!-- 头像上传 -->
        <el-form-item label="头像">
          <el-upload
            action=""
            :http-request="uploadAvatar"
            :before-upload="beforeImageUpload"
            :show-file-list="false"
          >
            <img v-if="dialogForm.avatar" :src="'http://localhost:8000' + dialogForm.avatar" class="avatar-preview" />
            <el-button v-else type="primary" size="small">上传头像</el-button>
          </el-upload>
          <span v-if="dialogForm.avatar" style="margin-left: 10px; color: #67c23a; font-size: 12px">已上传</span>
        </el-form-item>
        <!-- 性别选择 -->
        <el-form-item label="性别">
          <el-radio-group v-model="dialogForm.gender">
            <el-radio :value="0">未知</el-radio>
            <el-radio :value="1">男</el-radio>
            <el-radio :value="2">女</el-radio>
          </el-radio-group>
        </el-form-item>
        <!-- 简介 -->
        <el-form-item label="简介">
          <el-input v-model="dialogForm.introduction" type="textarea" :rows="3" placeholder="请输入歌手简介" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSubmit" :loading="submitting">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import api from '../../api/index.js'
import { ElMessage } from 'element-plus'

// ========== 列表相关 ==========

const singerList = ref([])  // 歌手列表
const page = ref(1)         // 当前页
const pageSize = ref(10)    // 每页条数
const total = ref(0)        // 总数

// 获取歌手列表
const fetchList = async () => {
  try {
    const res = await api.get('/singer/list', {
      params: { page: page.value, page_size: pageSize.value }
    })
    singerList.value = res.data.items
    total.value = res.data.total
  } catch (error) {
    ElMessage.error('获取歌手列表失败')
  }
}

// ========== 弹窗相关 ==========

const dialogVisible = ref(false)   // 弹窗是否显示
const isEdit = ref(false)          // 是否编辑模式
const editId = ref(null)           // 编辑中的歌手 ID
const submitting = ref(false)      // 提交中
const dialogFormRef = ref(null)    // 弹窗表单引用

// 弹窗表单数据
const dialogForm = ref({
  name: '',
  avatar: '',
  gender: 0,
  introduction: ''
})

// 弹窗表单验证规则
const dialogRules = {
  name: [{ required: true, message: '请输入歌手名', trigger: 'blur' }]
}

// 打开新增弹窗
const openAddDialog = () => {
  isEdit.value = false
  editId.value = null
  dialogForm.value = { name: '', avatar: '', gender: 0, introduction: '' }
  dialogVisible.value = true
}

// 打开编辑弹窗（把当前行数据填入表单）
const openEditDialog = (row) => {
  isEdit.value = true
  editId.value = row.id
  dialogForm.value = {
    name: row.name,
    avatar: row.avatar || '',
    gender: row.gender ?? 0,
    introduction: row.introduction || ''
  }
  dialogVisible.value = true
}

// ========== 文件上传 ==========

// 获取请求头（带 JWT token）
const getAuthHeaders = () => {
  const token = localStorage.getItem('token')
  return token ? { Authorization: 'Bearer ' + token } : {}
}

// 上传前校验图片格式
const beforeImageUpload = (file) => {
  const ext = file.name.split('.').pop().toLowerCase()
  const allowed = ['jpg', 'jpeg', 'png', 'gif', 'webp']
  if (!allowed.includes(ext)) {
    ElMessage.error(`不支持的图片格式：.${ext}`)
    return false
  }
  return true
}

// 自定义上传头像
const uploadAvatar = async (options) => {
  const formData = new FormData()
  formData.append('file', options.file)
  try {
    const res = await api.post('/upload/image', formData, {
      headers: { ...getAuthHeaders(), 'Content-Type': 'multipart/form-data' }
    })
    dialogForm.value.avatar = res.data.filename
    ElMessage.success('头像上传成功')
  } catch (error) {
    ElMessage.error('头像上传失败')
  }
}

// ========== 提交 / 删除 ==========

// 提交新增或编辑
const handleSubmit = async () => {
  const valid = await dialogFormRef.value.validate().catch(() => false)
  if (!valid) return

  submitting.value = true
  try {
    if (isEdit.value) {
      // 编辑模式：PUT /singer/update/{id}
      await api.put(`/singer/update/${editId.value}`, dialogForm.value, {
        headers: getAuthHeaders()
      })
      ElMessage.success('修改成功')
    } else {
      // 新增模式：POST /singer/create
      await api.post('/singer/create', dialogForm.value, {
        headers: getAuthHeaders()
      })
      ElMessage.success('添加成功')
    }
    dialogVisible.value = false
    fetchList()  // 刷新列表
  } catch (error) {
    ElMessage.error(error.response?.data?.detail || '操作失败')
  } finally {
    submitting.value = false
  }
}

// 删除歌手
const handleDelete = async (id) => {
  try {
    await api.delete(`/singer/delete/${id}`, {
      headers: getAuthHeaders()
    })
    ElMessage.success('删除成功')
    fetchList()  // 刷新列表
  } catch (error) {
    ElMessage.error(error.response?.data?.detail || '删除失败')
  }
}

// ========== 生命周期 ==========

onMounted(() => {
  fetchList()
})
</script>

<style scoped>
/* 头像预览图（弹窗内） */
.avatar-preview {
  width: 60px;
  height: 60px;
  border-radius: 50%;
  object-fit: cover;
  border: 1px solid #eee;
}
</style>
