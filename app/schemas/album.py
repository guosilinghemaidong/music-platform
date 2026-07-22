from pydantic import BaseModel
import datetime


# 专辑的返回格式
class AlbumResponse(BaseModel):
    id: int
    name: str
    singer_id: int
    cover: str | None = None
    release_date: datetime.date | None = None

    class Config:
        from_attributes = True  # 让 Pydantic 能读取 ORM 对象的属性


# 专辑的返回格式（带分页信息）
class AlbumListResponse(BaseModel):
    items: list[AlbumResponse]  # 专辑列表
    total: int                  # 总数量
    page: int                   # 当前页
    page_size: int              # 每页数量


# 新增专辑
class AlbumCreate(BaseModel):
    name: str
    singer_id: int
    cover: str | None = None
    release_date: datetime.date | None = None


# 修改专辑
class AlbumUpdate(BaseModel):
    name: str | None = None
    singer_id: int | None = None
    cover: str | None = None
    release_date: datetime.date | None = None