from sqlalchemy.orm import Mapped, mapped_column
import datetime
from app.models.base import Base
from sqlalchemy import DateTime, func


class MusicLike(Base):
    __tablename__ = "music_like"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True, comment="点赞ID")
    user_id: Mapped[int] = mapped_column(comment="用户ID")
    music_id: Mapped[int] = mapped_column(comment="音乐ID")
    create_time: Mapped[datetime.datetime] = mapped_column(DateTime, server_default=func.now(), comment="点赞时间")
