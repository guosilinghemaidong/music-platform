from sqlalchemy.orm import Mapped, mapped_column
import datetime
from app.models.base import Base
from sqlalchemy import String, DateTime, func, Text



# 定义 Music 模型类，对应数据库的 music 表,继承Base
# 表名默认是类名的小写形式，也可以用 __tablename__ 指定
class Music(Base):
    __tablename__ = "music"
    # 每个字段对应数据库表里的一列
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True, comment="音乐ID")
    title: Mapped[str] = mapped_column(String(100), nullable=False, comment="歌曲名")
    singer_id: Mapped[int] = mapped_column(nullable=False, comment="歌手ID")
    album_id: Mapped[int] = mapped_column(nullable=True, comment="专辑ID")
    category_id: Mapped[int] = mapped_column(nullable=True, comment="分类ID")
    file_url: Mapped[str] = mapped_column(String(255), nullable=False, comment="音乐文件路径")
    cover: Mapped[str] = mapped_column(String(255), nullable=True, comment="音乐封面")
    duration: Mapped[int] = mapped_column(nullable=True, comment="时长(秒)")
    lyric: Mapped[str] = mapped_column(Text, nullable=True, comment="歌词")
    play_count: Mapped[int] = mapped_column(default=0, comment="播放次数")
    status: Mapped[int] = mapped_column(default=1, comment="状态（1上架 0下架）")
    create_time: Mapped[datetime.datetime] = mapped_column(DateTime, server_default=func.now(), comment="创建时间")
    update_time: Mapped[datetime.datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now(), comment="更新时间")
