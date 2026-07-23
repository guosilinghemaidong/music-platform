from sqlalchemy.orm import Mapped, mapped_column
import datetime
from app.models.base import Base
from sqlalchemy import DateTime, func, Text


# 定义 Post 模型类，对应数据库的 post 表,继承Base
# 表名默认是类名的小写形式，也可以用 __tablename__ 指定
class Post(Base):
    __tablename__ = "post"
    # 每个字段对应数据库表里的一列
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True, comment="动态ID")
    user_id: Mapped[int] = mapped_column(nullable=False, comment="用户ID")
    content: Mapped[str] = mapped_column(Text, nullable=False, comment="动态内容")
    create_time: Mapped[datetime.datetime] = mapped_column(DateTime, server_default=func.now(), comment="发布时间")
    update_time: Mapped[datetime.datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now(), comment="动态更新时间")
