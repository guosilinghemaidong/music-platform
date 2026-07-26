/**
 * 全局播放器状态管理（Pinia Store）
 *
 * 作用：让播放器的状态（当前歌曲、是否播放、播放列表等）
 *       可以在多个组件之间共享，比如：
 *       - Discover.vue 点击卡片 → 设置播放歌曲
 *       - PlayerBar.vue 显示播放状态、控制播放/暂停
 *       - MyCollection.vue 点击播放收藏的歌曲
 */
import { defineStore } from 'pinia'
import { ref } from 'vue'

export const usePlayerStore = defineStore('player', () => {

  // ========== 状态（State）==========

  // 当前正在播放的歌曲对象（null 表示没有歌曲在播放）
  const currentMusic = ref(null)

  // 是否正在播放（true = 播放中，false = 暂停）
  const isPlaying = ref(false)

  // 播放列表（存放歌曲对象的数组）
  const playlist = ref([])

  // 当前播放时间（秒）
  const currentTime = ref(0)

  // 歌曲总时长（秒）
  const duration = ref(0)

  // 音量大小（0-100）
  const volume = ref(80)

  // ========== 操作方法（Actions）==========

  /**
   * 播放指定歌曲
   * @param {Object} music - 歌曲对象（需要包含 id, title, file_url 等字段）
   * @param {Array} list - 可选，传入播放列表（不传就用当前列表）
   */
  const playMusic = (music, list = null) => {
    // 如果传入了新的播放列表，就更新它
    if (list) {
      playlist.value = list
    }
    // 设置当前歌曲
    currentMusic.value = music
    // 标记为"需要播放"状态（实际播放由 PlayerBar 监听这个变化来执行）
    isPlaying.value = true
  }

  /**
   * 播放 / 暂停切换
   * 只有在有歌曲的时候才能操作
   */
  const togglePlay = () => {
    if (!currentMusic.value) return
    isPlaying.value = !isPlaying.value
  }

  /**
   * 播放上一首
   * 在当前播放列表里往前找一首，如果已经是第一首就跳到最后一首
   */
  const playPrev = () => {
    if (!currentMusic.value || playlist.value.length === 0) return
    // 找到当前歌曲在列表中的位置
    const idx = playlist.value.findIndex(m => m.id === currentMusic.value.id)
    // 上一首的索引（如果已经是第一首，就跳到列表末尾）
    const prevIdx = idx > 0 ? idx - 1 : playlist.value.length - 1
    playMusic(playlist.value[prevIdx])
  }

  /**
   * 播放下一首
   * 在当前播放列表里往后找一首，如果已经是最后一首就跳到第一首
   */
  const playNext = () => {
    if (!currentMusic.value || playlist.value.length === 0) return
    const idx = playlist.value.findIndex(m => m.id === currentMusic.value.id)
    const nextIdx = idx < playlist.value.length - 1 ? idx + 1 : 0
    playMusic(playlist.value[nextIdx])
  }

  /**
   * 判断某首歌是否正在播放
   * 用于在列表中高亮当前播放的歌曲
   * @param {number} musicId - 歌曲 ID
   * @returns {boolean}
   */
  const isCurrentMusic = (musicId) => {
    return currentMusic.value && currentMusic.value.id === musicId
  }

  // 返回所有状态和方法，供组件使用
  return {
    // 状态
    currentMusic,
    isPlaying,
    playlist,
    currentTime,
    duration,
    volume,
    // 方法
    playMusic,
    togglePlay,
    playPrev,
    playNext,
    isCurrentMusic
  }
})
