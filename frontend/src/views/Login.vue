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

// 表单数据
const form = reactive({
  username: '',
  password: ''
})

// 登录按钮点击事件
const handleLogin = () => {
  console.log('登录信息：', form.username, form.password)
  // 后面这里会调用后端接口
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
