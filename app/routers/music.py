from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database import AsyncSessionLocal
from app.models.music import Music
from app.models.play_history import PlayHistory
from app.models.user import User
from app.schemas.music import MusicResponse, MusicListResponse, MusicCreate, MusicUpdate


import json
from app.redis import redis_client

# JWT 相关（用于可选的用户认证）
from jose import jwt, JWTError
from app.config import SECRET_KEY, ALGORITHM
from app.routers.user import get_current_user

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


# 可选的用户认证：有 Token 就返回用户，没有就返回 None（不报错）
async def get_optional_user(
    authorization: str = Header(None),
    db: AsyncSession = Depends(get_database)
):
    if not authorization or not authorization.startswith("Bearer "):
        return None
    token = authorization.split(" ")[1]
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        if not username:
            return None
        result = await db.execute(select(User).where(User.username == username))
        return result.scalar_one_or_none()
    except JWTError:
        return None


@router.get("/list", response_model=MusicListResponse)
async def get_music_list(
    page: int = 1,           # 页码，默认第 1 页
    page_size: int = 10,     # 每页数量，默认 10 条
    keyword: str = None,     # 搜索关键词（按歌名模糊匹配）
    category_id: int = None, # 按分类 ID 筛选
    singer_id: int = None,   # 按歌手 ID 筛选
    db: AsyncSession = Depends(get_database)
):
    # 1. 构造缓存 Key（把搜索/筛选条件也带上，避免不同搜索结果混用缓存）
    cache_key = f"music:list:page={page}:page_size={page_size}:keyword={keyword}:category_id={category_id}:singer_id={singer_id}"

    # 2. 尝试从 Redis 获取缓存
    cached_data = redis_client.get(cache_key)
    if cached_data:
        # 有缓存，直接返回
        return json.loads(cached_data)

    # 3. 计算跳过多少条
    offset = (page - 1) * page_size

    # 4. 构造基础查询条件（只查已上架的音乐，status=1）
    query = select(Music).where(Music.status == 1)

    # 5. 如果有搜索关键词，按歌名模糊匹配（LIKE '%keyword%'）
    if keyword:
        query = query.where(Music.title.contains(keyword))

    # 6. 如果指定了分类 ID，加上分类筛选
    if category_id is not None:
        query = query.where(Music.category_id == category_id)

    # 7. 如果指定了歌手 ID，加上歌手筛选
    if singer_id is not None:
        query = query.where(Music.singer_id == singer_id)

    # 8. 查询总数（SELECT COUNT(*) FROM music WHERE ...）
    total_result = await db.execute(query)
    total = len(total_result.scalars().all())

    # 9. 查询当前页数据（SELECT * FROM music WHERE ... LIMIT page_size OFFSET offset）
    result = await db.execute(
        query
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

    # 10. 把结果存入 Redis，设置 60 秒过期
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
    # 1. 根据 ID 查询音乐
    result = await db.execute(select(Music).where(Music.id == music_id))
    music = result.scalar_one_or_none()

    # 2. 音乐不存在
    if music is None:
        raise HTTPException(status_code=404, detail="音乐未找到")

    # 3. 检查音乐是否已下架（status != 1 表示未上架，用户不能访问）
    if music.status != 1:
        raise HTTPException(status_code=403, detail="该音乐已下架")

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


# ==================== 获取歌词内容 ====================

@router.get("/lyric/{music_id}")
async def get_music_lyric(music_id: int, db: AsyncSession = Depends(get_database)):
    """
    根据音乐 ID 获取歌词文本。
    lyric 字段存放的是歌词文件路径（如 /static/lyric/晴天.txt），
    这个接口会读取文件内容并返回纯文本。
    """
    import os

    # 1. 查询音乐记录
    result = await db.execute(select(Music).where(Music.id == music_id))
    music = result.scalar_one_or_none()
    if music is None:
        raise HTTPException(status_code=404, detail="音乐未找到")

    # 2. 检查音乐是否已下架
    if music.status != 1:
        raise HTTPException(status_code=403, detail="该音乐已下架")

    # 3. 如果没有歌词路径，返回空
    if not music.lyric:
        return {"lyric": ""}

    # 4. 拼接歌词文件的完整路径（项目根目录/static/lyric/xxx.txt）
    #    music.lyric 存的是 /static/lyric/xxx.txt 这样的相对路径
    #    去掉开头的 / 后，拼到项目根目录下
    lyric_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), music.lyric.lstrip("/"))

    # 5. 读取文件内容
    try:
        with open(lyric_path, "r", encoding="utf-8") as f:
            lyric_text = f.read()
    except FileNotFoundError:
        # 文件不存在，返回空
        lyric_text = ""
    except Exception:
        lyric_text = ""

    return {"lyric": lyric_text}


