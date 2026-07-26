from pydantic import BaseModel


class FollowStatus(BaseModel):
    is_followed: bool

    class Config:
        from_attributes = True


class FollowToggle(BaseModel):
    following_id: int


# ==================== 关注列表相关 ====================

# 关注列表中单个用户的信息
class FollowUserItem(BaseModel):
    id: int                          # 用户ID
    username: str                    # 用户名
    nickname: str | None = None      # 昵称
    avatar: str | None = None        # 头像路径
    is_followed_back: bool           # 对方是否也关注了我（互相关注）


# 关注/粉丝列表的返回格式
class FollowListResponse(BaseModel):
    items: list[FollowUserItem]      # 用户列表
    followers_count: int             # 粉丝总数
    following_count: int             # 关注总数
