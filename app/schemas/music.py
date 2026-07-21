from pydantic import BaseModel
import datetime

# 单首音乐的返回格式
class MusicResponse(BaseModel):
    id: int
    title: str
    singer_id: int
    album_id: int | None = None
    category_id: int | None = None
    file_url: str
    cover: str | None = None
    duration: int | None = None
    lyric: str | None = None
    play_count: int
    status: int

    class Config:
        from_attributes = True  # 让 Pydantic 能读取 ORM 对象的属性

# 音乐列表的返回格式（带分页信息）
class MusicListResponse(BaseModel):
    items: list[MusicResponse]  # 音乐列表
    total: int                   # 总数量
    page: int                    # 当前页
    page_size: int               # 每页数量


class MusicCreate(BaseModel):
    title: str
    singer_id: int
    album_id: int | None = None
    category_id: int | None = None
    file_url: str
    cover: str | None = None
    duration: int | None = None
    lyric: str | None = None


class MusicUpdate(BaseModel):
    title: str | None = None
    singer_id: int | None = None
    album_id: int | None = None
    category_id: int | None = None
    file_url: str | None = None
    cover: str | None = None
    duration: int | None = None
    lyric: str | None = None

