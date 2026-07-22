from sqlalchemy.orm import Mapped, mapped_column
import datetime
from app.models.base import Base
from sqlalchemy import String, DateTime, func


class Category(Base):
    __tablename__ = "category"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True, comment="分类ID")
    name: Mapped[str] = mapped_column(String(50), nullable=False, comment="分类名称")
    create_time: Mapped[datetime.datetime] = mapped_column(DateTime, server_default=func.now(), comment="创建时间")