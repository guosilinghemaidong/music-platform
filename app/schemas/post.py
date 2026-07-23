from pydantic import BaseModel
import datetime

# 动态的返回格式
class PostResponse(BaseModel):
    id: int
    user_id: int
    content: str
    create_time: datetime.datetime
    update_time: datetime.datetime | None = None

    class Config:
        from_attributes = True  # 让 Pydantic 能读取 ORM 对象的属性

# 动态列表的返回格式（带分页信息）
class PostListResponse(BaseModel):
    items: list[PostResponse]  # 动态列表
    total: int                   # 总数量
    page: int                    # 当前页
    page_size: int               # 每页数量


class PostCreate(BaseModel):
    content: str


