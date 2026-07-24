from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database import AsyncSessionLocal
from app.models.music import Music
from app.schemas.music import MusicResponse, MusicListResponse, MusicCreate, MusicUpdate


import json
from app.redis import redis_client

router = APIRouter(prefix="/music", tags=["音乐"])

# 复用 user.py 里的 get_database（获取数据库会话）
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


@router.get("/list", response_model=MusicListResponse)
async def get_music_list(
    page: int = 1,           # 页码，默认第 1 页
    page_size: int = 10,     # 每页数量，默认 10 条
    db: AsyncSession = Depends(get_database)
):
    # 1. 构造缓存 Key
    cache_key = f"music:list:page={page}:page_size={page_size}"

    # 2. 尝试从 Redis 获取缓存
    cached_data = redis_client.get(cache_key)
    if cached_data:
        # 有缓存，直接返回
        return json.loads(cached_data)
    # 1. 计算跳过多少条
    offset = (page - 1) * page_size

    # 2. 查询总数（SELECT COUNT(*) FROM music）
    total_result = await db.execute(select(Music))
    total = len(total_result.scalars().all())

    # 3. 查询当前页数据（SELECT * FROM music LIMIT page_size OFFSET offset）
    result = await db.execute(
        select(Music)
        .offset(offset)
        .limit(page_size)
    )
    items = [
        {
            "id": m.id,
            "title": m.title,
            "singer_id": m.singer_id,
            "album_id": m.album_id,
            "category_id": m.category_id,
            "file_url": m.file_url,
            "cover": m.cover,
            "duration": m.duration,
            "play_count": m.play_count,
            "status": m.status
        }
        for m in result.scalars().all()
    ]
    # 4. 把结果存入 Redis，设置 60 秒过期
    result_dict = {
        "items": items,
        "total": total,
        "page": page,
        "page_size": page_size
    }
    redis_client.setex(cache_key, 60, json.dumps(result_dict))

    return result_dict

@router.get("/detail/{music_id}", response_model=MusicResponse)
async def get_music_detail(music_id: int, db: AsyncSession = Depends(get_database)):
    # 根据 ID 查询音乐
    result = await db.execute(select(Music).where(Music.id == music_id))
    music = result.scalar_one_or_none()
    if music is None:
        raise HTTPException(status_code=404, detail="音乐未找到")
    return music


@router.post("/create", response_model=MusicResponse)
async def create_music(music_data: MusicCreate, db: AsyncSession = Depends(get_database)):
    # 1. 检查是否已存在
    result = await db.execute(select(Music).where(Music.title == music_data.title))
    music = result.scalar_one_or_none()
    if music is not None:
        raise HTTPException(status_code=400, detail="音乐已存在")

    # 2. 创建新音乐
    new_music = Music(**music_data.model_dump())
    db.add(new_music)
    await db.flush()
    return new_music


@router.put("/update/{music_id}", response_model=MusicResponse)
async def update_music(music_id: int, music_data: MusicUpdate, db: AsyncSession = Depends(get_database)):
    # 1. 检查音乐是否存在
    result = await db.execute(select(Music).where(Music.id == music_id))
    music = result.scalar_one_or_none()
    if music is None:
        raise HTTPException(status_code=404, detail="音乐未找到")
    # 2. 更新音乐信息
    for key, value in music_data.model_dump().items():
        setattr(music, key, value)

    await db.flush()
    return music

@router.delete("/delete/{music_id}")
async def delete_music(music_id: int, db: AsyncSession = Depends(get_database)):
    # 1. 检查音乐是否存在
    result = await db.execute(select(Music).where(Music.id == music_id))
    music = result.scalar_one_or_none()
    if music is None:
        raise HTTPException(status_code=404, detail="音乐未找到")
    # 2. 删除音乐
    await db.delete(music)
    await db.flush()
    return {"message": "删除成功"}
