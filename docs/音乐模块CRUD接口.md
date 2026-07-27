C:\Users\41434\Desktop\FastAPI_base\docs\Day6-音乐模块CRUD接口.md
# Day 6 代码逐行分析

## 今日任务

| 任务 | 状态 |
|------|------|
| Navicat 建表：collection、comment、music_like、follow、post | ✅ |
| ORM 模型：models/singer.py、models/album.py、models/music.py | ✅ |
| 音乐 CRUD 接口：routers/music.py | ✅ |
| 分页查询 | ✅ |

---

## 文件 1：app/models/singer.py

from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, DateTime, func
import datetime
from app.models.base import Base

class Singer(Base):
    __tablename__ = "singer"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True, comment="歌手ID")
    name: Mapped[str] = mapped_column(String(100), nullable=False, comment="歌手名")
    gender: Mapped[int] = mapped_column(default=0, comment="性别（0未知 1男 2女）")
    avatar: Mapped[str] = mapped_column(String(255), nullable=True, comment="头像路径")
    introduction: Mapped[str] = mapped_column(Text, nullable=True, comment="歌手简介")
    create_time: Mapped[datetime.datetime] = mapped_column(DateTime, server_default=func.now(), comment="创建时间")
    update_time: Mapped[datetime.datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now(), comment="更新时间")

### 要点

| 字段 | 类型 | 说明 |
|------|------|------|
| `gender` | `Mapped[int]` | Python 用 int，数据库是 TINYINT |
| `introduction` | `Text` | 数据库是 TEXT 类型，需要导入 `Text` |

---

## 文件 2：app/models/album.py

from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, DateTime, func, Date
import datetime
from app.models.base import Base

class Album(Base):
    __tablename__ = "album"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True, comment="专辑ID")
    name: Mapped[str] = mapped_column(String(100), nullable=False, comment="专辑名")
    singer_id: Mapped[int] = mapped_column(nullable=False, comment="歌手ID")
    cover: Mapped[str] = mapped_column(String(255), nullable=True, comment="专辑封面")
    release_date: Mapped[datetime.date] = mapped_column(Date, nullable=True, comment="发行日期")
    create_time: Mapped[datetime.datetime] = mapped_column(DateTime, server_default=func.now(), comment="创建时间")
    update_time: Mapped[datetime.datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now(), comment="更新时间")

### 要点

| 字段 | 类型 | 说明 |
|------|------|------|
| `release_date` | `Mapped[datetime.date]` | 数据库是 DATE 类型，Python 用 `datetime.date` |

---

## 文件 3：app/models/music.py

from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, DateTime, func, Text
import datetime
from app.models.base import Base

class Music(Base):
    __tablename__ = "music"
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

### 要点

| 字段 | 类型 | 说明 |
|------|------|------|
| `lyric` | `Text` | 歌词可能很长，用 TEXT 类型 |
| `play_count` | `default=0` | 新歌曲默认 0 次播放 |
| `status` | `default=1` | 默认上架状态 |

---

## 文件 4：app/schemas/music.py

from pydantic import BaseModel
import datetime

class MusicResponse(BaseModel):
    id: int
    title: str
    singer_id: int
    album_id: int | None = None
    category_id: int | None = None
    file_url: str
    cover: str | None = None
    duration: int | None = None
    lyric: str | None = None
    play_count: int
    status: int

    class Config:
        from_attributes = True

class MusicListResponse(BaseModel):
    items: list[MusicResponse]
    total: int
    page: int
    page_size: int

class MusicCreate(BaseModel):
    title: str
    singer_id: int
    album_id: int | None = None
    category_id: int | None = None
    file_url: str
    cover: str | None = None
    duration: int | None = None
    lyric: str | None = None

class MusicUpdate(BaseModel):
    title: str | None = None
    singer_id: int | None = None
    album_id: int | None = None
    category_id: int | None = None
    file_url: str | None = None
    cover: str | None = None
    duration: int | None = None
    lyric: str | None = None

### 四个类的作用

| 类 | 用途 | 特点 |
|---|------|------|
| `MusicResponse` | 返回给前端 | 包含所有字段，`from_attributes = True` |
| `MusicListResponse` | 分页列表 | 包含列表 + 分页信息 |
| `MusicCreate` | 创建音乐 | 不需要 id、play_count、时间等 |
| `MusicUpdate` | 修改音乐 | 所有字段可选（`str \| None = None`） |

> 💡 **Pydantic v2 注意：** 可空字段必须用 `str | None = None`，不能用旧的 `str = None`。

---

## 文件 5：app/routers/music.py

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import AsyncSessionLocal
from app.models.music import Music
from app.schemas.music import MusicResponse, MusicListResponse, MusicCreate, MusicUpdate

router = APIRouter(prefix="/music", tags=["音乐"])

async def get_database():
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()

