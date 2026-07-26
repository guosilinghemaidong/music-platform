<template>
  <div>
    <h2>上架音乐</h2>

    <!-- 添加音乐表单 -->
    <el-form
      ref="formRef"
      :model="form"
      :rules="rules"
      label-width="100px"
      style="max-width: 600px; margin-top: 20px"
    >
      <!-- 歌曲名 -->
      <el-form-item label="歌曲名" prop="title">
        <el-input v-model="form.title" placeholder="请输入歌曲名" />
      </el-form-item>

      <!-- 歌手（下拉选择） -->
      <el-form-item label="歌手" prop="singer_id">
        <el-select v-model="form.singer_id" placeholder="请选择歌手" style="width: 100%">
          <el-option
            v-for="singer in singerList"
            :key="singer.id"
            :label="singer.name"
            :value="singer.id"
          />
        </el-select>
      </el-form-item>

      <!-- 专辑（下拉选择，可选） -->
      <el-form-item label="专辑" prop="album_id">
        <el-select v-model="form.album_id" placeholder="不选则无专辑" clearable style="width: 100%">
          <el-option
            v-for="album in albumList"
            :key="album.id"
            :label="album.name"
            :value="album.id"
          />
        </el-select>
      </el-form-item>

      <!-- 分类（下拉选择，可选） -->
      <el-form-item label="分类" prop="category_id">
        <el-select v-model="form.category_id" placeholder="不选则无分类" clearable style="width: 100%">
          <el-option
            v-for="cat in categoryList"
            :key="cat.id"
            :label="cat.name"
            :value="cat.id"
          />
        </el-select>
      </el-form-item>

      <!-- 音乐文件上传（只支持音频格式） -->
      <el-form-item label="音乐文件" prop="file_url">
        <el-upload
          action=""
          :http-request="uploadMusic"
          :before-upload="beforeMusicUpload"
          :show-file-list="false"
        >
          <!-- 已上传：显示文件名 + 重新上传按钮 -->
          <div v-if="form.file_url" class="upload-success">
            <el-icon><VideoPlay /></el-icon>
            <span class="upload-filename">{{ form.file_url }}</span>
            <el-button type="primary" link style="margin-left: 10px">重新上传</el-button>
          </div>
          <!-- 未上传：显示上传按钮 -->
          <el-button v-else type="primary">
            <el-icon style="margin-right: 5px"><Upload /></el-icon>上传音乐文件
          </el-button>
        </el-upload>
        <div class="upload-tip">支持 mp3、wav、flac、aac、ogg 格式</div>
      </el-form-item>

      <!-- 封面图片上传（只支持图片格式） -->
      <el-form-item label="封面图片">
        <el-upload
          action=""
          :http-request="uploadCover"
          :before-upload="beforeImageUpload"
          :show-file-list="false"
        >
          <!-- 已上传：显示预览图 + 重新上传按钮 -->
          <div v-if="form.cover" class="upload-success">
            <img :src="'http://localhost:8000' + form.cover" class="upload-preview" />
            <el-button type="primary" link style="margin-left: 10px">重新上传</el-button>
          </div>
          <!-- 未上传：显示上传按钮 -->
          <el-button v-else type="primary">
            <el-icon style="margin-right: 5px"><Upload /></el-icon>上传封面图片
          </el-button>
        </el-upload>
        <div class="upload-tip">支持 jpg、png、gif、webp 格式</div>
      </el-form-item>

      <!-- 时长（秒） -->
      <el-form-item label="时长(秒)" prop="duration">
        <el-input-number v-model="form.duration" :min="0" :max="99999" />
      </el-form-item>

      <!-- 歌词文件上传（只支持文本格式） -->
      <el-form-item label="歌词文件">
        <el-upload
          action=""
          :http-request="uploadLyric"
          :before-upload="beforeLyricUpload"
          :show-file-list="false"
        >
          <!-- 已上传：显示文件名 + 重新上传按钮 -->
          <div v-if="form.lyric" class="upload-success">
            <el-icon><Document /></el-icon>
            <span class="upload-filename">{{ form.lyric }}</span>
            <el-button type="primary" link style="margin-left: 10px">重新上传</el-button>
          </div>
          <!-- 未上传：显示上传按钮 -->
          <el-button v-else type="primary">
            <el-icon style="margin-right: 5px"><Upload /></el-icon>上传歌词文件
          </el-button>
        </el-upload>
        <div class="upload-tip">支持 txt、lrc 格式</div>
      </el-form-item>

      <!-- 提交按钮 -->
      <el-form-item>
        <el-button type="primary" @click="handleSubmit" :loading="submitting">提交</el-button>
        <el-button @click="handleReset">重置</el-button>
      </el-form-item>
    </el-form>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import api from '../../api/index.js'
import { ElMessage } from 'element-plus'
import { Upload, VideoPlay, Document } from '@element-plus/icons-vue'

// ========== 表单数据 ==========

// 表单引用（用于调用 validate 和 resetFields）
const formRef = ref(null)
// 提交中状态
const submitting = ref(false)

// 表单字段
const form = ref({
  title: '',
  singer_id: null,
  album_id: null,
  category_id: null,
  file_url: '',
  cover: '',
  duration: null,
  lyric: ''
})

// 表单验证规则
const rules = {
  title: [{ required: true, message: '请输入歌曲名', trigger: 'blur' }],
  singer_id: [{ required: true, message: '请选择歌手', trigger: 'change' }],
  file_url: [{ required: true, message: '请上传音乐文件', trigger: 'change' }]
}

// ========== 下拉列表数据 ==========

const singerList = ref([])    // 歌手列表
const albumList = ref([])     // 专辑列表
const categoryList = ref([])  // 分类列表

