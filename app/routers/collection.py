from fastapi import APIRouter, Depends
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.routers.user import get_current_user
from app.models.collection import Collection
from app.models.music import Music
from app.schemas.collection import CollectionToggle, CollectionStatus, CollectionMusicItem, CollectionListResponse

router = APIRouter(prefix="/collection", tags=["收藏"])


# ==================== 获取我的收藏列表 ====================

@router.get("/list", response_model=CollectionListResponse)
async def get_collection_list(
    page: int = 1,           # 页码，默认第 1 页
    page_size: int = 10,     # 每页数量，默认 10 条
    current_user: dict = Depends(get_current_user),  # 需要登录
    db: AsyncSession = Depends(get_db)
):
    # 1. 先查当前用户的收藏总数
    total_result = await db.execute(
        select(Collection).where(Collection.user_id == current_user.id)
    )
    total = len(total_result.scalars().all())

    # 2. 分页查询当前用户的收藏记录（按收藏时间倒序，最新收藏的排前面）
    offset = (page - 1) * page_size
    coll_result = await db.execute(
        select(Collection)
        .where(Collection.user_id == current_user.id)
        .order_by(Collection.create_time.desc())
        .offset(offset)
        .limit(page_size)
    )
    collections = coll_result.scalars().all()

    # 3. 如果没有收藏，直接返回空列表
    if not collections:
        return {"items": [], "total": total, "page": page, "page_size": page_size}

    # 4. 取出所有音乐 ID，批量查询音乐详情
    music_ids = [c.music_id for c in collections]
    music_result = await db.execute(
        select(Music).where(Music.id.in_(music_ids))
    )
    # 构建 music_id -> music 对象的映射，方便后面快速查找
    music_map = {m.id: m for m in music_result.scalars().all()}

    # 5. 组装返回数据（保持收藏记录的顺序，附上音乐详情和收藏时间）
    items = []
    for coll in collections:
        music = music_map.get(coll.music_id)
        if music:  # 跳过已被删除的音乐
            items.append({
                "id": music.id,
                "title": music.title,
                "singer_id": music.singer_id,
                "album_id": music.album_id,
                "category_id": music.category_id,
                "file_url": music.file_url,
                "cover": music.cover,
                "duration": music.duration,
                "play_count": music.play_count,
                "status": music.status,
                "collected_at": coll.create_time
            })

    return {"items": items, "total": total, "page": page, "page_size": page_size}


# ==================== 收藏 / 取消收藏 ====================

@router.post("/toggle", response_model=CollectionStatus)
async def toggle_collection(
        data: CollectionToggle,  # 接收 music_id
        current_user: dict = Depends(get_current_user),  # 获取当前用户
        db: AsyncSession = Depends(get_db)  # 数据库会话
):
    # 1. 查询是否已收藏
    existing = await db.execute(
        select(Collection).where(
            Collection.user_id == current_user.id,
            Collection.music_id == data.music_id
        )
    )
    collection = existing.scalar_one_or_none()

    # 2. 判断并操作
    if collection:
        # 已收藏 → 取消收藏
        await db.delete(collection)
        await db.commit()
        return {"is_collected": False}
    else:
        # 未收藏 → 添加收藏
        new_collection = Collection(
            user_id=current_user.id,
            music_id=data.music_id
        )
        db.add(new_collection)
        await db.commit()
        return {"is_collected": True}


# ==================== 查询某首歌的收藏状态 ====================

@router.get("/status/{music_id}", response_model=CollectionStatus)
async def get_collection_status(
        music_id: int,  # 要查询的歌曲 ID
        current_user: dict = Depends(get_current_user),  # 需要登录
        db: AsyncSession = Depends(get_db)
):
    """
    查询当前用户是否收藏了某首歌。
    返回 { is_collected: true/false }
    """
    # 查询收藏记录
    result = await db.execute(
        select(Collection).where(
            Collection.user_id == current_user.id,
            Collection.music_id == music_id
        )
    )
    collection = result.scalar_one_or_none()

    # 有记录 = 已收藏，没有 = 未收藏
    return {"is_collected": collection is not None}