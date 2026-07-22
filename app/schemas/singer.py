from pydantic import BaseModel
import datetime

# 歌手的返回格式
class SingerResponse(BaseModel):
    id: int
    name: str
    avatar: str | None = None
    gender: int | None = None
    introduction: str | None = None

    class Config:
        from_attributes = True  # 让 Pydantic 能读取 ORM 对象的属性

# 歌手的返回格式（带分页信息）
class SingerListResponse(BaseModel):
    items: list[SingerResponse]  # 歌手列表
    total: int                   # 总数量
    page: int                    # 当前页
    page_size: int               # 每页数量


class SingerCreate(BaseModel):
    name: str
    avatar: str | None = None
    gender: int | None = None
    introduction: str | None = None


class SingerUpdate(BaseModel):
    name: str | None = None
    avatar: str | None = None
    gender: int | None = None
    introduction: str | None = None


