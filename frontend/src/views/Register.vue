<template>
  <div class="register-container">
    <h2>注册</h2>
    <el-form :model="form">
      <el-form-item label="用户名">
        <el-input v-model="form.username" placeholder="请输入用户名" />
      </el-form-item>
      <el-form-item label="密码">
        <el-input v-model="form.password" type="password" placeholder="请输入密码" />
      </el-form-item>
      <el-form-item label="昵称">
        <el-input v-model="form.nickname" placeholder="请输入昵称（可选）" />
      </el-form-item>
      <el-form-item>
        <el-button type="primary" @click="handleRegister">注册</el-button>
        <el-button @click="$router.push('/login')">去登录</el-button>
      </el-form-item>
    </el-form>
  </div>
</template>

<script setup>
import { reactive } from 'vue'
import { useRouter } from 'vue-router'
import api from '../api/index.js'
import { ElMessage } from 'element-plus'

const router = useRouter()

const form = reactive({
  username: '',
  password: '',
  nickname: ''
})

const handleRegister = async () => {
  try {
    // 调用后端注册接口
    const res = await api.post('/user/register', {
      username: form.username,
      password: form.password,
      nickname: form.nickname
    })
    ElMessage.success('注册成功！')
    console.log('注册结果：', res.data)
    // 跳转到登录页
    router.push('/login')
  } catch (error) {
    // 注册失败（比如用户名已存在）
    ElMessage.error(error.response?.data?.detail || '注册失败')
  }
}

</script>

<style scoped>
.register-container {
  width: 400px;
  margin: 100px auto;
  padding: 30px;
  border: 1px solid #eee;
  border-radius: 8px;
}
</style>
