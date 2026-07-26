from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db                                  # 数据库会话依赖
from app.routers.user import get_current_user                    # 获取当前登录用户
from app.models.follow import Follow                             # 关注模型
from app.models.user import User                                 # 用户模型（查询用户信息）
from app.schemas.follow import (
    FollowToggle, FollowStatus,                                  # 原有 Schema
    FollowUserItem, FollowListResponse                           # 新增：列表 Schema
)


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


# ==================== 我的关注列表 ====================
# GET /follow/following
# 返回当前用户关注的所有人，并标注对方是否也关注了我（互相关注）
@router.get("/following", response_model=FollowListResponse)
async def get_following_list(
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    # 1. 查询当前用户关注了哪些人
    result = await db.execute(
        select(Follow).where(Follow.follower_id == current_user.id)
    )
    follows = result.scalars().all()
    following_ids = [f.following_id for f in follows]

    # 2. 查询这些用户的详细信息
    items = []
    following_count = len(following_ids)
    if following_ids:
        user_result = await db.execute(select(User).where(User.id.in_(following_ids)))
        users = user_result.scalars().all()
        user_map = {u.id: u for u in users}

        # 3. 查询这些人中哪些也关注了我（用于显示"互相关注"）
        back_result = await db.execute(
            select(Follow.following_id).where(
                Follow.follower_id.in_(following_ids),
                Follow.following_id == current_user.id
            )
        )
        follows_back = set(back_result.scalars().all())

        # 4. 按原始关注顺序组装结果
        for fid in following_ids:
            u = user_map.get(fid)
            if u:
                items.append(FollowUserItem(
                    id=u.id,
                    username=u.username,
                    nickname=u.nickname,
                    avatar=u.avatar,
                    is_followed_back=(u.id in follows_back)
                ))

    # 5. 顺便查一下粉丝总数（用于页面显示）
    followers_result = await db.execute(
        select(Follow).where(Follow.following_id == current_user.id)
    )
    followers_count = len(followers_result.scalars().all())

    return FollowListResponse(
        items=items,
        followers_count=followers_count,
        following_count=following_count
    )


# ==================== 我的粉丝列表 ====================
# GET /follow/followers
# 返回所有关注我的用户，并标注我是否也关注了对方
@router.get("/followers", response_model=FollowListResponse)
async def get_followers_list(
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    # 1. 查询谁关注了我
    result = await db.execute(
        select(Follow).where(Follow.following_id == current_user.id)
    )
    follows = result.scalars().all()
    follower_ids = [f.follower_id for f in follows]

    # 2. 查询这些粉丝的详细信息
    items = []
    followers_count = len(follower_ids)
    if follower_ids:
        user_result = await db.execute(select(User).where(User.id.in_(follower_ids)))
        users = user_result.scalars().all()
        user_map = {u.id: u for u in users}

        # 3. 查询我关注了这些人中的哪些（用于显示"已关注"/"回关"按钮）
        my_following_result = await db.execute(
            select(Follow.following_id).where(
                Follow.follower_id == current_user.id,
                Follow.following_id.in_(follower_ids)
            )
        )
        my_following = set(my_following_result.scalars().all())

        # 4. 组装结果
        for fid in follower_ids:
            u = user_map.get(fid)
            if u:
                items.append(FollowUserItem(
                    id=u.id,
                    username=u.username,
                    nickname=u.nickname,
                    avatar=u.avatar,
                    is_followed_back=(u.id in my_following)
                ))

    # 5. 顺便查一下关注总数
    following_result = await db.execute(
        select(Follow).where(Follow.follower_id == current_user.id)
    )
    following_count = len(following_result.scalars().all())

    return FollowListResponse(
        items=items,
        followers_count=followers_count,
        following_count=following_count
    )
