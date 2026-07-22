from sqlalchemy.orm import Mapped, mapped_column
import datetime
from app.models.base import Base
from sqlalchemy import Text, DateTime, func


class Comment(Base):
    __tablename__ = "comment"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True, comment="评论ID")
    user_id: Mapped[int] = mapped_column(comment="用户ID")
    music_id: Mapped[int] = mapped_column(comment="音乐ID")
    content: Mapped[str] = mapped_column(Text, nullable=False, comment="评论内容")
    create_time: Mapped[datetime.datetime] = mapped_column(DateTime, server_default=func.now(), comment="评论时间")
    update_time: Mapped[datetime.datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now(),comment="更新时间")