### 接口 1：获取音乐列表（带分页）

@router.get("/list", response_model=MusicListResponse)
async def get_music_list(
    page: int = 1,
    page_size: int = 10,
    db: AsyncSession = Depends(get_database)
):
    offset = (page - 1) * page_size
    total_result = await db.execute(select(Music))
    total = len(total_result.scalars().all())
    result = await db.execute(
        select(Music).offset(offset).limit(page_size)
    )
    items = result.scalars().all()
    return {
        "items": items,
        "total": total,
        "page": page,
        "page_size": page_size
    }

### 分页原理

| 页码 | offset | limit | 取第几条 |
|------|--------|-------|---------|
| 第 1 页 | 0 | 10 | 1-10 |
| 第 2 页 | 10 | 10 | 11-20 |
| 第 3 页 | 20 | 10 | 21-30 |

> 💡 **公式：** `offset = (page - 1) * page_size`

---

### 接口 2：获取音乐详情

@router.get("/detail/{music_id}", response_model=MusicResponse)
async def get_music_detail(music_id: int, db: AsyncSession = Depends(get_database)):
    result = await db.execute(select(Music).where(Music.id == music_id))
    music = result.scalar_one_or_none()
    if music is None:
        raise HTTPException(status_code=404, detail="音乐未找到")
    return music

---

### 接口 3：新增音乐

@router.post("/create", response_model=MusicResponse)
async def create_music(music_data: MusicCreate, db: AsyncSession = Depends(get_database)):
    result = await db.execute(select(Music).where(Music.title == music_data.title))
    existing = result.scalar_one_or_none()
    if existing is not None:
        raise HTTPException(status_code=400, detail="音乐已存在")
    new_music = Music(**music_data.model_dump())
    db.add(new_music)
    await db.flush()
    return new_music

### 要点

| 代码 | 含义 |
|------|------|
| `music_data.model_dump()` | 把 Pydantic 模型转成字典 |
| `Music(**字典)` | 用字典创建 ORM 对象 |
| `db.add(new_music)` | 标记为"待插入" |
| `await db.flush()` | 发送到数据库 |

---

### 接口 4：修改音乐

@router.put("/update/{music_id}", response_model=MusicResponse)
async def update_music(music_id: int, music_data: MusicUpdate, db: AsyncSession = Depends(get_database)):
    result = await db.execute(select(Music).where(Music.id == music_id))
    music = result.scalar_one_or_none()
    if music is None:
        raise HTTPException(status_code=404, detail="音乐未找到")
    for key, value in music_data.model_dump().items():
        setattr(music, key, value)
    await db.flush()
    return music

### setattr 解释
普通写法
music.title = "新歌名" music.cover = "新封面"
setattr 写法（动态设置）
setattr(music, "title", "新歌名") setattr(music, "cover", "新封面")
循环遍历字典
for key, value in music_data.model_dump().items(): setattr(music, key, value)

> 💡 **好处：** 不管前端传了几个字段，都能自动处理。

---

### 接口 5：删除音乐

@router.delete("/delete/{music_id}")
async def delete_music(music_id: int, db: AsyncSession = Depends(get_database)):
    result = await db.execute(select(Music).where(Music.id == music_id))
    music = result.scalar_one_or_none()
    if music is None:
        raise HTTPException(status_code=404, detail="音乐未找到")
    await db.delete(music)
    await db.flush()
    return {"message": "删除成功"}

### 要点

| 代码 | 含义 |
|------|------|
| `await db.delete(music)` | 标记为"待删除" |
| `await db.flush()` | 发送到数据库 |
| `return {"message": "删除成功"}` | 不加 `response_model`，直接返回字典 |

---

## Day 6 总结

### 新增的 5 个表

| 表名 | 作用 |
|------|------|
| `collection` | 收藏（用户 + 音乐） |
| `comment` | 评论（用户 + 音乐 + 内容） |
| `music_like` | 点赞（用户 + 音乐） |
| `follow` | 关注（粉丝 + 被关注用户） |
| `post` | 动态（用户 + 内容） |

### 新增的 3 个 ORM 模型

| 文件 | 对应表 |
|------|--------|
| `models/singer.py` | singer |
| `models/album.py` | album |
| `models/music.py` | music |

### 新增的 5 个接口

| 接口 | 方法 | 路径 | 功能 |
|------|------|------|------|
| 列表 | GET | `/music/list` | 分页获取所有音乐 |
| 详情 | GET | `/music/detail/{id}` | 获取单首音乐 |
| 新增 | POST | `/music/create` | 添加新音乐 |
| 修改 | PUT | `/music/update/{id}` | 修改音乐信息 |
| 删除 | DELETE | `/music/delete/{id}` | 删除音乐 |

**Day 6 的本质：** 完成音乐模块的完整 CRUD，掌握分页查询、动态更新（setattr）、删除操作。

