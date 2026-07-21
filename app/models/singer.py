from sqlalchemy.orm import Mapped, mapped_column
import datetime
from app.models.base import Base
from sqlalchemy import String, DateTime, func, Text


# 定义 Singer 模型类，对应数据库的 singer 表,继承Base
# 表名默认是类名的小写形式，也可以用 __tablename__ 指定
class Singer(Base):
    __tablename__ = "singer"
    # 每个字段对应数据库表里的一列
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True, comment="歌手ID")
    name: Mapped[str] = mapped_column(String(100), nullable=False, comment="歌手名")
    gender: Mapped[int] = mapped_column(default=0, comment="性别（0未知 1男 2女）")
    avatar: Mapped[str] = mapped_column(String(255), nullable=True, comment="头像路径")
    introduction: Mapped[str] = mapped_column(Text, nullable=True, comment="歌手简介")
    create_time: Mapped[datetime.datetime] = mapped_column(DateTime, server_default=func.now(), comment="创建时间")
    update_time: Mapped[datetime.datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now(), comment="更新时间")
