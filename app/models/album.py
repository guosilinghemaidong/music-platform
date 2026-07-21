from sqlalchemy.orm import Mapped, mapped_column
import datetime
from app.models.base import Base
from sqlalchemy import String, DateTime, func, Text,Date



# 定义 Album 模型类，对应数据库的 album 表,继承Base
# 表名默认是类名的小写形式，也可以用 __tablename__ 指定
class Album(Base):
    __tablename__ = "album"
    # 每个字段对应数据库表里的一列
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True, comment="专辑ID")
    name: Mapped[str] = mapped_column(String(100), nullable=False, comment="专辑名")
    singer_id: Mapped[int] = mapped_column(nullable=False, comment="歌手ID")
    cover: Mapped[str] = mapped_column(String(255), nullable=True, comment="专辑封面")
    release_date: Mapped[datetime.date] = mapped_column(Date, nullable=True, comment="发行日期")
    create_time: Mapped[datetime.datetime] = mapped_column(DateTime, server_default=func.now(), comment="创建时间")
    update_time: Mapped[datetime.datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now(), comment="更新时间")
