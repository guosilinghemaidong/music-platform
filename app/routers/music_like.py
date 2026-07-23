from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db                                  # 数据库会话依赖
from app.routers.user import get_current_user                    # 获取当前登录用户
from app.models.music_like import MusicLike                      # 点赞模型
from app.schemas.music_like import LikeToggle, LikeStatus        # 点赞 Schema


# 创建路由器，前缀 /like，标签"点赞"
router = APIRouter(prefix="/like", tags=["点赞"])


# 切换点赞状态（点赞 / 取消点赞）
# POST /like/toggle，Body 传 { "music_id": 1 }
# 需要登录才能调用（Depends(get_current_user)）
@router.post("/toggle", response_model=LikeStatus)
async def toggle_like(
    data: LikeToggle,                                        # 接收 music_id
    current_user: dict = Depends(get_current_user),          # 获取当前登录用户
    db: AsyncSession = Depends(get_db)                       # 数据库会话
):
    # 1. 查询当前用户是否已点赞这首音乐
    #    条件：user_id = 当前用户ID 且 music_id = 传入的音乐ID
    existing = await db.execute(
        select(MusicLike).where(
            MusicLike.user_id == current_user.id,
            MusicLike.music_id == data.music_id
        )
    )
    like = existing.scalar_one_or_none()

    # 2. 判断并操作
    if like:
        # 已点赞 → 取消点赞（删除记录）
        await db.delete(like)
        await db.commit()
        return {"is_liked": False}
    else:
        # 未点赞 → 添加点赞（新增记录）
        new_like = MusicLike(
            user_id=current_user.id,
            music_id=data.music_id
        )
        db.add(new_like)
        await db.commit()
        return {"is_liked": True}
