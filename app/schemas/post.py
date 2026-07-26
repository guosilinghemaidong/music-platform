from pydantic import BaseModel
import datetime


# ==================== 动态相关 ====================

# 发布动态的请求参数
class PostCreate(BaseModel):
    content: str                              # 动态文字内容（必填）
    images: str | None = None                 # 图片路径（JSON数组字符串，可选）
    music_id: int | None = None               # 转发的音乐ID（可选）


# 单条动态的返回格式
class PostResponse(BaseModel):
    id: int
    user_id: int
    content: str
    images: str | None = None
    music_id: int | None = None
    status: int
    like_count: int
    comment_count: int
    create_time: datetime.datetime
    update_time: datetime.datetime | None = None

    # 以下为关联查询后手动填充的字段
    username: str | None = None               # 发布者昵称/用户名
    avatar: str | None = None                 # 发布者头像
    is_liked: bool = False                    # 当前用户是否已点赞

    class Config:
        from_attributes = True


# 动态列表的返回格式（带分页信息）
class PostListResponse(BaseModel):
    items: list[PostResponse]
    total: int
    page: int
    page_size: int


# ==================== 动态点赞相关 ====================

# 切换点赞的请求参数
class PostLikeToggle(BaseModel):
    post_id: int


# 点赞状态返回
class PostLikeStatus(BaseModel):
    is_liked: bool
    like_count: int


# ==================== 动态评论相关 ====================

# 发表评论的请求参数
class PostCommentCreate(BaseModel):
    post_id: int
    content: str


# 单条评论的返回格式
class PostCommentResponse(BaseModel):
    id: int
    user_id: int
    post_id: int
    content: str
    username: str | None = None               # 评论者昵称/用户名
    avatar: str | None = None                 # 评论者头像
    create_time: datetime.datetime | None = None

    class Config:
        from_attributes = True
