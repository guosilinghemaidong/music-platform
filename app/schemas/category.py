from pydantic import BaseModel


# 分类的返回格式
class CategoryResponse(BaseModel):
    id: int
    name: str

    class Config:
        from_attributes = True  # 让 Pydantic 能读取 ORM 对象的属性


# 分类的返回格式（带分页信息）
class CategoryListResponse(BaseModel):
    items: list[CategoryResponse]  # 分类列表
    total: int                     # 总数量
    page: int                      # 当前页
    page_size: int                 # 每页数量


# 新增分类
class CategoryCreate(BaseModel):
    name: str


# 修改分类
class CategoryUpdate(BaseModel):
    name: str | None = None