from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db                                  # 数据库会话依赖
from app.routers.user import get_current_user                    # 获取当前登录用户
from app.models.follow import Follow                             # 关注模型
from app.schemas.follow import FollowToggle, FollowStatus        # 关注 Schema


# 创建路由器，前缀 /follow，标签"关注"
router = APIRouter(prefix="/follow", tags=["关注"])


# 切换关注状态（关注 / 取消关注）
# POST /follow/toggle，Body 传 { "following_id": 2 }
# 需要登录才能调用（Depends(get_current_user)）
@router.post("/toggle", response_model=FollowStatus)
async def toggle_follow(
    data: FollowToggle,                                      # 接收 following_id（要关注的用户ID）
    current_user: dict = Depends(get_current_user),          # 获取当前登录用户
    db: AsyncSession = Depends(get_db)                       # 数据库会话
):
    # 1. 不能关注自己
    if current_user.id == data.following_id:
        raise HTTPException(status_code=400, detail="不能关注自己")

    # 2. 查询当前用户是否已关注目标用户
    #    follower_id = 当前用户ID（谁在关注）
    #    following_id = 传入的用户ID（关注谁）
    existing = await db.execute(
        select(Follow).where(
            Follow.follower_id == current_user.id,
            Follow.following_id == data.following_id
        )
    )
    follow = existing.scalar_one_or_none()

    # 3. 判断并操作
    if follow:
        # 已关注 → 取消关注（删除记录）
        await db.delete(follow)
        await db.commit()
        return {"is_followed": False}
    else:
        # 未关注 → 添加关注（新增记录）
        new_follow = Follow(
            follower_id=current_user.id,
            following_id=data.following_id
        )
        db.add(new_follow)
        await db.commit()
        return {"is_followed": True}
