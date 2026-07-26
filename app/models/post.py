from sqlalchemy.orm import Mapped, mapped_column
import datetime
from app.models.base import Base
from sqlalchemy import DateTime, func, Text, INT


# 定义 Post 模型类，对应数据库的 post 表,继承Base
class Post(Base):
    __tablename__ = "post"
    # 每个字段对应数据库表里的一列
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True, comment="动态ID")
    user_id: Mapped[int] = mapped_column(nullable=False, comment="用户ID")
    content: Mapped[str] = mapped_column(Text, nullable=False, comment="动态内容")
    images: Mapped[str] = mapped_column(Text, nullable=True, comment="图片路径（JSON数组）")
    music_id: Mapped[int] = mapped_column(nullable=True, comment="转发的音乐ID")
    status: Mapped[int] = mapped_column(nullable=False, default=0, comment="审核状态（0=待审核，1=已通过，2=已拒绝）")
    like_count: Mapped[int] = mapped_column(nullable=False, default=0, comment="点赞数")
    comment_count: Mapped[int] = mapped_column(nullable=False, default=0, comment="评论数")
    create_time: Mapped[datetime.datetime] = mapped_column(DateTime, server_default=func.now(), comment="发布时间")
    update_time: Mapped[datetime.datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now(), comment="更新时间")
