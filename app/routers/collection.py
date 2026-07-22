from fastapi import APIRouter, Depends
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.routers.user import get_current_user
from app.models.collection import Collection
from app.schemas.collection import CollectionToggle, CollectionStatus

router = APIRouter(prefix="/collection", tags=["收藏"])


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