# ==================== 热门音乐（播放量排行） ====================
# GET /music/hot
# 返回播放量最高的前 6 首已上架音乐，用于首页推荐
@router.get("/hot")
async def get_hot_music(
    limit: int = 6,
    db: AsyncSession = Depends(get_database)
):
    # 1. 按播放次数倒序查询
    result = await db.execute(
        select(Music)
        .where(Music.status == 1)
        .order_by(Music.play_count.desc())
        .limit(limit)
    )
    items = result.scalars().all()

    # 2. 返回列表
    return [
        {
            "id": m.id,
            "title": m.title,
            "singer_id": m.singer_id,
            "cover": m.cover,
            "file_url": m.file_url,
            "play_count": m.play_count
        }
        for m in items
    ]


# ==================== 排行榜（热歌榜 + 新歌榜） ====================
# GET /music/ranking
# 返回两个榜单：热歌榜（按播放量排序，前50）和新歌榜（按上架时间排序，前20）
@router.get("/ranking")
async def get_ranking(
    db: AsyncSession = Depends(get_database)
):
    # 1. 热歌榜：按播放次数倒序，取前 50
    hot_result = await db.execute(
        select(Music)
        .where(Music.status == 1)
        .order_by(Music.play_count.desc())
        .limit(50)
    )
    hot_list = [
        {
            "id": m.id,
            "title": m.title,
            "singer_id": m.singer_id,
            "cover": m.cover,
            "file_url": m.file_url,
            "play_count": m.play_count
        }
        for m in hot_result.scalars().all()
    ]

    # 2. 新歌榜：按创建时间倒序，取前 20
    new_result = await db.execute(
        select(Music)
        .where(Music.status == 1)
        .order_by(Music.create_time.desc())
        .limit(20)
    )
    new_list = [
        {
            "id": m.id,
            "title": m.title,
            "singer_id": m.singer_id,
            "cover": m.cover,
            "file_url": m.file_url,
            "play_count": m.play_count,
            "create_time": str(m.create_time)
        }
        for m in new_result.scalars().all()
    ]

    return {"hot_list": hot_list, "new_list": new_list}


# ==================== 最近播放（当前用户的播放记录） ====================
# GET /music/recent
# 返回当前登录用户最近听过的 50 首歌（去重，同一首歌只保留最近一次）
@router.get("/recent")
async def get_recent_plays(
    limit: int = 50,
    db: AsyncSession = Depends(get_database),
    current_user: User = Depends(get_current_user)
):
    # 查询当前用户的播放记录，按时间倒序
    result = await db.execute(
        select(PlayHistory)
        .where(PlayHistory.user_id == current_user.id)
        .order_by(PlayHistory.played_at.desc())
        .limit(limit * 2)  # 多取一些，后面去重用
    )
    records = result.scalars().all()

    # 去重：同一首歌只保留最近一次出现
    seen_ids = set()
    unique_records = []
    for r in records:
        if r.music_id not in seen_ids:
            seen_ids.add(r.music_id)
            unique_records.append(r)
            if len(unique_records) >= limit:
                break

    # 批量查询歌曲详情
    music_ids = [r.music_id for r in unique_records]
    if not music_ids:
        return []

    music_result = await db.execute(
        select(Music).where(Music.id.in_(music_ids))
    )
    music_map = {m.id: m for m in music_result.scalars().all()}

    # 按播放记录的顺序返回（保持时间倒序）
    items = []
    for r in unique_records:
        m = music_map.get(r.music_id)
        if m and m.status == 1:  # 只返回已上架的歌曲
            items.append({
                "id": m.id,
                "title": m.title,
                "singer_id": m.singer_id,
                "album_id": m.album_id,
                "cover": m.cover,
                "file_url": m.file_url,
                "play_count": m.play_count,
                "played_at": str(r.played_at),
            })

    return items


# ==================== 播放次数 +1 ====================
# POST /music/{music_id}/play
# 每次播放一首歌时调用，play_count 自动加 1
# 如果用户已登录，同时记录播放历史
@router.post("/{music_id}/play")
async def increment_play_count(
    music_id: int,
    db: AsyncSession = Depends(get_database),
    current_user = Depends(get_optional_user)
):
    # 1. 查询音乐
    result = await db.execute(select(Music).where(Music.id == music_id))
    music = result.scalar_one_or_none()
    if music is None:
        raise HTTPException(status_code=404, detail="音乐未找到")

    # 2. 播放次数 +1
    music.play_count += 1

    # 3. 如果用户已登录，记录播放历史
    if current_user:
        play_record = PlayHistory(user_id=current_user.id, music_id=music_id)
        db.add(play_record)

    await db.flush()

    # 4. 清除音乐列表的 Redis 缓存（因为 play_count 变了，旧缓存数据不准确）
    #    用 keys 匹配所有 music:list: 开头的缓存 key，批量删除
    cache_keys = redis_client.keys("music:list:*")
    if cache_keys:
        redis_client.delete(*cache_keys)

    return {"play_count": music.play_count}
