from pydantic import BaseModel
import datetime


# ==================== 用户管理相关 ====================

# 管理员查看用户列表时，单个用户的返回格式
# 比普通 UserResponse 多了 status 字段，管理员需要看到用户的启用/禁用状态
class AdminUserResponse(BaseModel):
    id: int              # 用户ID
    username: str        # 用户名
    nickname: str | None = None # 昵称
    role: str            # 角色（user/admin）
    status: int          # 状态（1正常 0禁用）

    class Config:
        from_attributes = True  # 让 Pydantic 能读取 ORM 对象的属性


# 用户列表的返回格式（带分页信息）
class AdminUserListResponse(BaseModel):
    items: list[AdminUserResponse]  # 用户列表
    total: int                       # 总数量
    page: int                        # 当前页
    page_size: int                   # 每页数量


# 管理员修改用户状态时，前端传的参数
class UserStatusUpdate(BaseModel):
    status: int  # 目标状态：1 启用，0 禁用


# 修改用户状态后的返回格式
class UserStatusResponse(BaseModel):
    id: int       # 用户ID
    username: str # 用户名
    status: int   # 修改后的状态

    class Config:
        from_attributes = True


# ==================== 音乐审核相关 ====================

# 管理员审核音乐列表时，单首音乐的返回格式
# 包含 status 字段，管理员需要看到上架/下架状态
class AdminMusicResponse(BaseModel):
    id: int                        # 音乐ID
    title: str                     # 歌曲名
    singer_id: int                 # 歌手ID
    album_id: int | None = None    # 专辑ID
    category_id: int | None = None # 分类ID
    file_url: str                  # 音乐文件路径
    cover: str | None = None       # 歌曲封面
    duration: int | None = None    # 时长（秒）
    play_count: int                # 播放次数
    status: int                    # 状态（1上架 0下架）

    class Config:
        from_attributes = True


# 待审核音乐列表的返回格式（带分页信息）
class AdminMusicListResponse(BaseModel):
    items: list[AdminMusicResponse]  # 音乐列表
    total: int                        # 总数量
    page: int                         # 当前页
    page_size: int                    # 每页数量


# 管理员审核音乐时，前端传的参数
class MusicAuditUpdate(BaseModel):
    status: int  # 目标状态：1 上架，0 下架


# 审核音乐后的返回格式
class MusicAuditResponse(BaseModel):
    id: int      # 音乐ID
    title: str   # 歌曲名
    status: int  # 审核后的状态

    class Config:
        from_attributes = True


# ==================== 动态管理相关 ====================

# 管理员查看动态列表时，单条动态的返回格式
class AdminPostResponse(BaseModel):
    id: int
    user_id: int
    content: str
    images: str | None = None
    music_id: int | None = None
    status: int
    like_count: int
    comment_count: int
    create_time: datetime.datetime
    # 以下字段手动填充
    username: str | None = None

    class Config:
        from_attributes = True


# 管理员动态列表（带分页）
class AdminPostListResponse(BaseModel):
    items: list[AdminPostResponse]
    total: int
    page: int
    page_size: int


# 管理员审核动态的请求参数
class PostAuditUpdate(BaseModel):
    status: int  # 1=通过，2=拒绝


# 管理员审核动态后的返回格式
class PostAuditResponse(BaseModel):
    id: int
    content: str
    status: int

    class Config:
        from_attributes = True
