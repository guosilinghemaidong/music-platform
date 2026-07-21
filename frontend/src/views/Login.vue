<template>
  <div class="login-container">
    <h2>登录</h2>
    <el-form :model="form">
      <el-form-item label="用户名">
        <el-input v-model="form.username" placeholder="请输入用户名" />
      </el-form-item>
      <el-form-item label="密码">
        <el-input v-model="form.password" type="password" placeholder="请输入密码" />
      </el-form-item>
      <el-form-item>
        <el-button type="primary" @click="handleLogin">登录</el-button>
        <el-button @click="$router.push('/register')">去注册</el-button>
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

// 表单数据
const form = reactive({
  username: '',
  password: ''
})

// 登录按钮点击事件
const handleLogin = async () => {
  try {
    // 1. 调用登录接口，获取 Token
    const res = await api.post('/user/login', {
      username: form.username,
      password: form.password
    })

    // 2. 保存 Token
    localStorage.setItem('token', res.data.access_token)

    // 3. 获取用户信息（调用 /user/me 接口）
    const userRes = await api.get('/user/me', {
      headers: { Authorization: 'Bearer ' + res.data.access_token }
    })

    // 4. 保存用户信息
    localStorage.setItem('username', userRes.data.username)
    localStorage.setItem('role', userRes.data.role)

    ElMessage.success('登录成功！')

    // 5. 根据角色跳转不同页面
    if (userRes.data.role === 'admin') {
      router.push('/admin')
    } else {
      router.push('/home')
    }
  } catch (error) {
    ElMessage.error(error.response?.data?.detail || '登录失败')
  }
}


</script>

<style scoped>
.login-container {
  width: 400px;
  margin: 100px auto;
  padding: 30px;
  border: 1px solid #eee;
  border-radius: 8px;
}
</style>