// 获取歌手列表
const fetchSingerList = async () => {
  try {
    const res = await api.get('/singer/list', {
      params: { page: 1, page_size: 200 }
    })
    singerList.value = res.data.items
  } catch (error) {
    console.error('获取歌手列表失败', error)
  }
}

// 获取专辑列表
const fetchAlbumList = async () => {
  try {
    const res = await api.get('/album/list', {
      params: { page: 1, page_size: 200 }
    })
    albumList.value = res.data.items
  } catch (error) {
    console.error('获取专辑列表失败', error)
  }
}

// 获取分类列表
const fetchCategoryList = async () => {
  try {
    const res = await api.get('/category/list', {
      params: { page: 1, page_size: 200 }
    })
    categoryList.value = res.data.items
  } catch (error) {
    console.error('获取分类列表失败', error)
  }
}

// ========== 文件上传相关 ==========

// 获取请求头（带上 JWT token，上传接口也需要鉴权）
const getAuthHeaders = () => {
  const token = localStorage.getItem('token')
  return token ? { Authorization: 'Bearer ' + token } : {}
}

// 上传音乐前的校验（检查文件扩展名）
const beforeMusicUpload = (file) => {
  const ext = file.name.split('.').pop().toLowerCase()
  const allowed = ['mp3', 'wav', 'flac', 'aac', 'ogg']
  if (!allowed.includes(ext)) {
    ElMessage.error(`不支持的音频格式：.${ext}`)
    return false
  }
  return true
}

// 上传封面前的校验（检查文件扩展名）
const beforeImageUpload = (file) => {
  const ext = file.name.split('.').pop().toLowerCase()
  const allowed = ['jpg', 'jpeg', 'png', 'gif', 'webp']
  if (!allowed.includes(ext)) {
    ElMessage.error(`不支持的图片格式：.${ext}`)
    return false
  }
  return true
}

// 上传歌词前的校验（检查文件扩展名）
const beforeLyricUpload = (file) => {
  const ext = file.name.split('.').pop().toLowerCase()
  const allowed = ['txt', 'lrc']
  if (!allowed.includes(ext)) {
    ElMessage.error(`不支持的歌词格式：.${ext}`)
    return false
  }
  return true
}

// 自定义上传音乐文件（覆盖 el-upload 默认行为，手动发请求）
const uploadMusic = async (options) => {
  const formData = new FormData()
  formData.append('file', options.file)
  try {
    const res = await api.post('/upload/music', formData, {
      headers: { ...getAuthHeaders(), 'Content-Type': 'multipart/form-data' }
    })
    form.value.file_url = res.data.filename  // 把返回的路径填入表单
    ElMessage.success('音乐上传成功')
  } catch (error) {
    ElMessage.error(error.response?.data?.detail || '音乐上传失败')
  }
}

// 自定义上传封面图片
const uploadCover = async (options) => {
  const formData = new FormData()
  formData.append('file', options.file)
  try {
    const res = await api.post('/upload/image', formData, {
      headers: { ...getAuthHeaders(), 'Content-Type': 'multipart/form-data' }
    })
    form.value.cover = res.data.filename  // 把返回的路径填入表单
    ElMessage.success('封面上传成功')
  } catch (error) {
    ElMessage.error(error.response?.data?.detail || '封面上传失败')
  }
}

// 自定义上传歌词文件
const uploadLyric = async (options) => {
  const formData = new FormData()
  formData.append('file', options.file)
  try {
    const res = await api.post('/upload/lyric', formData, {
      headers: { ...getAuthHeaders(), 'Content-Type': 'multipart/form-data' }
    })
    form.value.lyric = res.data.filename  // 把返回的路径填入表单
    ElMessage.success('歌词上传成功')
  } catch (error) {
    ElMessage.error(error.response?.data?.detail || '歌词上传失败')
  }
}

// ========== 提交 / 重置 ==========

// 提交表单
const handleSubmit = async () => {
  // 先验证表单
  const valid = await formRef.value.validate().catch(() => false)
  if (!valid) return

  submitting.value = true
  try {
    // 构造请求数据（过滤掉空字符串的可选字段，传 null 给后端）
    const data = {
      title: form.value.title,
      singer_id: form.value.singer_id,
      album_id: form.value.album_id || null,
      category_id: form.value.category_id || null,
      file_url: form.value.file_url,
      cover: form.value.cover || null,
      duration: form.value.duration || null,
      lyric: form.value.lyric || null
    }

    await api.post('/admin/music/add', data, {
      headers: getAuthHeaders()
    })

    ElMessage.success('添加成功，已进入待审核状态')
    handleReset()  // 重置表单，方便继续添加
  } catch (error) {
    ElMessage.error(error.response?.data?.detail || '添加失败')
  } finally {
    submitting.value = false
  }
}

// 重置表单（同时清空文件上传状态）
const handleReset = () => {
  formRef.value.resetFields()
  form.value = {
    title: '',
    singer_id: null,
    album_id: null,
    category_id: null,
    file_url: '',
    cover: '',
    duration: null,
    lyric: ''
  }
}

// ========== 生命周期 ==========

onMounted(() => {
  fetchSingerList()
  fetchAlbumList()
  fetchCategoryList()
})
</script>

<style scoped>
/* 上传成功后的展示样式 */
.upload-success {
  display: flex;
  align-items: center;
  gap: 8px;
}

/* 上传成功后的文件名显示 */
.upload-filename {
  color: #67c23a;
  font-size: 13px;
  max-width: 300px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

/* 封面预览图 */
.upload-preview {
  width: 60px;
  height: 60px;
  object-fit: cover;
  border-radius: 4px;
  border: 1px solid #eee;
}

/* 上传按钮下方的格式提示 */
.upload-tip {
  font-size: 12px;
  color: #999;
  margin-top: 4px;
}
</style>
