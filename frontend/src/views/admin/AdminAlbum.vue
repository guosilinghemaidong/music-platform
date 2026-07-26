<template>
  <div>
    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px">
      <h2 style="margin: 0">专辑管理</h2>
      <el-button type="primary" @click="openAddDialog">+ 新增专辑</el-button>
    </div>

    <!-- 专辑列表 -->
    <el-table :data="albumList" border stripe>
      <!-- 专辑名 -->
      <el-table-column prop="name" label="专辑名" />
      <!-- 所属歌手（通过 singerMap 把 singer_id 转成歌手名） -->
      <el-table-column label="所属歌手">
        <template #default="{ row }">
          {{ singerMap[row.singer_id] || `ID:${row.singer_id}` }}
        </template>
      </el-table-column>
      <!-- 封面 -->
      <el-table-column label="封面" width="80">
        <template #default="{ row }">
          <img
            v-if="row.cover"
            :src="'http://localhost:8000' + row.cover"
            style="width: 40px; height: 40px; border-radius: 4px; object-fit: cover"
          />
          <span v-else style="color: #999">无</span>
        </template>
      </el-table-column>
      <!-- 发行日期 -->
      <el-table-column prop="release_date" label="发行日期" width="120">
        <template #default="{ row }">
          {{ row.release_date || '未设置' }}
        </template>
      </el-table-column>
      <!-- 操作列：编辑 + 删除 -->
      <el-table-column label="操作" width="160">
        <template #default="{ row }">
          <el-button type="primary" link @click="openEditDialog(row)">编辑</el-button>
          <el-popconfirm title="确定删除该专辑吗？" @confirm="handleDelete(row.id)">
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
    <el-dialog v-model="dialogVisible" :title="isEdit ? '编辑专辑' : '新增专辑'" width="500px">
      <el-form ref="dialogFormRef" :model="dialogForm" :rules="dialogRules" label-width="80px">
        <!-- 专辑名（必填） -->
        <el-form-item label="专辑名" prop="name">
          <el-input v-model="dialogForm.name" placeholder="请输入专辑名" />
        </el-form-item>
        <!-- 所属歌手（必填，下拉选择） -->
        <el-form-item label="所属歌手" prop="singer_id">
          <el-select v-model="dialogForm.singer_id" placeholder="请选择歌手" style="width: 100%">
            <el-option
              v-for="singer in singerList"
              :key="singer.id"
              :label="singer.name"
              :value="singer.id"
            />
          </el-select>
        </el-form-item>
        <!-- 封面上传 -->
        <el-form-item label="封面">
          <el-upload
            action=""
            :http-request="uploadCover"
            :before-upload="beforeImageUpload"
            :show-file-list="false"
          >
            <img v-if="dialogForm.cover" :src="'http://localhost:8000' + dialogForm.cover" class="cover-preview" />
            <el-button v-else type="primary" size="small">上传封面</el-button>
          </el-upload>
          <span v-if="dialogForm.cover" style="margin-left: 10px; color: #67c23a; font-size: 12px">已上传</span>
        </el-form-item>
        <!-- 发行日期 -->
        <el-form-item label="发行日期">
          <el-date-picker
            v-model="dialogForm.release_date"
            type="date"
            placeholder="选择发行日期"
            value-format="YYYY-MM-DD"
            style="width: 100%"
          />
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

const albumList = ref([])   // 专辑列表
const page = ref(1)         // 当前页
const pageSize = ref(10)    // 每页条数
const total = ref(0)        // 总数

// 获取专辑列表
const fetchList = async () => {
  try {
    const res = await api.get('/album/list', {
      params: { page: page.value, page_size: pageSize.value }
    })
    albumList.value = res.data.items
    total.value = res.data.total
  } catch (error) {
    ElMessage.error('获取专辑列表失败')
  }
}

// ========== 歌手映射（用于把 singer_id 显示成歌手名） ==========

const singerList = ref([])   // 歌手列表（弹窗下拉 + 列表显示用）
const singerMap = ref({})    // singer_id → 歌手名 的映射

// 获取歌手列表（用于下拉和名称映射）
const fetchSingerList = async () => {
  try {
    const res = await api.get('/singer/list', {
      params: { page: 1, page_size: 200 }
    })
    singerList.value = res.data.items
    // 构建 id → name 映射
    const map = {}
    res.data.items.forEach(s => { map[s.id] = s.name })
    singerMap.value = map
  } catch (error) {
    console.error('获取歌手列表失败', error)
  }
}

// ========== 弹窗相关 ==========

const dialogVisible = ref(false)   // 弹窗是否显示
const isEdit = ref(false)          // 是否编辑模式
const editId = ref(null)           // 编辑中的专辑 ID
const submitting = ref(false)      // 提交中
const dialogFormRef = ref(null)    // 弹窗表单引用

// 弹窗表单数据
const dialogForm = ref({
  name: '',
  singer_id: null,
  cover: '',
  release_date: ''
})

// 弹窗表单验证规则
const dialogRules = {
  name: [{ required: true, message: '请输入专辑名', trigger: 'blur' }],
  singer_id: [{ required: true, message: '请选择所属歌手', trigger: 'change' }]
}

// 打开新增弹窗
const openAddDialog = () => {
  isEdit.value = false
  editId.value = null
  dialogForm.value = { name: '', singer_id: null, cover: '', release_date: '' }
  dialogVisible.value = true
}

// 打开编辑弹窗（把当前行数据填入表单）
const openEditDialog = (row) => {
  isEdit.value = true
  editId.value = row.id
  dialogForm.value = {
    name: row.name,
    singer_id: row.singer_id,
    cover: row.cover || '',
    release_date: row.release_date || ''
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

// 自定义上传封面
const uploadCover = async (options) => {
  const formData = new FormData()
  formData.append('file', options.file)
  try {
    const res = await api.post('/upload/image', formData, {
      headers: { ...getAuthHeaders(), 'Content-Type': 'multipart/form-data' }
    })
    dialogForm.value.cover = res.data.filename
    ElMessage.success('封面上传成功')
  } catch (error) {
    ElMessage.error('封面上传失败')
  }
}

// ========== 提交 / 删除 ==========

// 提交新增或编辑
const handleSubmit = async () => {
  const valid = await dialogFormRef.value.validate().catch(() => false)
  if (!valid) return

  submitting.value = true
  try {
    // 构造提交数据（空字符串转 null）
    const data = {
      name: dialogForm.value.name,
      singer_id: dialogForm.value.singer_id,
      cover: dialogForm.value.cover || null,
      release_date: dialogForm.value.release_date || null
    }

    if (isEdit.value) {
      // 编辑模式：PUT /album/update/{id}
      await api.put(`/album/update/${editId.value}`, data, {
        headers: getAuthHeaders()
      })
      ElMessage.success('修改成功')
    } else {
      // 新增模式：POST /album/create
      await api.post('/album/create', data, {
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

// 删除专辑
const handleDelete = async (id) => {
  try {
    await api.delete(`/album/delete/${id}`, {
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
  fetchSingerList()  // 先加载歌手列表（用于映射名称）
  fetchList()        // 再加载专辑列表
})
</script>

<style scoped>
/* 封面预览图（弹窗内） */
.cover-preview {
  width: 60px;
  height: 60px;
  border-radius: 4px;
  object-fit: cover;
  border: 1px solid #eee;
}
</style>
