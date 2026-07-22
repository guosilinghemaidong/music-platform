from sqlalchemy.orm import Mapped, mapped_column
import datetime
from app.models.base import Base
from sqlalchemy import DateTime, func


class Follow(Base):
    __tablename__ = "follow"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True, comment="关注ID")
    follower_id: Mapped[int] = mapped_column(comment="粉丝ID")
    following_id: Mapped[int] = mapped_column(comment="被关注用户ID")
    create_time: Mapped[datetime.datetime] = mapped_column(DateTime, server_default=func.now(), comment="关注时间")