from pydantic import BaseModel
import datetime


class CollectionStatus(BaseModel):
    is_collected: bool

    class Config:
        from_attributes = True


class CollectionToggle(BaseModel):
    music_id: int


# 收藏列表中的单条数据（音乐信息 + 收藏时间）
class CollectionMusicItem(BaseModel):
    id: int                      # 音乐 ID
    title: str                   # 歌名
    singer_id: int               # 歌手 ID
    album_id: int | None = None  # 专辑 ID
    category_id: int | None = None  # 分类 ID
    file_url: str                # 音乐文件路径
    cover: str | None = None     # 封面
    duration: int | None = None  # 时长（秒）
    play_count: int              # 播放次数
    status: int                  # 状态（1上架 0下架）
    collected_at: datetime.datetime | None = None  # 收藏时间

    class Config:
        from_attributes = True


# 收藏列表（带分页）
class CollectionListResponse(BaseModel):
    items: list[CollectionMusicItem]  # 收藏的音乐列表
    total: int                        # 总数量
    page: int                         # 当前页
    page_size: int                    # 每页数量

