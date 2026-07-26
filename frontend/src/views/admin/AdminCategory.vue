<template>
  <div>
    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px">
      <h2 style="margin: 0">分类管理</h2>
      <el-button type="primary" @click="openAddDialog">+ 新增分类</el-button>
    </div>

    <!-- 分类列表 -->
    <el-table :data="categoryList" border stripe>
      <!-- 分类名 -->
      <el-table-column prop="name" label="分类名" />
      <!-- 操作列：编辑 + 删除 -->
      <el-table-column label="操作" width="160">
        <template #default="{ row }">
          <el-button type="primary" link @click="openEditDialog(row)">编辑</el-button>
          <el-popconfirm title="确定删除该分类吗？" @confirm="handleDelete(row.id)">
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
    <el-dialog v-model="dialogVisible" :title="isEdit ? '编辑分类' : '新增分类'" width="400px">
      <el-form ref="dialogFormRef" :model="dialogForm" :rules="dialogRules" label-width="80px">
        <!-- 分类名（必填） -->
        <el-form-item label="分类名" prop="name">
          <el-input v-model="dialogForm.name" placeholder="请输入分类名" />
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

const categoryList = ref([])  // 分类列表
const page = ref(1)           // 当前页
const pageSize = ref(10)      // 每页条数
const total = ref(0)          // 总数

// 获取分类列表
const fetchList = async () => {
  try {
    const res = await api.get('/category/list', {
      params: { page: page.value, page_size: pageSize.value }
    })
    categoryList.value = res.data.items
    total.value = res.data.total
  } catch (error) {
    ElMessage.error('获取分类列表失败')
  }
}

// ========== 弹窗相关 ==========

const dialogVisible = ref(false)   // 弹窗是否显示
const isEdit = ref(false)          // 是否编辑模式
const editId = ref(null)           // 编辑中的分类 ID
const submitting = ref(false)      // 提交中
const dialogFormRef = ref(null)    // 弹窗表单引用

// 弹窗表单数据
const dialogForm = ref({
  name: ''
})

// 弹窗表单验证规则
const dialogRules = {
  name: [{ required: true, message: '请输入分类名', trigger: 'blur' }]
}

// 打开新增弹窗
const openAddDialog = () => {
  isEdit.value = false
  editId.value = null
  dialogForm.value = { name: '' }
  dialogVisible.value = true
}

// 打开编辑弹窗（把当前行数据填入表单）
const openEditDialog = (row) => {
  isEdit.value = true
  editId.value = row.id
  dialogForm.value = { name: row.name }
  dialogVisible.value = true
}

// ========== 请求头 ==========

// 获取请求头（带 JWT token）
const getAuthHeaders = () => {
  const token = localStorage.getItem('token')
  return token ? { Authorization: 'Bearer ' + token } : {}
}

// ========== 提交 / 删除 ==========

// 提交新增或编辑
const handleSubmit = async () => {
  const valid = await dialogFormRef.value.validate().catch(() => false)
  if (!valid) return

  submitting.value = true
  try {
    if (isEdit.value) {
      // 编辑模式：PUT /category/update/{id}
      await api.put(`/category/update/${editId.value}`, dialogForm.value, {
        headers: getAuthHeaders()
      })
      ElMessage.success('修改成功')
    } else {
      // 新增模式：POST /category/create
      await api.post('/category/create', dialogForm.value, {
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

// 删除分类
const handleDelete = async (id) => {
  try {
    await api.delete(`/category/delete/${id}`, {
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
