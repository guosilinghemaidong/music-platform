<template>
  <div>
    <h2>关于</h2>
    <el-card style="margin-top: 20px">
      <template #header>
        <span>关于本项目</span>
      </template>
      <p>这是一个基于 <strong>FastAPI + Vue3</strong> 的音乐社交平台学习项目。</p>
      <el-divider />
      <h4>技术栈</h4>
      <p>后端：FastAPI + SQLAlchemy + MySQL + JWT 认证</p>
      <p>前端：Vue3 + Element Plus + Axios + Vue Router</p>
      <el-divider />
      <h4>主要功能</h4>
      <p>音乐浏览与搜索、在线播放、收藏、评论、点赞、关注、动态发布、用户管理、音乐审核。</p>
    </el-card>
  </div>
</template>

<script setup>
// 关于页面，纯静态展示，不需要数据请求
</script>
