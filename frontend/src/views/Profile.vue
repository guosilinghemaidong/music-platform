<template>
  <div>
    <h2>个人资料</h2>

    <!-- 用户信息展示卡片 -->
    <el-card style="margin-top: 20px">
      <template #header>
        <div style="display: flex; justify-content: space-between; align-items: center">
          <span>基本信息</span>
          <!-- 点击切换编辑/查看模式 -->
          <el-button v-if="!editing" type="primary" size="small" @click="startEdit">编辑</el-button>
          <div v-else>
            <el-button type="success" size="small" @click="handleSave">保存</el-button>
            <el-button size="small" @click="cancelEdit">取消</el-button>
          </div>
        </div>
      </template>

      <!-- 头像区域 -->
      <div style="display: flex; align-items: center; margin-bottom: 20px">
        <!-- 查看模式：展示头像 -->
        <el-avatar v-if="!editing" :size="80" :src="avatarUrl">
          <el-icon :size="40"><User /></el-icon>
        </el-avatar>
        <!-- 编辑模式：上传头像 -->
        <div v-else style="display: flex; align-items: center; gap: 20px">
          <el-avatar :size="80" :src="editForm.avatar || userInfo.avatar">
            <el-icon :size="40"><User /></el-icon>
          </el-avatar>
          <el-upload
            :show-file-list="false"
            :http-request="handleAvatarUpload"
            accept="image/*"
          >
            <el-button size="small" type="primary">更换头像</el-button>
          </el-upload>
        </div>
        <span style="margin-left: 16px; font-size: 18px; font-weight: bold">{{ userInfo.username }}</span>
      </div>

      <!-- 查看模式：展示用户信息 -->
      <el-descriptions v-if="!editing" :column="1" border>
        <el-descriptions-item label="用户名">{{ userInfo.username }}</el-descriptions-item>
        <el-descriptions-item label="昵称">{{ userInfo.nickname || '未设置' }}</el-descriptions-item>
        <el-descriptions-item label="角色">
          <el-tag :type="userInfo.role === 'admin' ? 'danger' : 'primary'">
            {{ userInfo.role === 'admin' ? '管理员' : '普通用户' }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="个性签名">
          {{ userInfo.signature || '未设置' }}
        </el-descriptions-item>
      </el-descriptions>

      <!-- 编辑模式：表单修改信息 -->
      <el-form v-else :model="editForm" label-width="80px">
        <el-form-item label="用户名">
          <el-input :value="userInfo.username" disabled />
        </el-form-item>
        <el-form-item label="昵称">
          <el-input v-model="editForm.nickname" placeholder="请输入昵称" />
        </el-form-item>
        <el-form-item label="个性签名">
          <el-input v-model="editForm.signature" type="textarea" :rows="2" placeholder="写一句话介绍自己吧" />
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 修改密码卡片 -->
    <el-card style="margin-top: 20px">
      <template #header>
        <span>修改密码</span>
      </template>
      <el-form :model="passwordForm" label-width="100px" style="max-width: 400px">
        <el-form-item label="旧密码">
          <el-input v-model="passwordForm.old_password" type="password" placeholder="请输入旧密码" />
        </el-form-item>
        <el-form-item label="新密码">
          <el-input v-model="passwordForm.new_password" type="password" placeholder="请输入新密码" />
        </el-form-item>
        <el-form-item label="确认新密码">
          <el-input v-model="passwordForm.confirm_password" type="password" placeholder="再次输入新密码" />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleChangePassword">修改密码</el-button>
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { User } from '@element-plus/icons-vue'
import api from '../api/index.js'
import { ElMessage } from 'element-plus'

// 用户信息（从后端获取）
const userInfo = ref({
  username: '',
  nickname: '',
  avatar: '',
  signature: '',
  role: ''
})

// 编辑表单的数据
const editForm = reactive({
  nickname: '',
  avatar: '',
  signature: ''
})

// 头像的完整 URL（后端返回的是 /static/images/xxx 相对路径，需要拼上后端地址）
const avatarUrl = computed(() => {
  if (userInfo.value.avatar) {
    return '' + userInfo.value.avatar
  }
  return ''
})

// 是否处于编辑模式
const editing = ref(false)

// 修改密码的表单数据
const passwordForm = reactive({
  old_password: '',
  new_password: '',
  confirm_password: ''
})

// 获取当前登录用户的信息（调用 GET /user/me）
const fetchUserInfo = async () => {
  try {
    const token = localStorage.getItem('token')
    const res = await api.get('/user/me', {
      headers: { Authorization: 'Bearer ' + token }
    })
    userInfo.value = res.data
  } catch (error) {
    ElMessage.error(error.response?.data?.detail || '获取用户信息失败')
  }
}

// 进入编辑模式，把当前昵称和头像填入表单
const startEdit = () => {
  editForm.nickname = userInfo.value.nickname || ''
  editForm.avatar = userInfo.value.avatar || ''
  editForm.signature = userInfo.value.signature || ''
  editing.value = true
}

// 取消编辑，退出编辑模式
const cancelEdit = () => {
  editing.value = false
}

// 保存修改（调用 PUT /user/me）
const handleSave = async () => {
  try {
    const token = localStorage.getItem('token')
    await api.put('/user/me', {
      nickname: editForm.nickname,
      avatar: editForm.avatar,
      signature: editForm.signature
    }, {
      headers: { Authorization: 'Bearer ' + token }
    })

    // 更新页面上显示的信息
    userInfo.value.nickname = editForm.nickname
    userInfo.value.avatar = editForm.avatar
    userInfo.value.signature = editForm.signature

    // 同步更新 localStorage 里的用户名（如果改了昵称的话）
    localStorage.setItem('username', editForm.nickname || userInfo.value.username)

    editing.value = false
    ElMessage.success('修改成功')
  } catch (error) {
    ElMessage.error(error.response?.data?.detail || '修改失败')
  }
}

// 上传头像（自定义上传，调用 POST /upload/image）
const handleAvatarUpload = async (options) => {
  try {
    const token = localStorage.getItem('token')
    const formData = new FormData()
    formData.append('file', options.file)

    const res = await api.post('/upload/image', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
        Authorization: 'Bearer ' + token
      }
    })

    // 上传成功，把返回的路径存到 editForm.avatar
    editForm.avatar = res.data.filename
    ElMessage.success('头像已上传，点保存生效')
  } catch (error) {
    ElMessage.error('头像上传失败')
  }
}

// 修改密码（调用 PUT /user/password）
const handleChangePassword = async () => {
  // 1. 前端校验：两次新密码是否一致
  if (passwordForm.new_password !== passwordForm.confirm_password) {
    ElMessage.error('两次输入的新密码不一致')
    return
  }
  // 2. 前端校验：新密码不能为空
  if (!passwordForm.old_password || !passwordForm.new_password) {
    ElMessage.error('请填写完整的密码信息')
    return
  }

  try {
    const token = localStorage.getItem('token')
    await api.put('/user/password', {
      old_password: passwordForm.old_password,
      new_password: passwordForm.new_password
    }, {
      headers: { Authorization: 'Bearer ' + token }
    })

    ElMessage.success('密码修改成功')
    // 清空表单
    passwordForm.old_password = ''
    passwordForm.new_password = ''
    passwordForm.confirm_password = ''
  } catch (error) {
    ElMessage.error(error.response?.data?.detail || '密码修改失败')
  }
}

// 页面加载时获取用户信息
onMounted(() => {
  fetchUserInfo()
})
</script>
