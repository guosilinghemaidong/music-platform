from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, DateTime, func
import datetime
from app.models.base import Base


# 定义 User 模型类，对应数据库的 user 表,继承Base
# 表名默认是类名的小写形式，也可以用 __tablename__ 指定
class User(Base):
    __tablename__ = "user"
    # 每个字段对应数据库表里的一列
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True, comment="用户ID")
    username: Mapped[str] = mapped_column(String(50), nullable=False, comment="用户名")
    password: Mapped[str] = mapped_column(String(100), nullable=False, comment="密码")
    nickname: Mapped[str] = mapped_column(String(50), nullable=True, comment="昵称")
    avatar: Mapped[str] = mapped_column(String(255), nullable=True, comment="头像路径")
    role: Mapped[str] = mapped_column(String(20), nullable=False, default="user", comment="角色")
    status: Mapped[int] = mapped_column(nullable=False, default=1, comment="状态")
    create_time: Mapped[datetime.datetime] = mapped_column(DateTime, server_default=func.now(), comment="创建时间")
    update_time: Mapped[datetime.datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now(), comment="更新时间")
