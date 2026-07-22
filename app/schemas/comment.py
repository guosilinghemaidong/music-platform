from pydantic import BaseModel
import datetime




# 返回评论
class CommentResponse(BaseModel):
    id: int
    user_id: int
    username: str      # 手动查询后填充
    content: str
    music_id: int
    create_time: datetime.datetime | None = None

    class Config:
        from_attributes = True  # 这个其实用不上了，因为我们手动组装 dict




# 发表评论
class CommentCreate(BaseModel):
    content: str       # 评论内容
    music_id: int      # 评论哪首歌
    # user_id 不需要，从 Token 获取



